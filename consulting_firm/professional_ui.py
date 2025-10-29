"""
Professional Consulting System UI - Streamlined Implementation

This module provides a clean Streamlit UI that integrates with the main consulting system.
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Local imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intake_flow import ClientProfile
from main import run as run_conductor
from model_client import ModelClient
from consulting_personas import get_persona_prompt
from consultation_state import extract_structured_from_chat, ConsultationData


class ProfessionalConsultingUI:
    """Professional consulting system UI with proper flow management."""
    
    def __init__(self):
        self.client_profile: Optional[ClientProfile] = None
        self.engagement_started = False
        self.discovery_complete = False
        self.deliverables_generated = False
        self.project_path = "sample_project"
    
    def initialize_session_state(self):
        """Initialize Streamlit session state."""
        if 'client_profile' not in st.session_state:
            st.session_state.client_profile = None
        if 'engagement_started' not in st.session_state:
            st.session_state.engagement_started = False
        if 'discovery_complete' not in st.session_state:
            st.session_state.discovery_complete = False
        if 'deliverables_generated' not in st.session_state:
            st.session_state.deliverables_generated = False
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []  # list of dicts: {role: 'user'|'assistant', content: str}
        if 'general_notes' not in st.session_state:
            st.session_state.general_notes = ""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []  # list of saved file paths
        if 'discovery_status' not in st.session_state:
            st.session_state.discovery_status = {
                'complete': False,
                'missing_sections': [
                    'Features', 'Functional Requirements', 'Non-Functional Requirements',
                    'Expectations', 'Acceptance Criteria', 'Constraints',
                    'Deliverables', 'User Stories'
                ],
                'notes': ''
            }
        if 'auto_generate' not in st.session_state:
            st.session_state.auto_generate = True
    
    def render_main_interface(self):
        """Render the main professional consulting interface."""
        st.set_page_config(
            page_title="Elite Consulting Group - Professional System",
            page_icon="🏢",
            layout="wide"
        )
        
        # Header
        st.title("🏢 Elite Consulting Group")
        st.subheader("Professional Multi-Agent Consulting System")
        
        # Sidebar for system status
        with st.sidebar:
            self._render_system_status()
        
        # Main content
        if not st.session_state.engagement_started:
            self._render_intake_flow()
        else:
            self._render_consulting_interface()
    
    def _render_system_status(self):
        """Render system status in sidebar."""
        st.header("System Status")
        
        if st.session_state.client_profile:
            st.success("✅ Client Profile Loaded")
            st.info(f"**Client:** {st.session_state.client_profile.client_name}")
            st.info(f"**Project:** {st.session_state.client_profile.project_name}")
        else:
            st.warning("⚠️ No Client Profile")
        
        if st.session_state.deliverables_generated:
            st.success("✅ Deliverables Generated")
        else:
            # Discovery status summary
            ds = st.session_state.discovery_status
            if ds['complete']:
                st.success("✅ Discovery Complete (scope locked)")
            else:
                st.info("Discovery In Progress")
                if ds.get('missing_sections'):
                    st.caption("Missing: " + ", ".join(ds['missing_sections'][:6]))
            st.toggle("Auto-generate when complete", key='auto_generate', value=st.session_state.auto_generate)
    
    def _render_intake_flow(self):
        """Render the professional client intake flow."""
        st.header("Professional Client Intake")
        
        with st.form("professional_intake"):
            st.subheader("Client Information")
            
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("Client Name *", value="", help="Full name of the primary client contact")
                organization = st.text_input("Organization", value="", help="Client's organization or company")
            
            with col2:
                project_name = st.text_input("Project Name *", value="", help="Name of the project or initiative")
                industry = st.text_input("Industry", value="", help="Primary industry or sector")
            
            project_description = st.text_area(
                "Project Description *",
                height=120,
                placeholder="Provide a comprehensive description of your project goals, challenges, requirements, and expected outcomes...",
                help="Detailed description of the project scope and objectives"
            )
            
            # System Configuration
            st.subheader("System Configuration")
            col1, col2 = st.columns(2)
            with col1:
                llm_provider = st.selectbox(
                    "LLM Provider",
                    ["ollama", "openai", "mock"],
                    index=0,  # Default to ollama
                    help="Choose the language model provider"
                )
            with col2:
                if llm_provider == "openai":
                    model_options = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                    default_index = 0
                elif llm_provider == "ollama":
                    model_options = ["llama3.2:1b", "llama3.1:8b", "llama3.1:70b"]
                    default_index = 0
                else:
                    model_options = ["mock"]
                    default_index = 0
                
                model_name = st.selectbox(
                    "Model",
                    model_options,
                    index=default_index,
                    help="Choose the specific model"
                )
            
            submitted = st.form_submit_button("🚀 Start Professional Engagement", type="primary")
            
            if submitted:
                # Validate required fields
                if not client_name or not project_name or not project_description:
                    st.error("❌ Please fill in all required fields: Client Name, Project Name, and Project Description")
                    return
                
                try:
                    # Create client profile
                    client_profile = ClientProfile(
                        client_name=client_name,
                        organization=organization,
                        project_name=project_name,
                        project_description=project_description,
                        industry=industry
                    )
                    
                    # Set environment variables for model configuration
                    os.environ['MODEL_PROVIDER'] = llm_provider
                    os.environ['MODEL_NAME'] = model_name
                    
                    # Store in session state
                    st.session_state.client_profile = client_profile
                    st.session_state.engagement_started = True
                    
                    st.success("✅ Professional consulting engagement started successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to initialize system: {str(e)}")
    
    def _render_consulting_interface(self):
        """Render the main consulting interface."""
        if not st.session_state.client_profile:
            st.error("❌ System not initialized. Please restart the intake process.")
            return
        
        client_profile = st.session_state.client_profile
        
        # Show client information
        st.header("Consulting Engagement")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Project Overview")
            st.write(f"**Client:** {client_profile.client_name}")
            st.write(f"**Organization:** {client_profile.organization}")
            st.write(f"**Project:** {client_profile.project_name}")
            st.write(f"**Industry:** {client_profile.industry}")
            st.write(f"**Description:** {client_profile.project_description}")
        
        with col2:
            st.subheader("Actions")
            
            # Upload supporting documents (optional)
            st.caption("Optional: Upload any notes or reference documents")
            uploaded = st.file_uploader("Upload documents", type=["md","txt","pdf","docx"], accept_multiple_files=True)
            if uploaded:
                project_path = Path(self.project_path)
                docs_dir = project_path / "project_documents"
                project_path.mkdir(exist_ok=True)
                docs_dir.mkdir(exist_ok=True)
                for uf in uploaded:
                    save_path = docs_dir / uf.name
                    with open(save_path, 'wb') as f:
                        f.write(uf.getbuffer())
                    if str(save_path) not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(str(save_path))
                st.success(f"Uploaded {len(uploaded)} file(s)")
            
            # Generate deliverables button
            if not st.session_state.deliverables_generated:
                if st.button("📄 Confirm & Generate Deliverables", type="primary"):
                    try:
                        with st.spinner("Generating professional deliverables..."):
                            # Create project documents directory
                            project_path = Path(self.project_path)
                            project_path.mkdir(exist_ok=True)
                            docs_dir = project_path / "project_documents"
                            docs_dir.mkdir(exist_ok=True)
                            
                            # Write consultation notes (includes chat transcript and notes)
                            consultation_file = docs_dir / "consultation_notes.md"
                            with open(consultation_file, 'w', encoding='utf-8') as f:
                                f.write(f"# Consultation Notes\n\n")
                                f.write(f"## Client Information\n")
                                f.write(f"**Client:** {client_profile.client_name}\n")
                                f.write(f"**Organization:** {client_profile.organization}\n")
                                f.write(f"**Project:** {client_profile.project_name}\n")
                                f.write(f"**Industry:** {client_profile.industry}\n\n")
                                f.write(f"## Project Description\n")
                                f.write(f"{client_profile.project_description}\n\n")
                                f.write(f"## General Notes\n")
                                f.write(st.session_state.general_notes or "(none)\n")
                                f.write("\n\n")
                                # Structured section
                                if st.session_state.get('structured_md'):
                                    f.write("## Structured Consultation Summary\n")
                                    f.write(st.session_state.get('structured_md',''))
                                    f.write("\n\n")
                                f.write(f"## Chat Transcript\n")
                                for m in st.session_state.chat_messages:
                                    speaker = "Client" if m.get('role') == 'user' else "Consultant"
                                    f.write(f"- **{speaker}:** {m.get('content','').strip()}\n")
                                f.write("\n")
                                if st.session_state.uploaded_files:
                                    f.write("## Uploaded Files\n")
                                    for p in st.session_state.uploaded_files:
                                        f.write(f"- {p}\n")
                            
                            # Run the conductor
                            artifacts, validation_report = run_conductor(
                                str(project_path), 
                                "outputs", 
                                max_rounds=3, 
                                do_export=True,
                                log_callback=lambda msg: st.write(f"📋 {msg}")
                            )
                            
                            st.session_state.deliverables_generated = True
                            
                            # Display results
                            st.success("✅ Professional deliverables generated!")
                            
                            # Show generated files
                            st.subheader("Generated Deliverables")
                            for artifact_type, file_path in artifacts.items():
                                if os.path.exists(file_path):
                                    with st.expander(f"📋 {artifact_type.replace('_', ' ').title()}"):
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                        st.markdown(content)
                            
                            # Show validation report
                            if os.path.exists(validation_report):
                                with st.expander("📊 Validation Report"):
                                    with open(validation_report, 'r', encoding='utf-8') as f:
                                        validation_content = f.read()
                                    st.markdown(validation_content)
                            
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error generating deliverables: {str(e)}")
                        st.error("Please check the console for detailed error information.")
            else:
                st.success("✅ Deliverables already generated!")
                
                # Show generated files
                st.subheader("Generated Deliverables")
                outputs_dir = Path("outputs")
                if outputs_dir.exists():
                    for file_path in outputs_dir.glob("*.md"):
                        with st.expander(f"📋 {file_path.stem.replace('_', ' ').title()}"):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            st.markdown(content)

        # Auto-generate when discovery is complete
        if (
            st.session_state.discovery_status.get('complete')
            and not st.session_state.deliverables_generated
            and st.session_state.auto_generate
        ):
            st.info("Discovery complete and scope locked. Generating deliverables...")
            # Programmatically click the generate flow
            try:
                with st.spinner("Generating professional deliverables..."):
                    project_path = Path(self.project_path)
                    project_path.mkdir(exist_ok=True)
                    docs_dir = project_path / "project_documents"
                    docs_dir.mkdir(exist_ok=True)
                    consultation_file = docs_dir / "consultation_notes.md"
                    with open(consultation_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Consultation Notes\n\n")
                        f.write(f"## Client Information\n")
                        f.write(f"**Client:** {client_profile.client_name}\n")
                        f.write(f"**Organization:** {client_profile.organization}\n")
                        f.write(f"**Project:** {client_profile.project_name}\n")
                        f.write(f"**Industry:** {client_profile.industry}\n\n")
                        f.write(f"## Project Description\n")
                        f.write(f"{client_profile.project_description}\n\n")
                        f.write(f"## General Notes\n")
                        f.write(st.session_state.general_notes or "(none)\n")
                        f.write("\n\n")
                        f.write(f"## Chat Transcript\n")
                        for m in st.session_state.chat_messages:
                            speaker = "Client" if m.get('role') == 'user' else "Consultant"
                            f.write(f"- **{speaker}:** {m.get('content','').strip()}\n")
                        f.write("\n")
                        if st.session_state.uploaded_files:
                            f.write("## Uploaded Files\n")
                            for p in st.session_state.uploaded_files:
                                f.write(f"- {p}\n")
                    artifacts, validation_report = run_conductor(
                        str(project_path),
                        "outputs",
                        max_rounds=3,
                        do_export=True,
                        log_callback=lambda msg: st.write(f"📋 {msg}")
                    )
                    st.session_state.deliverables_generated = True
                    st.success("✅ Professional deliverables generated!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error generating deliverables: {str(e)}")
        
        # Collaborative Discovery Chat & Notes
        st.subheader("Real-Time Discovery Chat")
        left, right = st.columns([3, 2])
        with left:
            chat_container = st.container()
            with chat_container:
                if not st.session_state.chat_messages:
                    st.info("Start the conversation to capture discovery details. Your messages feed the consulting team.")
                for m in st.session_state.chat_messages[-50:]:
                    if m.get('role') == 'user':
                        st.chat_message("user").markdown(m.get('content',''))
                    else:
                        st.chat_message("assistant").markdown(m.get('content',''))
            user_input = st.chat_input("Share details, requirements, constraints, or ask questions...")
            if user_input:
                # Append user message
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                # Generate EM response using ModelClient
                try:
                    model = ModelClient()
                    persona = get_persona_prompt("engagement_manager")
                    # Build concise context from profile, notes, and last messages
                    recent = "\n".join([
                        ("Client: " + m['content']) if m['role'] == 'user' else ("Consultant: " + m['content'])
                        for m in st.session_state.chat_messages[-6:]
                    ])
                    context = f"Client: {client_profile.client_name}\nProject: {client_profile.project_name}\nIndustry: {client_profile.industry}\nDescription: {client_profile.project_description}\nNotes: {st.session_state.general_notes[:500]}\n\nRecent:\n{recent}"
                    prompt = f"Use the context to respond professionally and ask focused follow-ups.\n\n{context}\n\nUser said: {user_input}"
                    reply = model.generate("engagement_manager", prompt, system=persona)
                except Exception as e:
                    reply = "Thanks—I've captured that. Could you also share key objectives, users, and constraints?"
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})

                # Meta QA controller: assess completeness and scope creep
                try:
                    qa_persona = get_persona_prompt("quality_assurance")
                    # Instruct QA to decide completeness and list missing sections; include a clear COMPLETE flag
                    qa_prompt = (
                        "You are the Meta QA Controller ensuring discovery completeness and scope control.\n"
                        "Given the context (profile, notes, recent chat), assess whether discovery is COMPLETE.\n"
                        "If not complete, list MISSING_SECTIONS drawn from: Features; Functional Requirements; Non-Functional Requirements;"
                        " Expectations; Acceptance Criteria; Constraints; Deliverables; User Stories.\n"
                        "Also flag potential SCOPE_CREEP topics to defer.\n\n"
                        f"Context:\nClient: {client_profile.client_name}\nProject: {client_profile.project_name}\nIndustry: {client_profile.industry}\n"
                        f"Description: {client_profile.project_description}\nNotes: {st.session_state.general_notes[:1000]}\n\n"
                        "Recent Chat:\n" + "\n".join([
                            ("Client: " + m['content']) if m['role'] == 'user' else ("Consultant: " + m['content'])
                            for m in st.session_state.chat_messages[-12:]
                        ]) + "\n\n"
                        "Return this exact template:\n"
                        "COMPLETE: YES|NO\n"
                        "MISSING_SECTIONS: comma-separated list (or NONE)\n"
                        "SCOPE_CREEP: brief bullets (or NONE)\n"
                        "NEXT_QUESTION: one targeted question to progress toward completeness.\n"
                    )
                    qa_output = model.generate("quality_assurance", qa_prompt, system=qa_persona)
                    # Parse the simple template
                    complete = ('COMPLETE: YES' in qa_output.upper())
                    missing_line = ''
                    for line in qa_output.splitlines():
                        if line.strip().upper().startswith('MISSING_SECTIONS:'):
                            missing_line = line.split(':', 1)[1].strip()
                            break
                    missing_sections = [s.strip() for s in missing_line.split(',') if s.strip()] if missing_line else []
                    if missing_sections and missing_sections[0].upper() == 'NONE':
                        missing_sections = []
                    st.session_state.discovery_status = {
                        'complete': complete,
                        'missing_sections': missing_sections,
                        'notes': qa_output
                    }
                    # If not complete, append QA next question as assistant prompt
                    next_q = None
                    for line in qa_output.splitlines():
                        if line.strip().upper().startswith('NEXT_QUESTION:'):
                            next_q = line.split(':', 1)[1].strip()
                            break
                    if not complete and next_q:
                        st.session_state.chat_messages.append({"role": "assistant", "content": f"QA Check → {next_q}"})
                except Exception:
                    pass

                # Structured extraction: update normalized consultation data
                try:
                    profile_dict = {
                        'client_name': client_profile.client_name,
                        'project_name': client_profile.project_name,
                        'industry': client_profile.industry,
                        'project_description': client_profile.project_description,
                    }
                    structured: ConsultationData = extract_structured_from_chat(profile_dict, st.session_state.general_notes, st.session_state.chat_messages)
                    st.session_state['structured_md'] = structured.to_markdown()
                except Exception:
                    st.session_state['structured_md'] = st.session_state.get('structured_md', '')
                st.rerun()
        with right:
            st.subheader("General Notes")
            st.session_state.general_notes = st.text_area(
                "Capture any general notes that should be included in the SOW",
                value=st.session_state.general_notes,
                height=200
            )
            st.subheader("Structured Summary (Live)")
            st.markdown(st.session_state.get('structured_md', '(Will appear as you chat)'))
        
        # Session management
        st.subheader("Session Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 New Session"):
                # Reset session state
                for key in ['client_profile', 'engagement_started', 'discovery_complete', 'deliverables_generated', 'chat_messages', 'general_notes', 'uploaded_files']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("📊 System Info"):
                st.json({
                    "client_profile": st.session_state.client_profile.__dict__ if st.session_state.client_profile else None,
                    "engagement_started": st.session_state.engagement_started,
                    "deliverables_generated": st.session_state.deliverables_generated,
                    "project_path": self.project_path
                })


def main():
    """Main function to run the professional consulting system."""
    ui = ProfessionalConsultingUI()
    ui.initialize_session_state()
    ui.render_main_interface()


if __name__ == "__main__":
    main()