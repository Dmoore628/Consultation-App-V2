# Elite Consulting Group - Professional Multi-Agent System

## Overview

A sophisticated multi-agent consulting system that simulates an elite consulting firm with specialized AI agents collaborating to provide professional consulting services.

## Architecture

### Core Components

```
consulting_firm/
├── main.py                    # CLI entry point and conductor
├── professional_ui.py         # Streamlit web UI
├── expert_team.py             # Main team orchestration
├── agent_coordinator.py       # Multi-agent coordination system
├── model_client.py            # LLM integration (OpenAI/Ollama/Mock)
├── consulting_personas.py     # Professional agent personas
├── intake_flow.py             # Client intake workflow
├── validation_engine.py       # Deliverable validation
├── document_generator.py      # PDF/DOCX generation
├── exporter.py                # Export utilities
├── project_assessor.py        # Project maturity assessment
└── config.py                  # Configuration management
```

### Key Features

- **Multi-Agent Coordination**: Sophisticated agent-to-agent communication and peer review
- **Professional Personas**: Detailed consulting personas with domain expertise
- **Quality Gates**: Comprehensive validation and quality assurance
- **Multiple LLM Support**: OpenAI, Ollama, and Mock providers
- **Professional Deliverables**: Discovery reports, SOW, technical architecture, roadmaps
- **Web UI**: Clean Streamlit interface for client interactions

## Usage

### CLI Interface

```bash
# Run with mock provider (no LLM required)
python -m consulting_firm.main sample_project --provider mock

# Run with Ollama (local LLM)
python -m consulting_firm.main sample_project --provider ollama

# Run with OpenAI
python -m consulting_firm.main sample_project --provider openai

# Generate exports (PDF/DOCX)
python -m consulting_firm.main sample_project --provider mock --export
```

### Web UI

```bash
# Run Streamlit interface
streamlit run consulting_firm/professional_ui.py
```

## Agent Roles

The system includes specialized consulting agents:

- **Engagement Manager**: Client relationship and project orchestration
- **Product Strategist**: Business strategy and market analysis
- **Lead Analyst**: Requirements engineering and stakeholder analysis
- **Solutions Architect**: Technical architecture and system design
- **Project Manager**: Timeline planning and resource management
- **Quality Assurance**: Validation and deliverable excellence

## Multi-Agent Workflow

1. **Discovery Phase**: Collaborative information gathering with peer review
2. **Analysis Phase**: Cross-functional validation and critique
3. **Planning Phase**: Technical architecture and project planning
4. **Delivery Phase**: Professional document generation

## Configuration

Set environment variables for LLM configuration:

```bash
export MODEL_PROVIDER=ollama  # or openai, mock
export MODEL_NAME=llama3.2:1b
export MODEL_TEMPERATURE=0.2
export MODEL_MAX_TOKENS=1500
```

## Dependencies

Core dependencies:
- `streamlit` - Web UI
- `requests` - HTTP client
- `markdown` - Markdown processing
- `pathlib` - File path handling

Optional dependencies:
- `weasyprint` - PDF generation
- `python-docx` - DOCX generation
- `reportlab` - PDF fallback
- `graphviz` - Architecture diagrams

## Project Structure

```
project_folder/
├── project_documents/         # Input documents
│   └── consultation_notes.md   # Client consultation notes
└── outputs/                   # Generated deliverables
    ├── 01_discovery_report.md
    ├── 02_scope_of_work.md
    ├── 03_technical_architecture.md
    ├── 04_implementation_roadmap.md
    ├── validation_report.md
    └── final_deliverable.pdf
```

## Quality Assurance

The system includes comprehensive validation:
- Document completeness checks
- Professional standards validation
- Cross-artifact consistency
- Technical architecture validation
- Industry standards compliance

## Development

The system is designed to be:
- **Modular**: Clear separation of concerns
- **Scalable**: Easy to add new agents and capabilities
- **Maintainable**: Clean code with minimal redundancy
- **Testable**: Well-structured for unit and integration testing

## License

This project is part of the Elite Consulting Group system.