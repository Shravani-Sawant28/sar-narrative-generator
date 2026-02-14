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
    /* Primary Button (Generate STR) - Red */
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
    div[data-testid="stButton"] button:has-text("File with FIU-IND"),
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

# Session State
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

# Collaboration State - Simulated Active Admins
if 'active_admins' not in st.session_state:
    from datetime import datetime, timedelta
    st.session_state['active_admins'] = [
        {
            "id": "admin_001",
            "name": "You",
            "initials": "ME",
            "color": "#00aeef",
            "activity": "Viewing Dashboard",
            "last_active": datetime.now()
        },
        {
            "id": "admin_002",
            "name": "Priya Sharma",
            "initials": "PS",
            "color": "#e53e3e",
            "activity": "Reviewing Alert #245",
            "last_active": datetime.now() - timedelta(seconds=15)
        },
        {
            "id": "admin_003",
            "name": "Amit Patel",
            "initials": "AP",
            "color": "#48bb78",
            "activity": "Generating SAR for CUST-998877",
            "last_active": datetime.now() - timedelta(seconds=45)
        }
    ]


# --- Pages ---

def admin_dashboard():
    # Header Image
    # if os.path.exists("pageheader.png"):
    #     st.image("pageheader.png", use_container_width=True)
        
    st.title("Admin Dashboard")
    st.markdown("Overview of AML Monitoring Activities")
    
    # Collaboration Panel - Active Admins
    st.markdown("---")
    st.markdown("Active Admins")
    
    # Display active admins in a horizontal layout
    admin_cols = st.columns(len(st.session_state['active_admins']))
    for idx, admin in enumerate(st.session_state['active_admins']):
        with admin_cols[idx]:
            # Calculate time since last active
            from datetime import datetime
            time_diff = datetime.now() - admin['last_active']
            if time_diff.total_seconds() < 60:
                time_str = f"{int(time_diff.total_seconds())}s ago"
            else:
                time_str = f"{int(time_diff.total_seconds() / 60)}m ago"
            
            # Admin card with colored badge
            st.markdown(f"""
            <div style="background-color: #292B3D; padding: 15px; border-radius: 10px; border: 2px solid {admin['color']}; text-align: center;">
                <div style="background-color: {admin['color']}; width: 50px; height: 50px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto;
                            font-weight: bold; font-size: 1.2em; color: white;">
                    {admin['initials']}
                </div>
                <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 5px;">{admin['name']}</div>
                <div style="color: #979AA3; font-size: 0.85em; margin-bottom: 3px;">{admin['activity']}</div>
                <div style="color: {admin['color']}; font-size: 0.75em; font-weight: 500;">{time_str}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

    
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
            name='STRs Processed',
            marker_color='#ffffff',
            marker_line_color='#002d4a',
            marker_line_width=1,
            text=sar_data['sar_processed'],
            textposition='outside',
            textfont=dict(size=10, color='#00aeef', family='Arial Black'),
            hovertemplate='<b>STRs Processed</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        # Add SAR Disseminated bars (light blue)
        fig_sar.add_trace(go.Bar(
            x=sar_data['date'],
            y=sar_data['sar_disseminated'],
            name='STRs Disseminated',
            marker_color='#00aeef',
            marker_line_color='#0088cc',
            marker_line_width=1,
            text=sar_data['sar_disseminated'],
            textposition='outside',
            textfont=dict(size=10, color='#00aeef', family='Arial Black'),
            hovertemplate='<b>STRs Disseminated</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        # Update layout to match reference image style
        fig_sar.update_layout(
            title={
                'text': f"Chart: {timeline_option.replace('-wise', '')} STRs Processed and Disseminated",
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.98,
                'yanchor': 'top',
                'font': {'size': 14, 'family': 'Georgia, serif', 'color': '#FFFFFF'}
            },
            height=500,
            xaxis_title="FINANCIAL YEAR" if timeline_option == "Year-wise" else "TIME PERIOD",
            yaxis_title="NO.OF STRS",
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
            color_discrete_map={'High': '#e53e3e', 'Medium': '#ed8936', 'Low': '#48bb78'}
        )
        fig_donut.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_donut, use_container_width=True)

    # Recent Flagged Transactions (Mock)
    st.subheader(" Recent Flagged Transactions")
    flagged_txns = all_txns[all_txns['amount'] > 50000].sort_values('date', ascending=False).head(5)
    st.dataframe(
        flagged_txns[['transaction_id', 'customer_id', 'date', 'amount', 'type', 'description']],
        hide_index=True,
        use_container_width=True
    )

def user_management_page():
    st.title(" User Management")
    
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
    
    # Visual Transaction History with Timeline Selector
    st.markdown("Activity Timeline")
    
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
    
    fig_timeline = px.bar(
        agg_txns, 
        x='date', 
        y='amount', 
        color='type',
        color_discrete_map={'Credit': '#48bb78', 'Debit': '#e53e3e'},
        title=f"Transaction Flow ({txn_timeline})",
        barmode='group'
    )
    fig_timeline.update_layout(
        height=300,
        xaxis_title=None,
        yaxis_title="Amount (INR)",
        xaxis=dict(tickformat=date_format)
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("Transaction Details")
    st.dataframe(transactions[['date', 'transaction_id', 'type', 'amount', 'counterparty', 'description']], hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Regulatory Reporting")
    
    # SAR Type Selection
    st.markdown("#### Select SAR Type")
    sar_type_choice = st.radio(
        "Choose report type:",
        ["Internal SAR (Preliminary Investigation)", "Normal SAR (Regulatory Filing with FIU-IND)"],
        key=f"sar_type_radio_{customer_id}",
        help="Internal SAR: For internal compliance review. Normal SAR: Official filing with government authority."
    )
    
    # Display info based on selection
    if "Internal" in sar_type_choice:
        st.info("**Internal SAR** - This report will be reviewed by the compliance team before any regulatory action.")
    else:
        st.warning("**Regulatory SAR** - This report will be filed with FIU-IND. **DO NOT inform the customer (tipping off is illegal)**.")
    
    if st.button("Generate Suspicious Transaction Report (STR) ", key="gen_sar_btn", type="primary"):
        with st.spinner("Analyzing patterns and compiling STR..."):
            time.sleep(1.5)
            result = generator.generate(customer, transactions)
            st.session_state['generated_narrative'] = result['narrative_text']
            st.session_state['audit_trace'] = result['audit_trace']
            st.session_state['current_customer'] = customer
            
            # Set SAR type based on selection
            st.session_state['sar_type'] = "Internal" if "Internal" in sar_type_choice else "Normal"
            st.session_state['sar_status'] = "Draft"
            
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
    st.markdown("---")
    
    # Display SAR Type Badge
    sar_type = st.session_state.get('sar_type', 'Internal')
    if sar_type == "Internal":
        st.markdown("Internal SAR - Compliance Review")
    else:
        st.markdown("Normal SAR - Regulatory Filing")
        st.warning("**REGULATORY FILING** - Do not inform the customer (tipping off is illegal)")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### STR Draft Preview (FIU-IND Format)")
        narrative_input = st.text_area(
            "Review and Edit Report:",
            value=st.session_state['generated_narrative'],
            height=600
        )
        
    with c2:
        st.markdown("### Actions")
        
        # Save Draft with PDF Export (available for both types)
        if st.button("Save Draft as PDF", use_container_width=True, key="save_draft_pdf"):
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from io import BytesIO
            from datetime import datetime
            
            # Update session state
            st.session_state['generated_narrative'] = narrative_input
            
            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor='#000000',
                spaceAfter=30
            )
            story.append(Paragraph(f"Suspicious Transaction Report (STR) - {sar_type}", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Customer Details
            if st.session_state.get('current_customer'):
                customer = st.session_state['current_customer']
                story.append(Paragraph(f"<b>Customer Name:</b> {customer['name']}", styles['Normal']))
                story.append(Paragraph(f"<b>Customer ID:</b> {customer['customer_id']}", styles['Normal']))
                story.append(Paragraph(f"<b>Risk Rating:</b> {customer['risk_rating']}", styles['Normal']))
                story.append(Paragraph(f"<b>SAR Type:</b> {sar_type}", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Narrative
            story.append(Paragraph("<b>Narrative:</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            # Split narrative into paragraphs
            for para in narrative_input.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.replace('\n', '<br/>'), styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"<i>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            
            # Log action
            audit_logger.log_event(f"{sar_type} SAR Draft Saved", "Admin_User", {
                "customer_id": st.session_state['current_customer']['customer_id'],
                "sar_type": sar_type,
                "format": "PDF"
            })
            
            # Download button
            st.download_button(
                label="Download PDF",
                data=buffer,
                file_name=f"STR_{sar_type}_Draft_{st.session_state['current_customer']['customer_id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("Draft saved as PDF!")
        
        # Share SAR Button
        if st.button("Generate Share Link", use_container_width=True, key="share_sar"):
            import hashlib
            from datetime import datetime
            
            # Generate unique share ID based on customer ID and timestamp
            customer_id = st.session_state['current_customer']['customer_id']
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_string = f"{customer_id}_{timestamp}_{sar_type}"
            share_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
            
            # Generate shareable link (in production, this would be a real URL)
            base_url = "https://sar-system.example.com/shared"
            share_link = f"{base_url}/{share_id}"
            
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
            st.info("**Shareable Link:**")
            st.code(st.session_state['share_link'], language=None)
            st.caption("Copy this link to share the SAR report with authorized personnel.")

        
        st.markdown("---")
        
        # Conditional actions based on SAR type
        if sar_type == "Internal":
            # Internal SAR Actions
            st.markdown("#### Internal SAR Actions")
            
            if st.button("Escalate to Regulatory SAR", type="primary", use_container_width=True, key="escalate_sar"):
                st.session_state['sar_type'] = "Normal"
                st.session_state['sar_status'] = "Escalated"
                st.session_state['generated_narrative'] = narrative_input
                
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
            
            if st.button("File with FIU-IND", type="primary", use_container_width=True, key="file_fiu"):
                st.session_state['sar_status'] = "Filed"
                st.session_state['generated_narrative'] = narrative_input
                
                audit_logger.log_event("Normal SAR Filed with FIU-IND", "Admin_User", {
                    "customer_id": st.session_state['current_customer']['customer_id'],
                    "sar_type": "Normal",
                    "status": "Filed"
                })
                
                st.success("STR Filed Successfully with FIU-IND!")

def audit_page():
    st.title("Audit Logs")
    logs = audit_logger.get_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
        st.download_button("Download JSON", data=json.dumps(logs, indent=4), file_name="audit_log.json")
    else:
        st.info("No logs found.")

# --- Navigation ---
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", width=150) # Authority Logo
elif os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)
else:
    # Placeholder or nothing if image missing
    st.sidebar.markdown("Authority")
st.sidebar.markdown("<h1 style='font-size: 2.2rem; margin-bottom: 0;'>SAR Generator</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 1.1rem; color: #E0E0E0; margin-top: 5px;'>Advanced AML Monitoring System</p>", unsafe_allow_html=True)

def ai_assistant_page():
    st.title("AI Assistant")
    display_sar_editor()

# Initialize navigation state
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Admin Dashboard"

def update_nav():
    st.session_state["nav_selection"] = st.session_state["nav_radio"]

# Dynamic Sidebar Logic
if st.session_state["nav_selection"] == "AI Assistant":
    if st.sidebar.button("← Back to Dashboard"):
        st.session_state["nav_selection"] = "User Management" # Return to source or default
        st.rerun()
else:
    # Ensure current state is a valid radio option, else default to Admin Dashboard
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
