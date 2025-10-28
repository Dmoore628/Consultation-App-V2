import os
from pathlib import Path
import streamlit as st
import datetime

# Import our conductor and config
from consulting_firm.main import run as run_conductor
from consulting_firm import config as cfg
from consulting_firm.model_client import ModelClient

APP_TITLE = "AI Consulting Firm — Discovery & Scoping"


def ensure_dirs(project_path: str, outputs_path: str):
    Path(project_path).mkdir(parents=True, exist_ok=True)
    docs_dir = Path(project_path) / 'project_documents'
    docs_dir.mkdir(parents=True, exist_ok=True)
    Path(outputs_path).mkdir(parents=True, exist_ok=True)
    return docs_dir


def save_uploaded_files(uploaded_files, docs_dir: Path):
    saved = []
    for uf in uploaded_files or []:
        suffix = Path(uf.name).suffix.lower()
        if suffix not in {'.md', '.txt', '.pdf', '.docx'}:
            st.warning(f"Skipping unsupported file type: {uf.name}")
            continue
        out_path = docs_dir / uf.name
        out_path.write_bytes(uf.getbuffer())
        saved.append(str(out_path))
    return saved


def write_consultation_notes(project_path: str, messages: list[dict]):
    """Save conversation messages to consultation_notes.md"""
    docs_dir = ensure_dirs(project_path, cfg.OUTPUT_PATH)
    notes_path = Path(project_path) / 'project_documents' / 'consultation_notes.md'
    with notes_path.open('w', encoding='utf-8') as f:
        f.write('# Consultation Notes\n\n')
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            f.write(f"**{role}**: {content}\n\n")
    return str(notes_path)


def analyze_uploaded_files(docs_dir: Path) -> str:
    """Analyze uploaded files and return a summary."""
    files = list(docs_dir.glob('*'))
    docs = [f for f in files if f.suffix.lower() in {'.md', '.txt', '.pdf', '.docx'}]
    if not docs:
        return ""
    
    summary_parts = ["I've analyzed your uploaded documents:"]
    for f in docs:
        size_kb = f.stat().st_size / 1024
        summary_parts.append(f"• {f.name} ({size_kb:.1f} KB)")
    
    summary_parts.append("\nLet me ask a few questions to validate and enhance these:")
    return "\n".join(summary_parts)


def check_context_sufficiency(messages: list[dict]) -> tuple[bool, dict[str, bool]]:
    """Determine if we have enough context to generate outputs.
    
    Returns: (is_sufficient, status_dict)
    """
    # Combine all user messages
    user_text = " ".join([m['content'].lower() for m in messages if m['role'] == 'user'])
    
    checks = {
        'goals': ['goal', 'objective', 'purpose', 'mission', 'problem', 'solve', 'need', 'want'],
        'users': ['user', 'customer', 'stakeholder', 'audience', 'who', 'persona', 'target'],
        'features': ['feature', 'functionality', 'capability', 'mvp', 'deliver', 'scope', 'requirement'],
        'tech_stack': ['technology', 'stack', 'platform', 'framework', 'language', 'database', 'infrastructure', 'architecture'],
        'timeline': ['timeline', 'deadline', 'schedule', 'month', 'week', 'launch', 'phase', 'milestone'],
    }
    
    status = {}
    for key, keywords in checks.items():
        status[key] = any(kw in user_text for kw in keywords)
    
    is_sufficient = sum(status.values()) >= 3  # At least 3 of 5 areas covered
    return (is_sufficient, status)


def generate_initial_response(user_input: str, has_files: bool, model: ModelClient) -> str:
    """AI generates context-aware initial response after user's first input."""
    
    if has_files:
        prompt = f"""The user has uploaded documents and said: "{user_input}"

Generate a professional, consultant-like response that:
1. Acknowledges their input and uploaded documents
2. Shows you've understood their project context
3. Asks 2-3 targeted questions to validate and enhance the uploaded information
4. Focuses on gaps like: architecture decisions, timeline accuracy, new requirements, success metrics

Be conversational, not robotic. Maximum 4 sentences."""
    else:
        prompt = f"""The user described their project: "{user_input}"

Generate a professional, consultant-like response that:
1. Acknowledges their project idea with enthusiasm
2. Shows you understand the core concept
3. Asks 2-4 targeted questions to gather essential details
4. Focus on: target users, key features, tech preferences, timeline, budget

Be conversational and engaging. Maximum 4 sentences."""
    
    response = model.generate("analyst", prompt)
    return response.strip()


def generate_followup_question(messages: list[dict], status: dict[str, bool], model: ModelClient) -> str:
    """AI generates a targeted follow-up question based on what's missing."""
    
    context = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-6:]])
    
    missing = [k.replace('_', ' ') for k, v in status.items() if not v]
    
    if not missing:
        return "✅ Great! I have enough information to generate your deliverables. Click **'Generate Deliverables'** when ready."
    
    missing_str = ", ".join(missing)
    
    prompt = f"""Based on this conversation:
{context}

The following areas need more detail: {missing_str}.

Ask ONE specific, natural follow-up question to gather this information. 
Be conversational like a real consultant. Keep it brief (1-2 sentences)."""
    
    question = model.generate("analyst", prompt)
    return question.strip()


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'context_sufficient' not in st.session_state:
    st.session_state.context_sufficient = False
if 'discovery_status' not in st.session_state:
    st.session_state.discovery_status = {
        'goals': False,
        'users': False,
        'features': False,
        'tech_stack': False,
        'timeline': False
    }
if 'generation_done' not in st.session_state:
    st.session_state.generation_done = False
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'generation_transcript' not in st.session_state:
    st.session_state.generation_transcript = ""
if 'uploaded_files_list' not in st.session_state:
    st.session_state.uploaded_files_list = []

st.set_page_config(page_title=APP_TITLE, layout='wide')
st.title(APP_TITLE)

# Use default settings
project_path = str(Path('RLFuturesSystemDocs').resolve())
outputs_path = str(Path('outputs').resolve())
provider = os.environ.get('MODEL_PROVIDER', 'ollama')
model_name = os.environ.get('MODEL_NAME', 'llama3.1:8b')
rounds = 3
do_export = True

# Hidden settings panel (collapsible)
with st.expander("⚙️ Advanced Settings", expanded=False):
    project_path = st.text_input("Project path", value=project_path)
    outputs_path = st.text_input("Outputs path", value=outputs_path)
    
    provider = st.selectbox("Model provider", options=['mock', 'ollama', 'openai'], index=1)
    model_name = st.text_input("Model name", value=model_name)
    rounds = st.number_input("Max refinement rounds", min_value=1, max_value=10, value=rounds, step=1)
    do_export = st.checkbox("Generate exports (PDF/DOCX & diagram)", value=do_export)
    
    if st.button("🔄 Start Fresh Session"):
        st.session_state.messages = []
        st.session_state.context_sufficient = False
        st.session_state.discovery_status = {k: False for k in st.session_state.discovery_status}
        st.session_state.generation_done = False
        st.session_state.activity_log = []
        st.session_state.generation_transcript = ""
        st.session_state.uploaded_files_list = []
        st.rerun()

os.environ['MODEL_PROVIDER'] = provider
os.environ['MODEL_NAME'] = model_name

# File upload section (compact, before main panels)
st.caption("📎 Upload project documents (optional - PDFs, DOCX, MD, TXT)")
docs_dir = ensure_dirs(project_path, outputs_path)
uploaded = st.file_uploader("Upload files", accept_multiple_files=True, type=['md', 'txt', 'pdf', 'docx'], label_visibility="collapsed")
if uploaded:
    saved = save_uploaded_files(uploaded, docs_dir)
    if saved:
        st.session_state.uploaded_files_list = [Path(f).name for f in saved]

st.markdown("---")

# Main area: Split panel (70% left, 30% right)
col_left, col_right = st.columns([7, 3])

with col_left:
    st.subheader("💬 Conversation & Discovery")
    
    # Empty state welcome message
    if not st.session_state.messages:
        st.info("""👋 **Welcome to your AI consulting firm!**
        
I'll guide you through a professional discovery process. You can:
- Describe your project in your own words
- Upload existing documents (architecture, SOW, requirements)
- Answer my targeted questions

I'll ask smart follow-up questions to ensure we capture everything needed for comprehensive deliverables.""")
    
    # Display conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
    
    # Chat input
    if user_input := st.chat_input("Describe your project or answer questions..."):
        # Check if this is the first message
        is_first_message = len(st.session_state.messages) == 0
        has_files = len(list(docs_dir.glob('*'))) > 0
        
        # Add user message
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        # Generate AI response
        model = ModelClient(provider)
        
        if is_first_message:
            # Initial context-aware response
            if has_files:
                file_summary = analyze_uploaded_files(docs_dir)
                ai_response = f"{file_summary}\n\n" + generate_initial_response(user_input, True, model)
            else:
                ai_response = generate_initial_response(user_input, False, model)
        else:
            # Check context sufficiency
            sufficient, status = check_context_sufficiency(st.session_state.messages)
            st.session_state.context_sufficient = sufficient
            st.session_state.discovery_status = status
            
            # Generate follow-up
            ai_response = generate_followup_question(st.session_state.messages, status, model)
        
        st.session_state.messages.append({'role': 'assistant', 'content': ai_response})
        st.rerun()

with col_right:
    st.subheader("📊 Status & Controls")
    
    # Uploaded files section
    if st.session_state.uploaded_files_list or len(list(docs_dir.glob('*'))) > 0:
        with st.container():
            st.markdown("##### 🗂️ Uploaded Files")
            existing_files = [f.name for f in docs_dir.glob('*') if f.suffix.lower() in {'.md', '.txt', '.pdf', '.docx'}]
            for fname in existing_files:
                st.caption(f"✓ {fname}")
            st.markdown("---")
    
    # Discovery status tracker
    with st.container():
        st.markdown("##### 📋 Discovery Status")
        status_labels = {
            'goals': 'Project Goals',
            'users': 'Target Users',
            'features': 'Key Features',
            'tech_stack': 'Tech Stack',
            'timeline': 'Timeline'
        }
        
        for key, label in status_labels.items():
            status = st.session_state.discovery_status.get(key, False)
            icon = "✓" if status else "□"
            color = "green" if status else "gray"
            st.markdown(f":{color}[{icon}] {label}")
        
        completed = sum(st.session_state.discovery_status.values())
        progress = completed / len(st.session_state.discovery_status)
        st.progress(progress)
        st.caption(f"{completed} of {len(st.session_state.discovery_status)} areas covered")
        st.markdown("---")
    
    # Generate button (enabled only when context is sufficient)
    generate_disabled = not st.session_state.context_sufficient or st.session_state.generation_done
    
    if st.session_state.context_sufficient and not st.session_state.generation_done:
        st.success("✅ Ready to generate!")
    elif st.session_state.generation_done:
        st.info("✓ Generation complete")
    else:
        st.warning("⏳ Continue conversation...")
    
    if st.button("🚀 Generate Deliverables", disabled=generate_disabled, type="primary", use_container_width=True):
        # Save notes
        notes_path = write_consultation_notes(project_path, st.session_state.messages)
        
        # Clear previous activity log
        st.session_state.activity_log = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.generation_transcript = f"# Generation Transcript\n\nStarted: {timestamp}\n\n"
        
        # Create log container
        log_container = st.empty()
        
        # Callback to update activity log in real-time
        def ui_log(message: str):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            st.session_state.activity_log.append(log_entry)
            st.session_state.generation_transcript += f"{log_entry}\n"
            
            # Update the log display
            with log_container.container():
                st.markdown("#### 🔄 Generation Progress")
                for entry in st.session_state.activity_log[-15:]:  # Show last 15 entries
                    st.text(entry)
        
        # Run conductor with logging
        try:
            with st.spinner("Generating deliverables..."):
                artifacts, validation_report = run_conductor(
                    project_path, 
                    outputs_path, 
                    max_rounds=int(rounds), 
                    do_export=do_export,
                    log_callback=ui_log
                )
            st.session_state.generation_done = True
            
            # Save transcript
            transcript_path = Path(outputs_path) / 'generation_transcript.md'
            transcript_path.write_text(st.session_state.generation_transcript, encoding='utf-8')
            
            st.success("✅ Generation complete! Scroll down to download outputs.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Generation failed: {e}")
            ui_log(f"❌ ERROR: {e}")
    
    # Show activity log if generation is in progress or complete
    if st.session_state.activity_log:
        st.markdown("---")
        with st.expander("📜 Activity Log", expanded=True):
            for entry in st.session_state.activity_log[-20:]:
                st.text(entry)

# Deliverables section (full width, below conversation)
if st.session_state.generation_done:
    st.markdown("---")
    st.subheader("📦 Your Deliverables")
    
    outputs_dir = Path(outputs_path)
    expected = [
        ('📄 Discovery Report', outputs_dir / '01_discovery_report.md'),
        ('📋 Scope of Work', outputs_dir / '02_scope_of_work.md'),
        ('🏗️ Technical Architecture', outputs_dir / '03_technical_architecture.md'),
        ('🗺️ Implementation Roadmap', outputs_dir / '04_implementation_roadmap.md'),
        ('⚠️ Validation Report', outputs_dir / 'validation_report.md'),
        ('📊 Architecture Diagram', outputs_dir / 'architecture.png'),
        ('📦 Combined DOCX', outputs_dir / 'final_deliverable.docx'),
        ('📑 Combined PDF', outputs_dir / 'final_deliverable.pdf'),
        ('📜 Generation Transcript', outputs_dir / 'generation_transcript.md'),
    ]
    
    available = [(label, path) for label, path in expected if path.exists()]
    
    if not available:
        st.warning("⚠️ Generation completed but no outputs found. Check the activity log for errors.")
    else:
        # Show validation report inline
        validation_path = outputs_dir / 'validation_report.md'
        if validation_path.exists():
            with st.expander("⚠️ View Validation Report", expanded=False):
                st.markdown(validation_path.read_text(encoding='utf-8'))
        
        # Download buttons in columns
        cols = st.columns(3)
        for idx, (label, path) in enumerate(available):
            col = cols[idx % 3]
            with col:
                st.write(f"**{label}**")
                try:
                    data = path.read_bytes()
                    mime = 'application/octet-stream'
                    if path.suffix == '.md':
                        mime = 'text/markdown'
                    elif path.suffix == '.pdf':
                        mime = 'application/pdf'
                    elif path.suffix == '.docx':
                        mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    elif path.suffix == '.png':
                        mime = 'image/png'
                    st.download_button(
                        "⬇️ Download", 
                        data=data, 
                        file_name=path.name, 
                        mime=mime,
                        key=f"download_{path.name}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.caption(f"⚠️ Could not load file: {e}")

st.markdown("---")
st.caption("💡 **Tip**: Using Ollama (local, free) for AI generation. Expand Advanced Settings to change providers.")
