import streamlit as st
import os
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
# Page Configuration
if os.path.exists("pageheader.png"):
    page_icon = "pageheader.png"
elif os.path.exists("pageicon.png"):
    page_icon = "pageicon.png"
elif os.path.exists("logo.jpg"):
    page_icon = "logo.jpg"
else:
    page_icon = ""

st.set_page_config(
    page_title="SAR Admin Dashboard",
    page_icon=page_icon,
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
    /* Primary Button (Generate SAR) - Red */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #e53e3e !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #c53030 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:active {
        background-color: #9b2c2c !important;
        color: #FFFFFF !important;
    }
    
    /* All Buttons - Increased Font Size */
    div[data-testid="stButton"] button {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }
    
    /* SAR Action Buttons - Extra Large Font */
    div[data-testid="stButton"] button:has-text("Save Draft as PDF"),
    div[data-testid="stButton"] button:has-text("File with FinCEN"),
    div[data-testid="stButton"] button:has-text("Escalate to Regulatory SAR"),
    div[data-testid="stButton"] button:has-text("Dismiss Internal SAR") {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Text Area (Report Content) - White Background, Black Text */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }
    .stTextArea label {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Authentication Credentials ---
USER_CREDENTIALS = {
    "Analyst": {"username": "analyst", "password": "analyst123"},
    "Supervisor": {"username": "supervisor", "password": "super123"},
    "Compliance Officer": {"username": "compliance", "password": "compliance123"},
}

# Session State
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_customer' not in st.session_state:
    st.session_state['current_customer'] = None
if 'generated_narrative' not in st.session_state:
    st.session_state['generated_narrative'] = ""
if 'audit_trace' not in st.session_state:
    st.session_state['audit_trace'] = []
if 'sar_type' not in st.session_state:
    st.session_state['sar_type'] = "Internal"  # "Internal" or "Normal"
if 'sar_status' not in st.session_state:
    st.session_state['sar_status'] = "Draft"  # "Draft", "Under Review", "Escalated", "Filed", "Dismissed"
if 'sar_report_stage' not in st.session_state:
    st.session_state['sar_report_stage'] = 1  # 1 = Initial Report, 2 = Final Report with Edits
if 'sar_edit_comments' not in st.session_state:
    st.session_state['sar_edit_comments'] = ""


def login_page():
    """Render a minimal, professional login page."""
    st.markdown("""
    <style>
    .login-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .login-subtitle {
        text-align: center;
        font-size: 0.9rem;
        color: #979AA3;
        margin-bottom: 24px;
    }
    /* hide sidebar on login page */
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)

    # Centred card
    col_left, col_mid, col_right = st.columns([1.2, 1.6, 1.2])
    with col_mid:
        # Logo (centered, larger)
        if os.path.exists("logo.jpg"):
            import base64 as b64
            with open("logo.jpg", "rb") as img_f:
                logo_data = b64.b64encode(img_f.read()).decode()
            st.markdown(
                f'<div style="display:flex;justify-content:center;margin-bottom:10px;">'
                f'<img src="data:image/jpeg;base64,{logo_data}" width="200" />'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif os.path.exists("logo.png"):
            import base64 as b64
            with open("logo.png", "rb") as img_f:
                logo_data = b64.b64encode(img_f.read()).decode()
            st.markdown(
                f'<div style="display:flex;justify-content:center;margin-bottom:10px;">'
                f'<img src="data:image/png;base64,{logo_data}" width="200" />'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div class='login-title'>SAR Narrative Generator</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-subtitle'>Advanced AML Monitoring System</div>", unsafe_allow_html=True)

        # Form
        role = st.selectbox("Access Level", list(USER_CREDENTIALS.keys()))
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Sign In", type="primary", use_container_width=True):
            expected = USER_CREDENTIALS[role]
            if username == expected["username"] and password == expected["password"]:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = role
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

        # Credentials reference
        st.markdown("---")
        with st.expander("View Login Credentials"):
            for r, creds in USER_CREDENTIALS.items():
                st.markdown(f"**{r}** — `{creds['username']}` / `{creds['password']}`")


# Handle shared report URL parameters
query_params = st.query_params
if 'share_id' in query_params:
    share_id = query_params['share_id']
    shared_reports_dir = "data/shared_reports"
    share_file_path = os.path.join(shared_reports_dir, f"{share_id}.json")
    
    if os.path.exists(share_file_path):
        try:
            with open(share_file_path, 'r') as f:
                shared_data = json.load(f)
            
            # Load the shared report into session state
            st.session_state['current_customer'] = shared_data.get('customer')
            st.session_state['generated_narrative'] = shared_data.get('narrative', '')
            st.session_state['audit_trace'] = shared_data.get('audit_trace', [])
            st.session_state['sar_type'] = shared_data.get('sar_type', 'Internal')
            st.session_state['sar_status'] = shared_data.get('sar_status', 'Draft')
            st.session_state['sar_report_stage'] = shared_data.get('report_stage', 1)
            st.session_state['sar_edit_comments'] = shared_data.get('edit_comments', '')
            st.session_state['nav_selection'] = "AI Assistant"  # Navigate to report view
            
            # Clear the query params after loading
            st.query_params.clear()
        except Exception as e:
            st.error(f"Error loading shared report: {str(e)}")





# --- Pages ---

def admin_dashboard():
    # Header Image
    # if os.path.exists("pageheader.png"):
    #     st.image("pageheader.png", use_container_width=True)
        
    st.title("Admin Dashboard")
    st.markdown("Overview of AML Monitoring Activities")
    


    
    stats = data_manager.get_customer_stats()
    all_txns = data_manager.get_all_transactions()
    
    # Key Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_alerts']}</div>
            <div class="metric-label">Total Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #e53e3e;">{stats['rejected_alerts']}</div>
            <div class="metric-label">Rejected Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #e53e3e;">{stats['suspicious_alerts']}</div>
            <div class="metric-label">Suspicious Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #48bb78;">{stats['approved_files']}</div>
            <div class="metric-label">Total Files Approved</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Advanced Charts
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.subheader("SAR Analytics Dashboard")
        
        # Timeline selector
        timeline_option = st.selectbox(
            "View by:",
            ["Day-wise", "Month-wise", "Year-wise"],
            key="admin_sar_timeline"
        )
        
        # Get SAR analytics data
        sar_data = data_manager.get_sar_analytics(timeline_option)
        
        # Determine date format
        if timeline_option == "Day-wise":
            date_format = "%d %b"
        elif timeline_option == "Month-wise":
            date_format = "%b %Y"
        else:  # Year-wise
            date_format = "%Y"
        
        # Create grouped bar chart with data labels (matching reference image style)
        fig_sar = go.Figure()
        
        # Add SAR Processed bars (dark blue)
        fig_sar.add_trace(go.Bar(
            x=sar_data['date'],
            y=sar_data['sar_processed'],
            name='SARs Processed',
            marker_color='#ffffff',
            marker_line_color='#002d4a',
            marker_line_width=1,
            text=sar_data['sar_processed'],
            textposition='outside',
            textfont=dict(size=10, color='#00aeef', family='Arial Black'),
            hovertemplate='<b>SARs Processed</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        # Add SAR Disseminated bars (light blue)
        fig_sar.add_trace(go.Bar(
            x=sar_data['date'],
            y=sar_data['sar_disseminated'],
            name='SARs Disseminated',
            marker_color='#00aeef',
            marker_line_color='#0088cc',
            marker_line_width=1,
            text=sar_data['sar_disseminated'],
            textposition='outside',
            textfont=dict(size=10, color='#00aeef', family='Arial Black'),
            hovertemplate='<b>SARs Disseminated</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        # Update layout to match reference image style
        fig_sar.update_layout(
            title={
                'text': f"Chart: {timeline_option.replace('-wise', '')} SARs Processed and Disseminated",
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.98,
                'yanchor': 'top',
                'font': {'size': 14, 'family': 'Georgia, serif', 'color': '#FFFFFF'}
            },
            height=500,
            xaxis_title="FINANCIAL YEAR" if timeline_option == "Year-wise" else "TIME PERIOD",
            yaxis_title="NO.OF SARS",
            xaxis=dict(
                tickformat=date_format,
                tickangle=-45,
                tickfont=dict(size=10, color='#FFFFFF'),
                title_font=dict(size=11, color='#FFFFFF'),
                title_standoff=25
            ),
            yaxis=dict(
                tickfont=dict(size=10, color='#FFFFFF'),
                gridcolor='rgba(255,255,255,0.1)',
                title_font=dict(size=11, color='#FFFFFF')
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0.3)",
                bordercolor="#00aeef",
                borderwidth=1,
                font=dict(color='#FFFFFF', size=10)
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, b=120, l=60, r=40),
            font=dict(color='#FFFFFF')
        )
        
        st.plotly_chart(fig_sar, use_container_width=True)



        
    with col_chart2:
        st.subheader("Risk Distribution")
        risk_df = pd.DataFrame(list(stats['risk_distribution'].items()), columns=['Risk Level', 'Count'])
        
        fig_donut = px.pie(
            risk_df, 
            values='Count', 
            names='Risk Level', 
            hole=0.5,
            color='Risk Level',
            color_discrete_map={'HIGH': '#e53e3e', 'MEDIUM': '#fbbf24', 'LOW': '#48bb78'}
        )
        fig_donut.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_donut, use_container_width=True)

    # Recent Flagged Transactions - Using Real Alert Data
    st.subheader("Recent Flagged Transactions")
    
    # Get alerts and join with transactions
    if data_manager.alerts is not None and not data_manager.alerts.empty:
        # Get most recent high-severity alerts
        recent_alerts = data_manager.alerts[
            data_manager.alerts['severity'].isin(['HIGH', 'CRITICAL'])
        ].sort_values('alert_date', ascending=False).head(25)
        
        if not recent_alerts.empty:
            # Get customer IDs from recent alerts
            alert_customer_ids = recent_alerts['customer_id'].unique()
            
            # Get transactions for these customers
            flagged_txns = all_txns[all_txns['customer_id'].isin(alert_customer_ids)].copy()
            
            # Merge with alert information to show alert type and severity
            flagged_txns = flagged_txns.merge(
                recent_alerts[['customer_id', 'alert_type', 'severity', 'rule_triggered']].drop_duplicates('customer_id'),
                on='customer_id',
                how='left'
            )
            
            # Sort by date and get top 25
            flagged_txns = flagged_txns.sort_values('date', ascending=False).head(25)
            
            # Display the flagged transactions
            st.dataframe(
                flagged_txns[['date', 'transaction_id', 'customer_id', 'amount', 'type', 'channel', 'alert_type', 'severity']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "date": "Date",
                    "transaction_id": "Transaction ID",
                    "customer_id": "Customer ID",
                    "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
                    "type": "Type",
                    "channel": "Channel",
                    "alert_type": "Alert Type",
                    "severity": "Severity"
                }
            )
        else:
            st.info("No high-severity alerts found.")
    else:
        # Fallback if no alerts data
        st.info("No alert data available. Please ensure ALERTS_TRAINING.csv is loaded.")


def user_management_page():
    st.title("User Management")
    
    # State Management for Navigation
    if 'selected_customer_id' not in st.session_state:
        st.session_state['selected_customer_id'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 0

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
            ["HIGH", "MEDIUM", "LOW"], 
            default=["HIGH", "MEDIUM", "LOW"]
        )
        
        # Search box
        search_term = st.sidebar.text_input("Search by Name or ID", "")
        
        customers = data_manager.customers
        filtered_customers = customers[customers['risk_rating'].isin(risk_filter)]
        
        # Apply search filter
        if search_term:
            filtered_customers = filtered_customers[
                filtered_customers['name'].str.contains(search_term, case=False, na=False) |
                filtered_customers['customer_id'].str.contains(search_term, case=False, na=False)
            ]
        
        # Pagination settings
        items_per_page = 20
        total_customers = len(filtered_customers)
        total_pages = (total_customers + items_per_page - 1) // items_per_page
        
        # Ensure current page is within bounds
        if st.session_state['current_page'] >= total_pages and total_pages > 0:
            st.session_state['current_page'] = total_pages - 1
        elif st.session_state['current_page'] < 0:
            st.session_state['current_page'] = 0
        
        st.markdown(f"### Customer Registry ({total_customers} customers)")
        
        if total_customers == 0:
            st.info("No customers match the selected filters.")
        else:
            # Calculate pagination indices
            start_idx = st.session_state['current_page'] * items_per_page
            end_idx = min(start_idx + items_per_page, total_customers)
            
            # Get current page customers
            page_customers = filtered_customers.iloc[start_idx:end_idx]
            
            # Display customers in a more efficient way
            for idx, row in page_customers.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"ID: {row['customer_id']} | {row['occupation']}")
                
                with col2:
                    risk_color = '#e53e3e' if row['risk_rating'] == 'HIGH' else '#ed8936' if row['risk_rating'] == 'MEDIUM' else '#48bb78'
                    st.markdown(f"<span style='background-color: {risk_color}; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8em;'>{row['risk_rating']} Risk</span>", unsafe_allow_html=True)
                
                with col3:
                    if st.button("View →", key=f"btn_{row['customer_id']}"):
                        # Log the customer profile view
                        audit_logger.log_event("Customer Profile Viewed", "Admin_User", {
                            "customer_id": row['customer_id'],
                            "customer_name": row['name'],
                            "risk_rating": row['risk_rating'],
                            "action": "View Profile"
                        })
                        st.session_state['selected_customer_id'] = row['customer_id']
                        st.rerun()

                
                st.markdown("---")
            
            # Pagination controls
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮First", disabled=(st.session_state['current_page'] == 0)):
                    st.session_state['current_page'] = 0
                    st.rerun()
            
            with col2:
                if st.button("Prev", disabled=(st.session_state['current_page'] == 0)):
                    st.session_state['current_page'] -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f"<div style='text-align: center; padding: 8px;'>Page {st.session_state['current_page'] + 1} of {total_pages}</div>", unsafe_allow_html=True)
            
            with col4:
                if st.button("Next ", disabled=(st.session_state['current_page'] >= total_pages - 1)):
                    st.session_state['current_page'] += 1
                    st.rerun()
            
            with col5:
                if st.button("Last ", disabled=(st.session_state['current_page'] >= total_pages - 1)):
                    st.session_state['current_page'] = total_pages - 1
                    st.rerun()


def show_customer_details(customer_id):
    customer = data_manager.get_customer(customer_id)
    transactions = data_manager.get_transactions(customer_id)
    alerts = data_manager.get_alerts(customer_id)
    
    # Helper function to display country code
    def display_country(country_code):
        """Convert country codes for better display (GB -> UK)"""
        if country_code == 'GB':
            return 'UK'
        return country_code
    
    # Custom CSS for Profile Cards
    st.markdown("""
        <style>
        .profile-header {
            background: linear-gradient(135deg, #292B3D 0%, #1a1d2e 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid #333333;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .profile-name {
            font-size: 2.2em;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 8px;
        }
        .profile-subtitle {
            color: #979AA3;
            font-size: 1.1em;
        }
        .info-card {
            background-color: #292B3D;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #333333;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            margin-bottom: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.3);
        }
        .info-card-title {
            font-size: 0.85em;
            color: #979AA3;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .info-card-value {
            font-size: 1.4em;
            font-weight: 600;
            color: #FFFFFF;
        }
        .section-header {
            background-color: #1a1d2e;
            padding: 16px 20px;
            border-radius: 10px;
            margin: 24px 0 16px 0;
            border-left: 4px solid #00aeef;
        }
        .section-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #FFFFFF;
            margin: 0;
        }
        .compliance-badge {
            display: inline-block;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95em;
            text-align: center;
            margin: 8px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .alert-card {
            background-color: #2d1f1f;
            border-left: 4px solid #e53e3e;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # === PROFILE HEADER ===
    risk_badge_color = '#e53e3e' if customer['risk_rating'] == 'HIGH' else '#ed8936' if customer['risk_rating'] == 'MEDIUM' else '#48bb78'
    
    st.markdown(f"""
        <div class="profile-header">
            <div class="profile-name">{customer['name']}</div>
            <div class="profile-subtitle">
                <span style="background-color: {risk_badge_color}; padding: 6px 12px; border-radius: 6px; color: white; font-weight: bold; margin-right: 12px;">
                    {customer['risk_rating']} RISK
                </span>
                Customer ID: <code style="background-color: #1a1d2e; padding: 4px 8px; border-radius: 4px; color: #00aeef;">{customer['customer_id']}</code>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # === PERSONAL & ACCOUNT INFORMATION ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">Personal & Account Information</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Full Name</div>
                <div class="info-card-value">{customer['name']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Customer ID</div>
                <div class="info-card-value" style="color: #00aeef;">{customer['customer_id']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Country</div>
                <div class="info-card-value">{display_country(customer['country'])}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Occupation</div>
                <div class="info-card-value">{customer['occupation']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Account Opened</div>
                <div class="info-card-value">{customer.get('account_opened', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Tenure</div>
                <div class="info-card-value">{customer['tenure_years']} Years</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Customer Segment</div>
                <div class="info-card-value">{customer.get('customer_segment', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        kyc_color = '#48bb78' if customer['kyc_status'] == 'Verified' else '#ed8936'
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">KYC Status</div>
                <div class="info-card-value" style="color: {kyc_color};">✓ {customer['kyc_status']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # === FINANCIAL INFORMATION ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">Financial Information</div>
        </div>
    """, unsafe_allow_html=True)
    
    fin_col1, fin_col2, fin_col3 = st.columns(3)
    
    with fin_col1:
        yearly_income = customer.get('yearly_income', 0)
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Yearly Income</div>
                <div class="info-card-value" style="color: #48bb78;">${yearly_income:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with fin_col2:
        credit_score = customer.get('credit_score', 0)
        credit_color = "#48bb78" if credit_score >= 700 else "#ed8936" if credit_score >= 600 else "#e53e3e"
        credit_icon = "🟢" if credit_score >= 700 else "🟡" if credit_score >= 600 else "🔴"
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Credit Score</div>
                <div class="info-card-value" style="color: {credit_color};">{credit_icon} {credit_score}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with fin_col3:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">Customer Segment</div>
                <div class="info-card-value">{customer.get('customer_segment', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # === RISK & COMPLIANCE FLAGS ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">⚠️ Risk & Compliance</div>
        </div>
    """, unsafe_allow_html=True)
    
    risk_col1, risk_col2, risk_col3, risk_col4, risk_col5 = st.columns(5)
    
    with risk_col1:
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <div class="info-card-title">Risk Rating</div>
                <div class="compliance-badge" style="background-color: {risk_badge_color}; color: white;">
                    {customer['risk_rating']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with risk_col2:
        pep_status = customer.get('is_pep', 0) == 1
        pep_color = "#e53e3e" if pep_status else "#48bb78"
        pep_text = "YES" if pep_status else "NO"
        pep_icon = "⚠️" if pep_status else "✓"
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <div class="info-card-title">PEP Status</div>
                <div class="compliance-badge" style="background-color: {pep_color}; color: white;">
                    {pep_icon} {pep_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with risk_col3:
        fatf_black = customer.get('is_fatf_black', 0) == 1
        fatf_black_color = "#e53e3e" if fatf_black else "#48bb78"
        fatf_black_text = "YES" if fatf_black else "NO"
        fatf_black_icon = "⚠️" if fatf_black else "✓"
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <div class="info-card-title">FATF Blacklist</div>
                <div class="compliance-badge" style="background-color: {fatf_black_color}; color: white;">
                    {fatf_black_icon} {fatf_black_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with risk_col4:
        fatf_grey = customer.get('is_fatf_grey', 0) == 1
        fatf_grey_color = "#ed8936" if fatf_grey else "#48bb78"
        fatf_grey_text = "YES" if fatf_grey else "NO"
        fatf_grey_icon = "⚠️" if fatf_grey else "✓"
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <div class="info-card-title">FATF Greylist</div>
                <div class="compliance-badge" style="background-color: {fatf_grey_color}; color: white;">
                    {fatf_grey_icon} {fatf_grey_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with risk_col5:
        fca_high_risk = customer.get('is_fca_high_risk', 0) == 1
        fca_color = "#e53e3e" if fca_high_risk else "#48bb78"
        fca_text = "YES" if fca_high_risk else "NO"
        fca_icon = "⚠️" if fca_high_risk else "✓"
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <div class="info-card-title">FCA High Risk</div>
                <div class="compliance-badge" style="background-color: {fca_color}; color: white;">
                    {fca_icon} {fca_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # === ALERT INFORMATION ===
    if alerts is not None and not alerts.empty:
        st.markdown("""
            <div class="section-header">
                <div class="section-title">Alert Information</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display alert summary metrics in cards
        alert_summary_col1, alert_summary_col2, alert_summary_col3 = st.columns(3)
        
        with alert_summary_col1:
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">Total Alerts</div>
                    <div class="info-card-value" style="color: #e53e3e;">{len(alerts)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with alert_summary_col2:
            critical_count = len(alerts[alerts['severity'] == 'CRITICAL']) if 'severity' in alerts.columns else 0
            high_count = len(alerts[alerts['severity'] == 'HIGH']) if 'severity' in alerts.columns else 0
            total_high_critical = critical_count + high_count
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">High/Critical Alerts</div>
                    <div class="info-card-value" style="color: #e53e3e;">{total_high_critical}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with alert_summary_col3:
            latest_alert = alerts['alert_date'].max() if 'alert_date' in alerts.columns else 'N/A'
            latest_alert_str = str(latest_alert)[:10] if latest_alert != 'N/A' else 'N/A'
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">Latest Alert</div>
                    <div class="info-card-value" style="color: #ed8936;">{latest_alert_str}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Display detailed alert table
        st.markdown("<br>", unsafe_allow_html=True)
        alert_display_cols = ['alert_date', 'alert_type', 'severity', 'rule_triggered']
        available_cols = [col for col in alert_display_cols if col in alerts.columns]
        
        if available_cols:
            st.dataframe(
                alerts[available_cols].sort_values('alert_date', ascending=False) if 'alert_date' in available_cols else alerts[available_cols],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "alert_date": "Alert Date",
                    "alert_type": "Alert Type",
                    "severity": "Severity",
                    "rule_triggered": "Rule Triggered"
                }
            )
        else:
            st.dataframe(alerts, hide_index=True, use_container_width=True)
    else:
        st.markdown("""
            <div class="section-header">
                <div class="section-title">🚨 Alert Information</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div class="info-card" style="text-align: center; padding: 30px;">
                <div style="font-size: 2em; margin-bottom: 10px;">✓</div>
                <div style="color: #48bb78; font-size: 1.2em; font-weight: 600;">No Alerts Found</div>
                <div style="color: #979AA3; margin-top: 8px;">This customer has no recorded alerts</div>
            </div>
        """, unsafe_allow_html=True)
    
    # === TRANSACTION ACTIVITY ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">Transaction Activity</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Timeline selector
    txn_timeline = st.selectbox(
        "View transactions by:",
        ["Day-wise", "Month-wise", "Year-wise"],
        key=f"txn_timeline_{customer_id}"
    )
    
    transactions['date'] = pd.to_datetime(transactions['date'])
    
    # Aggregate transactions based on timeline selection
    if txn_timeline == "Day-wise":
        agg_txns = transactions.groupby([pd.Grouper(key='date', freq='D'), 'type'])['amount'].sum().reset_index()
        date_format = "%d %b"
    elif txn_timeline == "Month-wise":
        agg_txns = transactions.groupby([pd.Grouper(key='date', freq='M'), 'type'])['amount'].sum().reset_index()
        date_format = "%b %Y"
    else:  # Year-wise
        agg_txns = transactions.groupby([pd.Grouper(key='date', freq='Y'), 'type'])['amount'].sum().reset_index()
        date_format = "%Y"
    
    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### Transaction Flow by Type")
        fig_timeline = px.bar(
            agg_txns, 
            x='date', 
            y='amount', 
            color='type',
            color_discrete_map={'Credit': '#48bb78', 'Debit': '#e53e3e'},
            title=f"By Type ({txn_timeline})",
            barmode='group'
        )
        fig_timeline.update_layout(
            height=350,
            xaxis_title=None,
            yaxis_title="Amount",
            xaxis=dict(tickformat=date_format, tickangle=-45),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF')
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with chart_col2:
        st.markdown("#### Transaction Flow by Channel")
        # Check if channel column exists
        if 'channel' in transactions.columns:
            # Aggregate by channel
            if txn_timeline == "Day-wise":
                agg_channel = transactions.groupby([pd.Grouper(key='date', freq='D'), 'channel'])['amount'].sum().reset_index()
            elif txn_timeline == "Month-wise":
                agg_channel = transactions.groupby([pd.Grouper(key='date', freq='M'), 'channel'])['amount'].sum().reset_index()
            else:  # Year-wise
                agg_channel = transactions.groupby([pd.Grouper(key='date', freq='Y'), 'channel'])['amount'].sum().reset_index()
            
            # Define contrasting colors for channels
            channel_colors = {
                'Wire': '#8b5cf6',      # Purple
                'ATM': '#f59e0b',       # Orange
                'Cash': '#10b981',      # Green
                'Debit': '#3b82f6',     # Blue
                'Credit': '#ec4899',    # Pink
                'Online': '#06b6d4',    # Cyan
                'Branch': '#84cc16'     # Lime
            }
            
            fig_channel = px.bar(
                agg_channel,
                x='date',
                y='amount',
                color='channel',
                color_discrete_map=channel_colors,
                title=f"By Channel ({txn_timeline})",
                barmode='stack'
            )
            fig_channel.update_layout(
                height=350,
                xaxis_title=None,
                yaxis_title="Amount",
                xaxis=dict(tickformat=date_format, tickangle=-45),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF')
            )
            st.plotly_chart(fig_channel, use_container_width=True)
        else:
            st.info("Channel data not available for this customer")
    
    # === TRANSACTION PATTERN NETWORK VISUALIZATION ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">Transaction Pattern Visualization</div>
        </div>
    """, unsafe_allow_html=True)

    if 'counterparty' in transactions.columns and not transactions.empty:
        import plotly.graph_objects as go
        import math

        # Aggregate flows between customer and counterparties
        flow_data = transactions.groupby(['counterparty', 'type']).agg(
            total_amount=('amount', 'sum'),
            txn_count=('transaction_id', 'count'),
            channels=('channel', lambda x: ', '.join(x.unique())),
            countries=('country_dest', lambda x: ', '.join(x.dropna().unique())) if 'country_dest' in transactions.columns else ('channel', lambda x: '')
        ).reset_index()

        # Get top counterparties by total volume
        top_counterparties = transactions.groupby('counterparty')['amount'].sum().nlargest(12).index.tolist()
        flow_data = flow_data[flow_data['counterparty'].isin(top_counterparties)]

        if not flow_data.empty:
            # Summary stats above the graph
            total_inflow = flow_data[flow_data['type'] == 'Credit']['total_amount'].sum()
            total_outflow = flow_data[flow_data['type'] == 'Debit']['total_amount'].sum()
            total_volume = total_inflow + total_outflow
            num_cp = len(top_counterparties)

            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            with stat_col1:
                st.markdown(f"""
                    <div style="background:#292B3D; padding:14px; border-radius:10px; border:1px solid #333333; text-align:center;">
                        <div style="font-size:0.75rem; color:#979AA3; text-transform:uppercase; letter-spacing:0.5px;">Counterparties</div>
                        <div style="font-size:1.5rem; font-weight:700; color:#00aeef;">{num_cp}</div>
                    </div>
                """, unsafe_allow_html=True)
            with stat_col2:
                st.markdown(f"""
                    <div style="background:#292B3D; padding:14px; border-radius:10px; border:1px solid #333333; text-align:center;">
                        <div style="font-size:0.75rem; color:#979AA3; text-transform:uppercase; letter-spacing:0.5px;">Total Inflow</div>
                        <div style="font-size:1.5rem; font-weight:700; color:#48bb78;">{total_inflow:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with stat_col3:
                st.markdown(f"""
                    <div style="background:#292B3D; padding:14px; border-radius:10px; border:1px solid #333333; text-align:center;">
                        <div style="font-size:0.75rem; color:#979AA3; text-transform:uppercase; letter-spacing:0.5px;">Total Outflow</div>
                        <div style="font-size:1.5rem; font-weight:700; color:#e53e3e;">{total_outflow:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with stat_col4:
                st.markdown(f"""
                    <div style="background:#292B3D; padding:14px; border-radius:10px; border:1px solid #333333; text-align:center;">
                        <div style="font-size:0.75rem; color:#979AA3; text-transform:uppercase; letter-spacing:0.5px;">Total Volume</div>
                        <div style="font-size:1.5rem; font-weight:700; color:#FFFFFF;">{total_volume:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Build node positions — customer at center, counterparties in a circle
            node_x = [0.0]
            node_y = [0.0]
            node_labels = [customer_id]
            node_colors = ['#00aeef']
            node_sizes = [55]
            node_border_colors = ['rgba(0,174,239,0.3)']
            node_border_sizes = [75]

            radius = 1.2
            for i, cp in enumerate(top_counterparties):
                angle = 2 * math.pi * i / num_cp - math.pi / 2  # Start from top
                node_x.append(radius * math.cos(angle))
                node_y.append(radius * math.sin(angle))
                node_labels.append(cp)
                cp_credits = flow_data[(flow_data['counterparty'] == cp) & (flow_data['type'] == 'Credit')]['total_amount'].sum()
                cp_debits = flow_data[(flow_data['counterparty'] == cp) & (flow_data['type'] == 'Debit')]['total_amount'].sum()
                if cp_credits > cp_debits:
                    node_colors.append('#48bb78')
                    node_border_colors.append('rgba(72,187,120,0.2)')
                else:
                    node_colors.append('#e53e3e')
                    node_border_colors.append('rgba(229,62,62,0.2)')
                scaled = 22 + min(18, (cp_credits + cp_debits) / (transactions['amount'].sum() + 1) * 120)
                node_sizes.append(scaled)
                node_border_sizes.append(scaled + 14)

            # Build edges with curves
            edge_traces = []
            arrow_annotations = []
            max_amount = flow_data['total_amount'].max() if not flow_data.empty else 1

            for _, row in flow_data.iterrows():
                cp = row['counterparty']
                if cp not in top_counterparties:
                    continue
                cp_idx = top_counterparties.index(cp) + 1

                edge_color = 'rgba(72,187,120,0.6)' if row['type'] == 'Credit' else 'rgba(229,62,62,0.6)'
                edge_width = 1.5 + (row['total_amount'] / max_amount) * 5

                if row['type'] == 'Credit':
                    x0, y0 = node_x[cp_idx], node_y[cp_idx]
                    x1, y1 = node_x[0], node_y[0]
                else:
                    x0, y0 = node_x[0], node_y[0]
                    x1, y1 = node_x[cp_idx], node_y[cp_idx]

                # Curved edge using a control point offset perpendicular to the line
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                dx, dy = x1 - x0, y1 - y0
                length = math.sqrt(dx**2 + dy**2) + 0.001
                # Perpendicular offset for curve
                offset = 0.08
                cx = mx + offset * (-dy / length)
                cy = my + offset * (dx / length)

                # Approximate curve with 3 segments
                pts_x, pts_y = [], []
                for t in [0, 0.25, 0.5, 0.75, 1.0]:
                    bx = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
                    by = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
                    pts_x.append(bx)
                    pts_y.append(by)
                pts_x.append(None)
                pts_y.append(None)

                edge_traces.append(go.Scatter(
                    x=pts_x, y=pts_y,
                    mode='lines',
                    line=dict(width=edge_width, color=edge_color, shape='spline'),
                    hoverinfo='text',
                    text=f"<b>{row['type']}</b><br>Amount: {row['total_amount']:,.2f}<br>Transactions: {row['txn_count']}<br>Channels: {row['channels']}",
                    showlegend=False
                ))

                # Arrow annotation at 70% along the curve
                t = 0.7
                ax_pt = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
                ay_pt = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
                t2 = 0.65
                ax2 = (1-t2)**2 * x0 + 2*(1-t2)*t2 * cx + t2**2 * x1
                ay2 = (1-t2)**2 * y0 + 2*(1-t2)*t2 * cy + t2**2 * y1
                arrow_color = '#48bb78' if row['type'] == 'Credit' else '#e53e3e'
                arrow_annotations.append(dict(
                    x=ax_pt, y=ay_pt, ax=ax2, ay=ay2,
                    xref='x', yref='y', axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=3, arrowsize=1.5, arrowwidth=2,
                    arrowcolor=arrow_color
                ))

            # Glow ring trace (behind the main nodes)
            glow_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                marker=dict(size=node_border_sizes, color=node_border_colors, line=dict(width=0)),
                hoverinfo='skip',
                showlegend=False
            )

            # Node hover text
            node_hover = []
            node_hover.append(f"<b>{customer_id}</b><br>Investigated Customer<br>Volume: {total_volume:,.2f}")
            for i, cp in enumerate(top_counterparties):
                cp_rows = flow_data[flow_data['counterparty'] == cp]
                total = cp_rows['total_amount'].sum()
                count = cp_rows['txn_count'].sum()
                countries_str = ', '.join(cp_rows['countries'].unique()) if 'countries' in cp_rows.columns else ''
                hover = f"<b>{cp}</b><br>Total: {total:,.2f}<br>Transactions: {count}"
                if countries_str:
                    hover += f"<br>Countries: {countries_str}"
                node_hover.append(hover)

            # Main node trace
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='rgba(255,255,255,0.15)')
                ),
                text=node_labels,
                textposition='top center',
                textfont=dict(size=10, color='#FFFFFF', family='Arial'),
                hoverinfo='text',
                hovertext=node_hover,
                showlegend=False
            )

            # Assemble figure
            fig_network = go.Figure(data=edge_traces + [glow_trace, node_trace])
            fig_network.update_layout(
                height=520,
                plot_bgcolor='#1a1d2e',
                paper_bgcolor='#1a1d2e',
                font=dict(color='#FFFFFF'),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.8, 1.8]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.8, 1.8], scaleanchor='x'),
                margin=dict(l=10, r=10, t=10, b=40),
                annotations=arrow_annotations + [
                    dict(text="<b>Green</b> = Inflow (Credit)  |  <b>Red</b> = Outflow (Debit)  |  Line thickness = Amount",
                         xref="paper", yref="paper", x=0.5, y=-0.04,
                         showarrow=False, font=dict(size=11, color='#979AA3'))
                ]
            )
            st.plotly_chart(fig_network, use_container_width=True)
        else:
            st.info("Not enough counterparty data to generate pattern visualization.")
    else:
        st.info("Counterparty data not available for this customer.")

    # === COMPREHENSIVE TRANSACTION DETAILS ===
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prepare transaction display with all available columns
    txn_display_cols = ['date', 'transaction_id', 'type', 'amount', 'currency', 'amount_gbp', 
                        'channel', 'country_dest', 'counterparty', 'description']
    
    # Filter to only include columns that exist in the dataframe
    available_txn_cols = [col for col in txn_display_cols if col in transactions.columns]
    
    # Create a copy for display and convert GB to UK in country_dest
    transactions_display = transactions[available_txn_cols].copy()
    if 'country_dest' in transactions_display.columns:
        transactions_display['country_dest'] = transactions_display['country_dest'].apply(display_country)
    
    st.dataframe(
        transactions_display.sort_values('date', ascending=False),
        hide_index=True,
        use_container_width=True,
        column_config={
            "date": "Date",
            "transaction_id": "Transaction ID",
            "type": "Type",
            "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
            "currency": "Currency",
            "amount_gbp": st.column_config.NumberColumn("Amount (GBP)", format="%.2f"),
            "channel": "Channel",
            "country_dest": "Destination Country",
            "counterparty": "Receiver ID",
            "description": "Description"
        }
    )
    
    
    # === REGULATORY REPORTING ===
    st.markdown("""
        <div class="section-header">
            <div class="section-title">Regulatory Reporting</div>
        </div>
    """, unsafe_allow_html=True)
    
    # SAR Type Selection with styled cards
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="color: #979AA3; font-size: 0.95em; margin-bottom: 12px; font-weight: 500;">
                SELECT SAR TYPE
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    sar_type_choice = st.radio(
        "Choose report type:",
        [
            "Internal SAR (Preliminary Investigation)",
            "Normal SAR (Regulatory Filing with FinCEN)"
        ],
        key=f"sar_type_radio_{customer_id}",
        label_visibility="collapsed"
    )
    
    # Display info card based on selection
    if "Internal" in sar_type_choice:
        st.markdown("""
            <div class="info-card" style="background-color: #1a2332; border-left: 4px solid #00aeef;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 1.5em;">ℹ️</div>
                    <div>
                        <div style="font-weight: 600; color: #00aeef; margin-bottom: 4px;">Internal SAR</div>
                        <div style="color: #979AA3; font-size: 0.9em;">
                            This report will be reviewed by the compliance team before any regulatory action.
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-card" style="background-color: #2d1f1f; border-left: 4px solid #e53e3e;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 1.5em;">⚠️</div>
                    <div>
                        <div style="font-weight: 600; color: #e53e3e; margin-bottom: 4px;">Regulatory SAR</div>
                        <div style="color: #979AA3; font-size: 0.9em;">
                            This report will be filed with FinCEN. <strong style="color: #e53e3e;">DO NOT inform the customer (tipping off is illegal)</strong>.
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Generate Suspicious Activity Report (SAR) ", key="gen_sar_btn", type="primary"):
        with st.spinner("Analyzing patterns and compiling SAR..."):
            time.sleep(1.5)
            result = generator.generate(customer, transactions)
            st.session_state['generated_narrative'] = result['narrative_text']
            st.session_state['audit_trace'] = result['audit_trace']
            st.session_state['current_customer'] = customer
            
            # Set SAR type based on selection
            st.session_state['sar_type'] = "Internal" if "Internal" in sar_type_choice else "Normal"
            st.session_state['sar_status'] = "Draft"
            
            # Reset to Stage 1 for new SAR
            st.session_state['sar_report_stage'] = 1
            st.session_state['sar_edit_comments'] = ""
            
            # Log with SAR type
            sar_type_label = st.session_state['sar_type']
            audit_logger.log_event(f"{sar_type_label} SAR Generated", "Admin_User", {
                "customer_id": customer['customer_id'], 
                "sar_type": sar_type_label,
                "status": "Generated"
            })
            
            # Navigate to AI Assistant Page
            st.session_state["nav_selection"] = "AI Assistant"
            st.rerun()


def display_sar_editor():
    # Force scroll to top by using a container at the top
    st.markdown('<div id="top-of-page"></div>', unsafe_allow_html=True)
    
    # Check for comparison mode
    comparison_mode = st.session_state.get('view_comparison_mode', False)
    
    if comparison_mode:
        # --- COMPARISON VIEW ---
        st.markdown("Report Comparison (Initial vs Final)")
        
        if st.button("← Back to Editor", key="back_from_comp"):
            st.session_state['view_comparison_mode'] = False
            st.rerun()
            
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("Initial Report")
            import base64
            pdf_path_initial = "Fincen SAR formata also includes basic rules_BEFORECHANGES.pdf"
            if os.path.exists(pdf_path_initial):
                with open(pdf_path_initial, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>', unsafe_allow_html=True)
            else:
                st.error("Initial report PDF not found.")

        with comp_col2:
            st.markdown("Final Report")
            import base64
            pdf_path_final = "Fincen SAR formata also includes basic rules_afterChangesFinal.pdf"
            if os.path.exists(pdf_path_final):
                with open(pdf_path_final, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>', unsafe_allow_html=True)
            else:
                st.error("Final report PDF not found.")
                
        return  # Exit function to show only comparison view

    # --- STANDARD EDITOR VIEW ---
    # Use a container to group the header elements and help with focus
    with st.container():
        st.markdown("---")
        
        # Display SAR Type Badge
        sar_type = st.session_state.get('sar_type', 'Internal')
        report_stage = st.session_state.get('sar_report_stage', 1)
    
        # Custom CSS for AI Assistant
        st.markdown("""
        <style>
        .ai-chat-container {
            background-color: #292B3D;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #333333;
            margin-bottom: 20px;
        }
        .ai-msg-bubble {
            background-color: #161B2F;
            color: #E2E8F0;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #00aeef;
        }
        .user-msg-bubble {
            background-color: #00395d;
            color: #FFFFFF;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: right;
            border-right: 4px solid #e53e3e;
        }
        .empty-state-msg {
            color: #979AA3;
            font-style: italic;
            text-align: center;
            padding: 20px;
            background-color: #161B2F;
            border-radius: 8px;
            border: 1px dashed #4A5568;
        }
        .stTextArea textarea {
            background-color: #161B2F !important;
            color: #FFFFFF !important;
            border: 1px solid #4A5568 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Stage Indicator
    col_stage1, col_stage2 = st.columns(2)
    with col_stage1:
        if report_stage == 1:
            st.markdown("Stage 1: Initial Report")
        else:
            st.markdown("Stage 1: Complete")
    with col_stage2:
        if report_stage == 2:
            st.markdown("Stage 2: Final Report with Edits")
            st.markdown('<div style="background-color: #292B3D; color: #48bb78; padding: 10px; border-radius: 8px; font-weight: bold; text-align: center;">Final report incorporating your edits</div>', unsafe_allow_html=True)
        else:
            st.markdown("Stage 2: Pending")
    
    if sar_type == "Internal":
        st.markdown("Internal SAR - Compliance Review")
    else:
        st.markdown("Normal SAR - Regulatory Filing")
        st.warning("**REGULATORY FILING** - Do not inform the customer (tipping off is illegal)")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        if report_stage == 1:
            st.markdown("### Initial Report Preview")
            
            # Show Initial Report PDF Preview
            import base64
            pdf_path_initial = "Fincen SAR formata also includes basic rules_BEFORECHANGES.pdf"
            if os.path.exists(pdf_path_initial):
                with open(pdf_path_initial, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>', unsafe_allow_html=True)
            else:
                st.warning("Initial report PDF preview not available.")
            
            # Divider
            st.markdown("---")
            
            # AI Assistant for refinement
            st.markdown("### AI Assistant - Edit Instructions")
            
            # Chat Input Area with Generate Button side-by-side
            input_col1, input_col2 = st.columns([4, 1])
            
            with input_col1:
                edit_comments = st.text_area(
                    "Enter edit instructions...",
                    value=st.session_state.get('sar_edit_comments', ''),
                    height=150,
                    placeholder="Enter specific edit instructions (e.g., 'Add more details about transaction patterns', 'Update risk assessment section')...",
                    label_visibility="collapsed",
                    key="edit_comments_input"
                )
            
            with input_col2:
                st.markdown("<br>", unsafe_allow_html=True) # Spacing alignment
                if st.button("Generate\nFinal Report", type="primary", use_container_width=True, key="proceed_to_stage2"):
                    # Save edit comments and move to stage 2
                    st.session_state['sar_edit_comments'] = edit_comments
                    st.session_state['sar_report_stage'] = 2
                    
                    # Log action
                    audit_logger.log_event(f"{sar_type} SAR - Proceeded to Final Report", "Admin_User", {
                        "customer_id": st.session_state['current_customer']['customer_id'],
                        "sar_type": sar_type,
                        "has_edits": bool(edit_comments.strip())
                    })
                    
                    st.success("Generating Final Report...")
                    st.rerun()
            
            
        
        else:  # Stage 2
            st.markdown("### Final Report Preview")
            st.success("✓ This is your final edited report ready for submission")
            
            # Show Final Report PDF Preview
            import base64
            pdf_path_final = "Fincen SAR formata also includes basic rules_afterChangesFinal.pdf"
            if os.path.exists(pdf_path_final):
                with open(pdf_path_final, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>', unsafe_allow_html=True)
            else:
                st.error("Final report PDF not found. Please ensure 'Fincen SAR formata also includes basic rules_afterChangesFinal.pdf' exists in the root folder.")
            
            # Show AI assistant comments if any were added
            if st.session_state.get('sar_edit_comments'):
                st.markdown("---")
                st.markdown("### Edit Instructions Applied")
                st.info(st.session_state['sar_edit_comments'])
            
            # Explanation Section
            st.markdown("---")
            
            # Initialize session state for explanation visibility
            if 'show_explanation' not in st.session_state:
                st.session_state['show_explanation'] = False
            
            # Explanation Button
            if st.button("Show Explanation", use_container_width=True, key="show_explanation_btn"):
                st.session_state['show_explanation'] = not st.session_state['show_explanation']
                st.rerun()
            
            # Display explanation if button was clicked
            if st.session_state.get('show_explanation', False):
                st.markdown("### Report Explanation")
                
                # Hardcoded explanation text
                explanation_text = """
### 1 Why Structuring Was Selected

**Pattern Identified:**
- 19 cash deposits
- Each below $10,000
- Most between $9,850 – $9,990
- Occurring within 72-hour clusters

**CTR threshold under BSA = $10,000**

Repeated $9,9xx deposits indicate threshold avoidance behavior.
The probability of 19 consecutive deposits just under $10,000 occurring randomly is statistically low.

---

### 2 Why Multi-Branch Activity Increased Risk

**Deposits occurred across:**
- Downtown Chicago
- West Loop
- River North

**AI Risk Insight:**
Multi-branch usage suggests deliberate attempt to avoid detection clustering.

---

### 3 Why International Wire Transfers Elevated Risk

**On 04/15/24:**
Two outgoing wires totaling $120,000 to Estonia.

**Risk factors:**
- Cross-border transfer
- Beneficiary country with higher AML monitoring sensitivity
- No invoice provided
- Cash-funded account

**AI Interpretation:**
Cash → Structuring → Rapid International Transfer

This matches classic **placement → layering** pattern.

---

### 4 Why SAR Threshold Is Met (Regulatory Basis)

**Under 31 U.S.C. §5318(g):**
A SAR must be filed if:
- Suspicious activity ≥ $5,000
- Institution suspects BSA evasion

**Here:**
- Total structured cash = $148,750
- Clearly above minimum threshold.

---

### 5️ Why No Financial Loss Reported

This case is **not fraud against the bank**.
- Funds belong to customer.
- The issue is potential illegal origin or structuring behavior.

**Therefore:**
- Loss = $0.00
- But compliance risk = **High**.

---

### 6 Why Law Enforcement Escalation Was Recommended

When total activity expanded to $312,400 across multiple accounts:

**Risk Model Output:**
- Aggregate suspicious volume doubled
- Cross-account coordination detected
- Structured deposits persisted after monitoring alert

This indicates **intentional evasion** rather than misunderstanding.

---

### 7 Behavioral Risk Indicators Identified

**AI behavioral markers:**
- Round-number proximity deposits
- Sequential day deposits
- No business justification
- High cash vs stated business profile
- Immediate outbound wire transfer
                """
                
                st.markdown(explanation_text)
                
                # Optional: Add a close button
                if st.button("Hide Explanation", key="hide_explanation_btn"):
                    st.session_state['show_explanation'] = False
                    st.rerun()



        
    with c2:
        st.markdown("### Actions")
        
        # Stage-specific actions
       
            
        # Stage-specific actions
        if report_stage == 1:
            # Stage 1: Actions
            pass
        
        else:  # Stage 2
            
        
          
            # COMPARE BUTTON
            if st.button("Compare Initial vs Final", use_container_width=True, key="comp_btn"):
                st.session_state['view_comparison_mode'] = True
                st.rerun()
            
            # Stage 2: Button to go back to initial report
            if st.button("← Back to Initial Report", use_container_width=True, key="back_to_stage1"):
                st.session_state['sar_report_stage'] = 1
                st.rerun()
            
            st.markdown("---")
        
        # Save Draft with PDF Export (available for both stages)
        pdf_label = "Download Initial Report PDF" if report_stage == 1 else "Download Final Report PDF"
        
        # Determine which PDF template to use
        if report_stage == 1:
            pdf_template_path = "Fincen SAR formata also includes basic rules_BEFORECHANGES.pdf"
        else:
            pdf_template_path = "Fincen SAR formata also includes basic rules_afterChangesFinal.pdf"
        
        if os.path.exists(pdf_template_path):
            # Read the PDF file
            with open(pdf_template_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Download button
            from datetime import datetime
            customer_id = st.session_state['current_customer']['customer_id'] if st.session_state.get('current_customer') else "UNKNOWN"
            stage_label = "Initial" if report_stage == 1 else "Final"
            filename = f"STR_{stage_label}_Report_{customer_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            st.download_button(
                label=pdf_label,
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
                key=f"download_pdf_stage{report_stage}"
            )
            
            # Log action
            if st.session_state.get('current_customer'):
                audit_logger.log_event(f"{sar_type} SAR {stage_label} Report Downloaded", "Admin_User", {
                    "customer_id": customer_id,
                    "sar_type": sar_type,
                    "stage": report_stage,
                    "format": "PDF"
                })
        else:
            st.error(f"PDF template not found: {pdf_template_path}")

        
        # Share SAR Button
        if st.button("Generate Share Link", use_container_width=True, key="share_sar"):
            import hashlib
            from datetime import datetime
            
            # Generate unique share ID based on customer ID and timestamp
            customer_id = st.session_state['current_customer']['customer_id']
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_string = f"{customer_id}_{timestamp}_{sar_type}"
            share_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
            
            # Create shared_reports directory if it doesn't exist
            shared_reports_dir = "data/shared_reports"
            os.makedirs(shared_reports_dir, exist_ok=True)
            
            # Save report data to JSON file
            share_data = {
                'share_id': share_id,
                'customer': st.session_state['current_customer'],
                'narrative': st.session_state['generated_narrative'],
                'audit_trace': st.session_state['audit_trace'],
                'sar_type': st.session_state['sar_type'],
                'sar_status': st.session_state['sar_status'],
                'report_stage': st.session_state['sar_report_stage'],
                'edit_comments': st.session_state.get('sar_edit_comments', ''),
                'created_at': timestamp
            }
            
            share_file_path = os.path.join(shared_reports_dir, f"{share_id}.json")
            with open(share_file_path, 'w') as f:
                json.dump(share_data, f, indent=2)
            
            # Generate real shareable link with query parameter
            # Get the current URL (works for both localhost and deployed)
            share_link = f"http://localhost:8501/?share_id={share_id}"
            
            # Store in session state
            st.session_state['share_link'] = share_link
            st.session_state['share_id'] = share_id
            
            # Log action
            audit_logger.log_event(f"{sar_type} SAR Share Link Generated", "Admin_User", {
                "customer_id": customer_id,
                "sar_type": sar_type,
                "share_id": share_id
            })
            
            st.success("Share link generated!")
        
        # Display share link if generated
        if 'share_link' in st.session_state and st.session_state.get('share_link'):
            st.code(st.session_state['share_link'], language=None)

        
        st.markdown("---")
        
        # Conditional actions based on SAR type
        if sar_type == "Internal":
            # Internal SAR Actions
            st.markdown("#### Internal SAR Actions")
            
            if st.button("Escalate to Regulatory SAR", type="primary", use_container_width=True, key="escalate_sar"):
                st.session_state['sar_type'] = "Normal"
                st.session_state['sar_status'] = "Escalated"
                
                audit_logger.log_event("Internal SAR Escalated to Regulatory", "Admin_User", {
                    "customer_id": st.session_state['current_customer']['customer_id'],
                    "previous_type": "Internal",
                    "new_type": "Normal"
                })
                
                st.success("Escalated to Regulatory SAR!")
                st.rerun()
            
            if st.button("Dismiss Internal SAR", use_container_width=True, key="dismiss_sar"):
                st.session_state['sar_status'] = "Dismissed"
                
                audit_logger.log_event("Internal SAR Dismissed", "Admin_User", {
                    "customer_id": st.session_state['current_customer']['customer_id'],
                    "sar_type": "Internal"
                })
                
                st.info("Internal SAR dismissed. No regulatory action taken.")
                
        else:
            # Normal SAR Actions
            st.markdown("#### Regulatory Actions")
            
            if st.button("Proceed for Review", type="primary", use_container_width=True, key="file_fiu"):
                st.session_state['sar_status'] = "Filed"
                
                audit_logger.log_event("Normal SAR Filed with FinCEN", "Admin_User", {
                    "customer_id": st.session_state['current_customer']['customer_id'],
                    "sar_type": "Normal",
                    "status": "Filed"
                })
                
                st.success("SAR Filed Successfully with FinCEN!")

def audit_page():
    st.title("Audit Logs")
    st.markdown("Complete audit trail of all system activities")
    
    logs = audit_logger.get_logs()
    if logs:
        # Convert to DataFrame for better display
        df_logs = pd.DataFrame(logs)
        
        # Format timestamp for better readability
        if 'timestamp' in df_logs.columns:
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
            df_logs['formatted_time'] = df_logs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Reorder columns for better display
            display_cols = ['formatted_time', 'event_type', 'user', 'details']
            df_logs = df_logs[display_cols]
            df_logs.columns = ['Timestamp', 'Event Type', 'User', 'Details']
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", len(logs))
        with col2:
            event_types = df_logs['Event Type'].nunique() if 'Event Type' in df_logs.columns else 0
            st.metric("Event Types", event_types)
        with col3:
            # Get most recent event time
            if 'Timestamp' in df_logs.columns:
                latest = df_logs['Timestamp'].iloc[-1] if len(df_logs) > 0 else "N/A"
                st.metric("Latest Event", latest)
        
        st.markdown("---")
        
        # Filter by event type
        if 'Event Type' in df_logs.columns:
            event_types_list = ['All'] + sorted(df_logs['Event Type'].unique().tolist())
            selected_event = st.selectbox("Filter by Event Type", event_types_list)
            
            if selected_event != 'All':
                df_logs = df_logs[df_logs['Event Type'] == selected_event]
        
        # Display logs in reverse chronological order (newest first)
        st.dataframe(df_logs.iloc[::-1], use_container_width=True, hide_index=True)
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON Download
            st.download_button(
                "Download as JSON", 
                data=json.dumps(logs, indent=4), 
                file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # PDF Download
            if st.button("Generate PDF", use_container_width=True):
                from reportlab.lib.pagesizes import letter, landscape
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from io import BytesIO
                import os
                
                # Create PDF
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch)
                story = []
                styles = getSampleStyleSheet()
                
                # Add logo if it exists
                logo_path = None
                if os.path.exists("logo.png"):
                    logo_path = "logo.png"
                elif os.path.exists("logo.jpg"):
                    logo_path = "logo.jpg"
                
                if logo_path:
                    try:
                        logo = Image(logo_path, width=3*inch, height=1*inch)
                        logo.hAlign = 'CENTER'
                        story.append(logo)
                        story.append(Spacer(1, 0.2*inch))
                    except:
                        pass  # If logo fails to load, continue without it
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#00395d'),
                    spaceAfter=20,
                    alignment=1  # Center
                )
                story.append(Paragraph("Audit Log Report", title_style))
                story.append(Paragraph(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))

                
                # Summary statistics
                summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontSize=10, spaceAfter=10)
                story.append(Paragraph(f"<b>Total Events:</b> {len(logs)} | <b>Event Types:</b> {event_types} | <b>Latest Event:</b> {latest}", summary_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Prepare table data
                table_data = [['Timestamp', 'Event Type', 'User', 'Details']]
                
                # Add log entries (reverse chronological)
                for _, row in df_logs.iloc[::-1].iterrows():
                    details_str = str(row['Details'])
                    if len(details_str) > 100:
                        details_str = details_str[:97] + "..."
                    
                    table_data.append([
                        str(row['Timestamp']),
                        str(row['Event Type']),
                        str(row['User']),
                        details_str
                    ])
                
                # Create table
                table = Table(table_data, colWidths=[1.8*inch, 2*inch, 1.2*inch, 4*inch])
                table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00395d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(table)
                
                # Build PDF
                doc.build(story)
                buffer.seek(0)
                
                # Download button for PDF
                st.download_button(
                    label="Download PDF",
                    data=buffer,
                    file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("PDF generated successfully!")
    else:
        st.info("No audit logs found. Logs will appear here as users perform actions in the system.")


# --- Navigation ---

def ai_assistant_page():
    st.title("AI Assistant")
    display_sar_editor()

if not st.session_state.get('authenticated', False):
    login_page()
else:
    # Sidebar header
    if os.path.exists("logo.jpg"):
        st.sidebar.image("logo.jpg", width=150)
    elif os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=150)
    else:
        st.sidebar.markdown("Authority")
    st.sidebar.markdown("<h1 style='font-size: 2.2rem; margin-bottom: 0;'>SAR Generator</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size: 1.1rem; color: #E0E0E0; margin-top: 5px;'>Advanced AML Monitoring System</p>", unsafe_allow_html=True)

    # Logged-in user info
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='background:#292B3D; padding:12px 16px; border-radius:10px; border:1px solid #333333;'>"
        f"<span style='font-size:0.8rem; color:#979AA3; text-transform:uppercase; letter-spacing:0.5px;'>Logged in as</span><br>"
        f"<span style='font-size:1.1rem; font-weight:600;'>{st.session_state['username']}</span><br>"
        f"<span style='font-size:0.85rem; color:#00aeef;'>{st.session_state['user_role']}</span></div>",
        unsafe_allow_html=True
    )
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['user_role'] = None
        st.session_state['username'] = None
        st.rerun()

    # Credentials reference
    with st.sidebar.expander("Login Credentials"):
        for r, creds in USER_CREDENTIALS.items():
            st.markdown(
                f"<div style='background:#292B3D; padding:10px 14px; border-radius:8px; border:1px solid #333333; margin-bottom:8px;'>"
                f"<div style='font-size:0.85rem; font-weight:600; color:#FFFFFF; margin-bottom:4px;'>{r}</div>"
                f"<div style='font-size:0.78rem; color:#979AA3;'>User: <span style='color:#00aeef;'>{creds['username']}</span></div>"
                f"<div style='font-size:0.78rem; color:#979AA3;'>Pass: <span style='color:#00aeef;'>{creds['password']}</span></div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.sidebar.markdown("---")

    # Initialize navigation state
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Admin Dashboard"

    def update_nav():
        st.session_state["nav_selection"] = st.session_state["nav_radio"]

    # Dynamic Sidebar Logic
    if st.session_state["nav_selection"] == "AI Assistant":
        if st.sidebar.button("← Back to Dashboard"):
            st.session_state["nav_selection"] = "User Management"
            st.rerun()
    else:
        current_index = 0
        options = ["Admin Dashboard", "User Management", "Audit Logs"]
        if st.session_state["nav_selection"] in options:
            current_index = options.index(st.session_state["nav_selection"])

        page = st.sidebar.radio(
            "Navigation",
            options,
            key="nav_radio",
            index=current_index,
            on_change=update_nav
        )

    if st.session_state["nav_selection"] == "Admin Dashboard":
        admin_dashboard()
    elif st.session_state["nav_selection"] == "User Management":
        user_management_page()
    elif st.session_state["nav_selection"] == "AI Assistant":
        ai_assistant_page()
    elif st.session_state["nav_selection"] == "Audit Logs":
        audit_page()
