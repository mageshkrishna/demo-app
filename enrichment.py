import streamlit as st
from enrichment import EnrichmentService
from dataflow.dataflow import Dataflow
import traceback

# Initialize Dataflow SDK for secrets
dataflow = Dataflow()

# Page configuration
st.set_page_config(
    page_title="Company Enrichment Agent",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Company Enrichment Agent")
st.markdown("Generate comprehensive company enrichment reports with AI-powered analysis")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    project_type = st.selectbox(
        "Select Project Type",
        options=["Dataflow", "Digital Back Office", "Kiran Foundation"],
        help="Choose the project context for the enrichment report"
    )
    
    st.divider()
    st.markdown("### 📋 Project Descriptions")
    
    if project_type == "Dataflow":
        st.info("**Dataflow Platform**: Build, deploy, and manage complex data workflows")
    elif project_type == "Digital Back Office":
        st.info("**DBO Services**: AI transformation and data excellence")
    else:
        st.info("**Kiran Foundation**: Empowering talented students from under-resourced families")

# Main content area
st.subheader("🌐 Company Details")

company_url = st.text_input(
    "Company Website URL",
    placeholder="https://example.com",
    help="Enter the full company website URL"
)

generate_button = st.button(
    "🔍 Generate Report",
    type="primary",
    use_container_width=False
)

# Initialize session state
if 'report' not in st.session_state:
    st.session_state.report = None
if 'loading' not in st.session_state:
    st.session_state.loading = False

# Generate report
if generate_button:
    if not company_url:
        st.error("⚠️ Please enter a company website URL")
    else:
        # Validate URL
        if not company_url.startswith(('http://', 'https://')):
            company_url = 'https://' + company_url
        
        # Auto-detect company name from URL
        company_name = company_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Map project type to internal code
        project_mapping = {
            "Dataflow": "dataflow",
            "Digital Back Office": "dbo",
            "Kiran Foundation": "kiran"
        }
        project_code = project_mapping[project_type]
        
        st.session_state.loading = True
        st.session_state.company_name = company_name  # Store for later use
        
        with st.spinner(f"🔄 Enriching data for {company_name}... This may take 30-60 seconds"):
            try:
                # Get secrets from Dataflow - already returns dict
                secrets = dataflow.secret('streamlit_enrichment_app_cred')

                # Initialize enrichment service
                enrichment_service = EnrichmentService(secrets)
                
                # Generate report
                report = enrichment_service.enrich_company_data(
                    company_url=company_url,
                    company_name=company_name,
                    project_type=project_code
                )
                
                st.session_state.report = report
                st.session_state.loading = False
                st.success("✅ Report generated successfully!")
                
            except Exception as e:
                st.session_state.loading = False
                st.error(f"❌ Error generating report: {str(e)}")
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())

# Display report
if st.session_state.report:
    st.divider()
    st.subheader("📊 Enrichment Report")
    
    # Create tabs for Raw and Preview
    tab1, tab2 = st.tabs(["📝 Raw Markdown", "👁️ Preview"])
    
    with tab1:
        st.code(st.session_state.report, language="markdown")
    
    with tab2:
        st.markdown(st.session_state.report)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <small>Company Enrichment Agent | Powered by Jina AI, Hunter.io & Google Gemini</small>
    </div>
    """,
    unsafe_allow_html=True
)
