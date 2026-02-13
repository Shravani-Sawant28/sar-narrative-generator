import streamlit as st
import pandas as pd
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from src.data_manager import DataManager
from src.generator import SARGenerator
from src.audit import AuditLogger

# Initialize Services
data_manager = DataManager()
generator = SARGenerator()
audit_logger = AuditLogger()

# Page Configuration
st.set_page_config(
    page_title="SAR Admin Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
    <style>
    .metric-card {
        background-color: #292B3D;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        text-align: center;
        border: 1px solid #333333;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-label {
        color: #979AA3;
        font-size: 0.95em;
        font-weight: 500;
        margin-top: 4px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.8em;
        font-weight: 600;
        background-color: #FFFFFF;
        color: #161B2F;
        border: none;
    }
    .stButton>button:hover {
        background-color: #f0f0f0;
        color: #161B2F;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State
if 'current_customer' not in st.session_state:
    st.session_state['current_customer'] = None
if 'generated_narrative' not in st.session_state:
    st.session_state['generated_narrative'] = ""
if 'audit_trace' not in st.session_state:
    st.session_state['audit_trace'] = []

# --- Pages ---

def admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.markdown("Overview of AML Monitoring Activities")
    
    stats = data_manager.get_customer_stats()
    all_txns = data_manager.get_all_transactions()
    
    # Key Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_customers']}</div>
            <div class="metric-label">Total Customers</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #e53e3e;">{stats['high_risk_count']}</div>
            <div class="metric-label">High Risk Subjects</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(all_txns)}</div>
            <div class="metric-label">Total Transactions</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        total_vol = all_txns['amount'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{total_vol/10000000:.1f} Cr</div>
            <div class="metric-label">Transaction Volume</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Advanced Charts
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.subheader("Transaction Analysis")
        all_txns['date'] = pd.to_datetime(all_txns['date'])
        
        # Scatter Plot of Transactions
        fig_scatter = px.scatter(
            all_txns, 
            x='date', 
            y='amount', 
            color='type',
            size='amount',
            hover_data=['description', 'customer_id'],
            title="Transaction Volume & Frequency",
            color_discrete_map={'Credit': '#3696FC', 'Debit': '#CBCCD1'}
        )
        fig_scatter.update_layout(height=400, xaxis_title="Date", yaxis_title="Amount (INR)")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_chart2:
        st.subheader("Risk Distribution")
        risk_df = pd.DataFrame(list(stats['risk_distribution'].items()), columns=['Risk Level', 'Count'])
        
        fig_donut = px.pie(
            risk_df, 
            values='Count', 
            names='Risk Level', 
            hole=0.5,
            color='Risk Level',
            color_discrete_map={'High': '#e53e3e', 'Medium': '#ed8936', 'Low': '#48bb78'}
        )
        fig_donut.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_donut, use_container_width=True)

    # Recent Flagged Transactions (Mock)
    st.subheader("🚨 Recent Flagged Transactions")
    flagged_txns = all_txns[all_txns['amount'] > 50000].sort_values('date', ascending=False).head(5)
    st.dataframe(
        flagged_txns[['transaction_id', 'customer_id', 'date', 'amount', 'type', 'description']],
        hide_index=True,
        use_container_width=True
    )

def user_management_page():
    st.title("👥 User Management")
    
    # State Management for Navigation
    if 'selected_customer_id' not in st.session_state:
        st.session_state['selected_customer_id'] = None

    # Detail View
    if st.session_state['selected_customer_id']:
        if st.button("← Back to List"):
            st.session_state['selected_customer_id'] = None
            st.rerun()
        show_customer_details(st.session_state['selected_customer_id'])
    
    # List View
    else:
        # Sidebar Filter
        st.sidebar.markdown("### Filters")
        risk_filter = st.sidebar.multiselect(
            "Risk Rating", 
            ["High", "Medium", "Low"], 
            default=["High", "Medium", "Low"]
        )
        
        customers = data_manager.customers
        filtered_customers = customers[customers['risk_rating'].isin(risk_filter)]
        
        st.markdown("### Customer Registry")
        
        # Display as a grid of cards or a clean list
        for idx, row in filtered_customers.iterrows():
            with st.container():
                # Card-like container
                st.markdown(f"""
                <div style="background-color: #292B3D; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333333;">
                    <div style="display: flex; justify-content: space-between; align_items: center;">
                        <div>
                            <h3 style="margin: 0; color: #FFFFFF;">{row['name']}</h3>
                            <p style="margin: 0; color: #979AA3; font-size: 0.9em;">ID: {row['customer_id']} | Occupation: {row['occupation']}</p>
                        </div>
                        <div style="text-align: right;">
                             <span style="background-color: {'#e53e3e' if row['risk_rating'] == 'High' else '#ed8936' if row['risk_rating'] == 'Medium' else '#48bb78'}; 
                                          padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8em;">
                                {row['risk_rating']} Risk
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Button
                if st.button(f"View Profile ➜", key=f"btn_{row['customer_id']}"):
                    st.session_state['selected_customer_id'] = row['customer_id']
                    st.rerun()

def show_customer_details(customer_id):
    customer = data_manager.get_customer(customer_id)
    transactions = data_manager.get_transactions(customer_id)
    
    st.markdown(f"## {customer['name']}")
    
    # Validating risk rating color
    risk_color = "red" if customer['risk_rating'] == 'High' else "orange" if customer['risk_rating'] == 'Medium' else "green"
    st.markdown(f"**Risk Rating:** :{risk_color}[{customer['risk_rating']}] | **ID:** `{customer['customer_id']}`")
    
    d1, d2, d3 = st.columns(3)
    d1.info(f"**Occupation**\n\n{customer['occupation']}")
    d2.info(f"**Tenure**\n\n{customer['tenure_years']} Years")
    d3.info(f"**KYC Status**\n\n{customer['kyc_status']}")
    
    # Visual Transaction History
    st.markdown("### 📊 Activity Timeline")
    transactions['date'] = pd.to_datetime(transactions['date'])
    fig_timeline = px.bar(
        transactions, 
        x='date', 
        y='amount', 
        color='type',
        color_discrete_map={'Credit': '#3696FC', 'Debit': '#CBCCD1'},
        title="Transaction Flow"
    )
    fig_timeline.update_layout(height=300, xaxis_title=None)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("### 📜 Transaction Details")
    st.dataframe(transactions[['date', 'transaction_id', 'type', 'amount', 'counterparty', 'description']], hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("⚠️ Regulatory Reporting")
    
    if st.button("Generate Suspicious Transaction Report (STR) 🚀", key="gen_sar_btn", type="primary"):
        with st.spinner("Analyzing patterns and compiling STR..."):
            time.sleep(1.5)
            result = generator.generate(customer, transactions)
            st.session_state['generated_narrative'] = result['narrative_text']
            st.session_state['audit_trace'] = result['audit_trace']
            st.session_state['current_customer'] = customer
            
            audit_logger.log_event("Generation", "Admin_User", {
                "customer_id": customer['customer_id'], 
                "status": "Generated"
            })
            st.rerun()

    if st.session_state.get('current_customer') and st.session_state['current_customer']['customer_id'] == customer_id:
        if st.session_state['generated_narrative']:
            display_sar_editor()

def display_sar_editor():
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### STR Draft Preview (FIU-IND Format)")
        narrative_input = st.text_area(
            "Review and Edit Report:",
            value=st.session_state['generated_narrative'],
            height=600
        )
        
    with c2:
        st.markdown("### 🔍 Audit Trace")
        with st.container(border=True):
            for trace in st.session_state['audit_trace']:
                st.markdown(f"**{trace['step']}**")
                st.caption(f"{trace['reasoning']}")
                st.divider()
                
        st.markdown("### Actions")
        if st.button("Save Draft"):
            st.session_state['generated_narrative'] = narrative_input
            audit_logger.log_event("Edit", "Admin_User", {"customer_id": st.session_state['current_customer']['customer_id']})
            st.success("Draft Saved")
            
        if st.button("Approve & File ✅", type="primary"):
            audit_logger.log_event("Approval", "Admin_User", {"customer_id": st.session_state['current_customer']['customer_id']})
            st.balloons()
            st.success("STR Filed Successfully!")

def audit_page():
    st.title("🛡️ Audit Logs")
    logs = audit_logger.get_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
        st.download_button("Download JSON", data=json.dumps(logs, indent=4), file_name="audit_log.json")
    else:
        st.info("No logs found.")

# --- Navigation ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/9322/9322127.png", width=50) # Placeholder logo
st.sidebar.title("SAR Gen AI")
st.sidebar.caption("Advanced AML Monitoring System")

page = st.sidebar.radio("Navigation", ["Admin Dashboard", "User Management", "Audit Logs"])

if page == "Admin Dashboard":
    admin_dashboard()
elif page == "User Management":
    user_management_page()
elif page == "Audit Logs":
    audit_page()
