"""
Elite Consulting Group - Professional Client Engagement Platform

A modular, industry-standard consulting firm interface following best practices:
- Structured intake process
- Client profile management  
- Specialist team assembly
- Discovery-driven conversation
- Professional deliverable generation
"""

import os
from pathlib import Path
import streamlit as st
import datetime

# Import modular components
from consulting_firm.intake_flow import (
    IntakeStage, ClientProfile, IntakeWorkflow, create_intake_form_data
)
from consulting_firm.conversation_manager import (
    ConversationContext, ConversationOrchestrator, ConversationMessage
)
from consulting_firm.domain_detector import DomainDetector, ProjectDomain
from consulting_firm.team_assembler import TeamAssembler
from consulting_firm.model_client import ModelClient
from consulting_firm.main import run as run_conductor
from consulting_firm import config as cfg

# Constants
APP_TITLE = "Elite Consulting Group"
APP_SUBTITLE = "Professional Strategy & Implementation Services"


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        # Intake workflow
        'intake_stage': IntakeStage.WELCOME,
        'client_profile': ClientProfile(),
        'engagement_started': False,
        
        # Conversation
        'conversation_context': None,
        'project_domain': None,
        'specialist_team': [],
        
        # Generation
        'generation_done': False,
        'activity_log': [],
        'generation_transcript': ""
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def ensure_directories(project_path: str) -> Path:
    """Ensure project directories exist."""
    project_dir = Path(project_path)
    project_dir.mkdir(parents=True, exist_ok=True)
    
    docs_dir = project_dir / 'project_documents'
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    outputs_dir = Path(cfg.OUTPUT_PATH)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    return docs_dir


def save_uploaded_files(uploaded_files, docs_dir: Path) -> list[str]:
    """Save uploaded files to project documents directory."""
    saved_files = []
    for uploaded_file in uploaded_files or []:
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in {'.md', '.txt', '.pdf', '.docx'}:
            st.warning(f"⚠️ Skipping unsupported file type: {uploaded_file.name}")
            continue
        
        file_path = docs_dir / uploaded_file.name
        file_path.write_bytes(uploaded_file.getbuffer())
        saved_files.append(uploaded_file.name)
    
    return saved_files


def render_intake_stage(stage: IntakeStage, model: ModelClient, docs_dir: Path):
    """Render UI for current intake stage."""
    stage_info = IntakeWorkflow.get_stage_description(stage)
    
    st.markdown(f"### {stage_info['title']}")
    st.caption(stage_info['subtitle'])
    st.info(f"ℹ️ {stage_info['instruction']}")
    st.markdown("---")
    
    if stage == IntakeStage.WELCOME:
        render_welcome_stage()
    
    elif stage == IntakeStage.CLIENT_INFO:
        render_client_info_stage()
    
    elif stage == IntakeStage.PROJECT_OVERVIEW:
        render_project_overview_stage()
    
    elif stage == IntakeStage.DOCUMENT_UPLOAD:
        render_document_upload_stage(docs_dir)
    
    elif stage == IntakeStage.ENGAGEMENT_CONFIRMED:
        render_engagement_confirmed_stage(model, docs_dir)


def render_welcome_stage():
    """Render welcome/intro stage."""
    st.markdown("""
    **Welcome to Elite Consulting Group** — Where domain expertise meets professional execution.
    
    We provide comprehensive consulting services including:
    - ✅ Business strategy and feasibility analysis
    - ✅ Technical architecture and implementation planning
    - ✅ Risk assessment and project roadmapping
    - ✅ Professional deliverables ready for stakeholders
    
    Our process is structured, efficient, and tailored to your domain:
    1. **Intake** — We'll gather essential information (2 minutes)
    2. **Discovery** — Brief conversation to understand your vision (5-10 minutes)
    3. **Generation** — Our specialist team produces comprehensive deliverables
    
    **You're the domain expert. We provide the structure and execution.**
    """)
    
    if st.button("🚀 Begin Engagement", type="primary", use_container_width=True):
        st.session_state.intake_stage = IntakeStage.CLIENT_INFO
        st.rerun()


def render_client_info_stage():
    """Render client information form."""
    form_data = create_intake_form_data()[IntakeStage.CLIENT_INFO]
    
    with st.form("client_info_form"):
        form_values = {}
        
        for field in form_data:
            if field['type'] == 'text':
                form_values[field['key']] = st.text_input(
                    field['label'],
                    value=getattr(st.session_state.client_profile, field['key'], ""),
                    placeholder=field.get('placeholder', ""),
                    help=field.get('help', "")
                )
        
        col1, col2 = st.columns([1, 1])
        with col2:
            submitted = st.form_submit_button("Continue →", type="primary", use_container_width=True)
        
        if submitted:
            # Validate
            valid = True
            for field in form_data:
                if field['required'] and not form_values.get(field['key']):
                    st.error(f"❌ {field['label']} is required")
                    valid = False
            
            if valid:
                # Update profile
                for key, value in form_values.items():
                    setattr(st.session_state.client_profile, key, value)
                
                # Move to next stage
                st.session_state.intake_stage = IntakeStage.PROJECT_OVERVIEW
                st.rerun()


def render_project_overview_stage():
    """Render project overview form."""
    form_data = create_intake_form_data()[IntakeStage.PROJECT_OVERVIEW]
    
    with st.form("project_overview_form"):
        form_values = {}
        
        for field in form_data:
            if field['type'] == 'text':
                form_values[field['key']] = st.text_input(
                    field['label'],
                    value=getattr(st.session_state.client_profile, field['key'], ""),
                    placeholder=field.get('placeholder', ""),
                    help=field.get('help', "")
                )
            elif field['type'] == 'select':
                current_value = getattr(st.session_state.client_profile, field['key'], "")
                form_values[field['key']] = st.selectbox(
                    field['label'],
                    options=field['options'],
                    index=field['options'].index(current_value) if current_value in field['options'] else 0,
                    help=field.get('help', "")
                )
            elif field['type'] == 'textarea':
                form_values[field['key']] = st.text_area(
                    field['label'],
                    value=getattr(st.session_state.client_profile, field['key'], ""),
                    placeholder=field.get('placeholder', ""),
                    help=field.get('help', ""),
                    height=100
                )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            back = st.form_submit_button("← Back", use_container_width=True)
        with col2:
            submitted = st.form_submit_button("Continue →", type="primary", use_container_width=True)
        
        if back:
            st.session_state.intake_stage = IntakeStage.CLIENT_INFO
            st.rerun()
        
        if submitted:
            # Validate required fields
            valid = True
            for field in form_data:
                if field['required'] and not form_values.get(field['key']):
                    st.error(f"❌ {field['label']} is required")
                    valid = False
            
            if valid:
                # Update profile
                for key, value in form_values.items():
                    setattr(st.session_state.client_profile, key, value)
                
                # Move to document upload
                st.session_state.intake_stage = IntakeStage.DOCUMENT_UPLOAD
                st.rerun()


def render_document_upload_stage(docs_dir: Path):
    """Render document upload stage."""
    st.markdown("""
    Do you have any existing project documents? These are **optional** but can help us provide better insights.
    
    **Helpful documents include:**
    - Requirements or specifications
    - Architecture diagrams or technical docs
    - Business plans or strategy documents
    - Meeting notes or stakeholder feedback
    - Any relevant research or analysis
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Documents (Optional)",
        accept_multiple_files=True,
        type=['md', 'txt', 'pdf', 'docx'],
        help="Supported formats: PDF, DOCX, Markdown, TXT"
    )
    
    # Show currently uploaded files
    if st.session_state.client_profile.uploaded_files:
        st.success(f"✅ {len(st.session_state.client_profile.uploaded_files)} file(s) uploaded:")
        for fname in st.session_state.client_profile.uploaded_files:
            st.caption(f"• {fname}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.intake_stage = IntakeStage.PROJECT_OVERVIEW
            st.rerun()
    
    with col2:
        if st.button("Skip", use_container_width=True):
            st.session_state.client_profile.has_existing_docs = False
            st.session_state.intake_stage = IntakeStage.ENGAGEMENT_CONFIRMED
            st.rerun()
    
    with col3:
        if st.button("Continue →", type="primary", use_container_width=True, disabled=not uploaded_files):
            if uploaded_files:
                # Save files
                saved = save_uploaded_files(uploaded_files, docs_dir)
                st.session_state.client_profile.uploaded_files = saved
                st.session_state.client_profile.has_existing_docs = True
            
            st.session_state.intake_stage = IntakeStage.ENGAGEMENT_CONFIRMED
            st.rerun()


def render_engagement_confirmed_stage(model: ModelClient, docs_dir: Path):
    """Render engagement confirmation and start discovery."""
    st.success("✅ **Intake Complete** — Your engagement is confirmed!")
    
    # Detect domain
    if not st.session_state.project_domain:
        profile = st.session_state.client_profile
        doc_context = " ".join(profile.uploaded_files) if profile.uploaded_files else ""
        
        st.session_state.project_domain = DomainDetector.detect(
            user_input=profile.project_description,
            document_context=doc_context,
            industry_hint=profile.industry
        )
    
    # Assemble team
    if not st.session_state.specialist_team:
        st.session_state.specialist_team = TeamAssembler.assemble_team(
            st.session_state.project_domain
        )
    
    # Show team
    st.markdown("#### 👥 Your Specialist Team")
    for specialist in st.session_state.specialist_team:
        st.caption(f"**{specialist['name']}**, {specialist['title']} — {specialist['expertise']}")
    
    st.markdown("---")
    st.info("Click **'Begin Discovery'** to start your consultation session.")
    
    if st.button("🎯 Begin Discovery", type="primary", use_container_width=True):
        # Initialize conversation context
        st.session_state.conversation_context = ConversationContext(
            st.session_state.client_profile
        )
        
        # Generate opening statement from Engagement Manager
        orchestrator = ConversationOrchestrator(model)
        team_intro = TeamAssembler.format_team_introduction(
            st.session_state.project_domain,
            st.session_state.client_profile.client_name
        )
        
        opening = orchestrator.generate_opening_statement(
            st.session_state.client_profile,
            team_intro,
            document_summary=f"{len(st.session_state.client_profile.uploaded_files)} documents provided" if st.session_state.client_profile.uploaded_files else None
        )
        
        st.session_state.conversation_context.add_message(
            'assistant',
            opening,
            speaker='Jennifer Martinez (Engagement Manager)'
        )
        
        st.session_state.engagement_started = True
        st.rerun()


def render_discovery_conversation(model: ModelClient):
    """Render discovery conversation interface."""
    context: ConversationContext = st.session_state.conversation_context
    orchestrator = ConversationOrchestrator(model)
    
    col_left, col_right = st.columns([7, 3])
    
    with col_left:
        st.subheader("💬 Discovery Session")
        
        # Display conversation
        for msg in context.messages:
            avatar = "🏢" if msg.role == 'assistant' else "👤"
            with st.chat_message(msg.role, avatar=avatar):
                if msg.speaker:
                    st.caption(f"**{msg.speaker}**")
                st.markdown(msg.content)
        
        # Chat input
        if user_input := st.chat_input(f"Share your thoughts, {context.client_profile.client_name}..."):
            # Add user message
            context.add_message('user', user_input)
            
            # Generate AI response
            response, speaker = orchestrator.generate_discovery_question(context)
            context.add_message('assistant', response, speaker=speaker)
            
            st.rerun()
    
    with col_right:
        st.subheader("📊 Progress")
        
        # Show project info
        st.markdown("##### 📋 Project")
        st.caption(f"**{context.client_profile.project_name}**")
        st.caption(f"Client: {context.client_profile.client_name}")
        st.markdown("---")
        
        # Show team
        st.markdown("##### 👥 Your Team")
        for specialist in st.session_state.specialist_team[:5]:  # Show top 5
            st.caption(f"**{specialist['name']}**")
        if len(st.session_state.specialist_team) > 5:
            st.caption(f"... +{len(st.session_state.specialist_team) - 5} more")
        st.markdown("---")
        
        # Discovery status
        st.markdown("##### ✅ Discovery Areas")
        status_labels = {
            'goals': 'Business Objectives',
            'users': 'Target Users',
            'features': 'Key Capabilities',
            'tech_stack': 'Technical Approach',
            'timeline': 'Timeline & Resources'
        }
        
        for key, label in status_labels.items():
            icon = "✓" if context.discovery_status[key] else "○"
            st.caption(f"{icon} {label}")
        
        completed = sum(context.discovery_status.values())
        progress = completed / len(context.discovery_status)
        st.progress(progress)
        st.caption(f"{completed}/5 areas covered")
        st.markdown("---")
        
        # Generate button
        ready = context.is_sufficient_for_generation()
        
        if ready and not st.session_state.generation_done:
            st.success("✅ Ready to generate!")
        elif st.session_state.generation_done:
            st.info("✓ Generation complete")
        else:
            st.warning(f"⏳ {5 - completed} more areas needed")
        
        if st.button(
            "🚀 Generate Deliverables",
            disabled=not ready or st.session_state.generation_done,
            type="primary",
            use_container_width=True
        ):
            run_generation(context, model)


def run_generation(context: ConversationContext, model: ModelClient):
    """Execute deliverable generation."""
    # Save consultation notes
    profile = context.client_profile
    project_path = f"projects/{profile.client_name.replace(' ', '_')}_{profile.project_name.replace(' ', '_')}"
    docs_dir = ensure_directories(project_path)
    
    notes_path = docs_dir / 'consultation_notes.md'
    with notes_path.open('w', encoding='utf-8') as f:
        f.write(f"# Consultation Notes\n\n")
        f.write(f"## Client Profile\n{profile.to_context_string()}\n\n")
        f.write(f"## Discovery Conversation\n\n")
        for msg in context.messages:
            speaker = msg.speaker if msg.speaker else msg.role.upper()
            f.write(f"**{speaker}**: {msg.content}\n\n")
    
    # Create progress container
    progress_container = st.empty()
    
    def ui_log(message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        st.session_state.activity_log.append(log_entry)
        st.session_state.generation_transcript += f"{log_entry}\n"
        
        with progress_container.container():
            st.markdown("#### 🔄 Generation Progress")
            for entry in st.session_state.activity_log[-10:]:
                st.text(entry)
    
    # Run generation
    try:
        with st.spinner("Generating deliverables..."):
            artifacts, validation = run_conductor(
                project_path,
                cfg.OUTPUT_PATH,
                max_rounds=3,
                do_export=True,
                log_callback=ui_log
            )
        
        st.session_state.generation_done = True
        st.success("✅ Generation complete!")
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Generation failed: {e}")
        ui_log(f"ERROR: {e}")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏢",
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    
    # Initialize
    init_session_state()
    
    # Header
    st.title(f"🏢 {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.markdown("---")
    
    # Get model client
    provider = os.environ.get('MODEL_PROVIDER', 'ollama')
    model = ModelClient(provider)
    
    # Ensure directories
    project_path = "RLFuturesSystemDocs"  # Default, will be personalized after intake
    docs_dir = ensure_directories(project_path)
    
    # Route to appropriate view
    if not st.session_state.engagement_started:
        # Intake flow
        render_intake_stage(st.session_state.intake_stage, model, docs_dir)
    else:
        # Discovery conversation
        render_discovery_conversation(model)
    
    # Footer
    st.markdown("---")
    st.caption("🏢 Elite Consulting Group — Professional consulting services powered by specialized AI experts")


if __name__ == "__main__":
    main()
