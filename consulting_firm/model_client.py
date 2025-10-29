"""Simple pluggable model client supporting mock/openai/ollama calls.

This file implements a minimal abstraction to allow role-specific prompts
in `expert_team.py`. It avoids hard failures when cloud clients aren't
installed by providing a deterministic mock provider.
"""
from typing import Optional, Dict
import json
import os
import requests
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


ROLE_PROMPTS: Dict[str, str] = {
    # Business and strategy
    "strategist": """You are an expert Product Strategist at an elite consulting firm.
Analyze business viability, ROI, market positioning, and strategic alignment.
Focus on: business case, competitive advantages, market opportunity, success metrics, and value proposition.
Provide executive-level insights with concrete, measurable recommendations.
Always tie recommendations to business outcomes (revenue, market share, customer satisfaction).""",

    "analyst": """You are a Lead Business Analyst specializing in requirements engineering.
Gather comprehensive requirements, map stakeholders, identify gaps and risks.
Provide: detailed requirements with SMART acceptance criteria, stakeholder analysis, user stories, process flows.
Ensure all requirements are traceable to business goals and testable.
Clearly distinguish in-scope from out-of-scope to prevent scope creep.""",

    "product": """You are a Product Owner with expertise in product management and prioritization.
Prioritize features by business value, define MVP scope, and ensure alignment with strategic goals.
Focus on: feature prioritization, MVP definition, user impact, business value justification.
Use frameworks like RICE or MoSCoW for prioritization. Define measurable success criteria and KPIs.""",

    # Technical disciplines
    "architect": """You are a Senior Solutions Architect with 20+ years of experience.
Design clear, scalable, maintainable system architectures aligned with business constraints.
Provide: component diagrams, data flows, technology recommendations with business justification, scalability approach.
Explain technical decisions in business terms: cost, speed, reliability, security, maintainability.
Use standard architectural patterns and document key design decisions.""",

    "fullstack": """You are a Senior Full-Stack Developer focused on implementation feasibility and delivery.
Validate technical feasibility, estimate effort realistically, flag dependencies and risks.
Provide: effort estimates (hours/days/weeks), implementation approach, technical risks, phasing recommendations.
Be pragmatic: suggest simpler alternatives when complexity is high. Consider team capabilities.""",

    "ml": """You are an ML Research Scientist specializing in applied machine learning.
Assess AI/ML feasibility, define data requirements, recommend model approaches.
Focus on: problem framing, data needs, model approach (in plain language), performance metrics, ethical AI.
Set realistic expectations about accuracy, timeline, and cost. Explain AI limitations clearly.
Always address bias, fairness, and explainability considerations.""",

    "ux": """You are a UX/UI Strategist focused on human-centered design.
Define user personas, map user journeys, ensure usability and accessibility.
Provide: user personas, journey maps, key flows, usability requirements, accessibility standards (WCAG 2.1 AA).
Focus on intuitive, accessible experiences. Define UX success metrics (task completion, satisfaction).
Advocate for end users while balancing business constraints.""",

    "devops": """You are a DevOps Engineer specializing in production reliability and automation.
Design deployment pipelines, infrastructure, monitoring, and disaster recovery.
Focus on: infrastructure topology, CI/CD, scalability, monitoring, SLAs, disaster recovery (RTO/RPO).
Explain infrastructure in terms of reliability, performance, and cost.
Provide concrete uptime targets and operational requirements.""",

    "security": """You are a Security Specialist focused on risk management and compliance.
Identify security risks, define controls, ensure regulatory compliance.
Focus on: threat modeling, security controls, compliance requirements (GDPR/HIPAA/PCI/SOC2), data protection.
Explain security in business terms: risk, impact, compliance, reputation.
Balance security with usability. Provide clear recommendations for identity, encryption, and monitoring.""",

    "data": """You are a Data Engineer specializing in data architecture and pipelines.
Design data flows, storage strategies, and integration approaches.
Focus on: data architecture, quality, governance, pipeline design (batch/streaming), analytics enablement.
Explain data in business terms: quality, availability, insights, decision-making value.
Address data security, privacy, and compliance requirements.""",

    # Management
    "pm": """You are an experienced Project Manager specializing in technology initiatives.
Create realistic timelines, identify risks, allocate resources, define governance.
Provide: phased roadmap with milestones, resource plan, risk register, RAID log, project governance.
Use standard PM frameworks appropriately. Always state assumptions behind estimates.
Focus on achievable timelines with clear dependencies and critical path.""",
}


class ModelClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.MODEL_PROVIDER
        self.model = config.MODEL_NAME
        self.temperature = config.MODEL_TEMPERATURE

    def _get_short_prompt(self, role: str, prompt: str) -> str:
        """Get a shorter, more focused prompt for Ollama to avoid timeouts."""
        short_roles = {
            "engagement_manager": "You are Jennifer Martinez, Engagement Manager. Be warm, professional, and client-focused.",
            "product_strategist": "You are Alex, Product Strategist. Focus on business value, market opportunity, and ROI.",
            "lead_analyst": "You are Jordan, Lead Business Analyst. Focus on requirements, stakeholders, and user needs.",
            "solutions_architect": "You are Dr. Sarah Chen, Solutions Architect. Focus on technical feasibility and architecture.",
            "senior_developer": "You are Marcus, Senior Developer. Focus on implementation feasibility and effort estimates.",
            "ml_researcher": "You are Dr. James Liu, ML Researcher. Focus on AI/ML feasibility and data requirements.",
            "ux_strategist": "You are Priya, UX Strategist. Focus on user experience and usability.",
            "devops_engineer": "You are Carlos, DevOps Engineer. Focus on infrastructure and deployment.",
            "security_specialist": "You are Rachel Kim, Security Specialist. Focus on security and compliance.",
            "project_manager": "You are Robert Taylor, Project Manager. Focus on timeline and resource planning.",
            "quality_assurance": "You are Dr. Patricia Williams, QA Director. Focus on quality validation and testing."
        }
        
        role_intro = short_roles.get(role, f"You are an expert {role}.")
        return f"{role_intro}\n\nTask: {prompt}\n\nProvide a detailed, professional response."
    
    def generate(self, role: str, prompt: str, system: Optional[str] = None) -> str:
        """Generate text for a role+prompt using configured provider.

        Providers supported:
        - mock: deterministic placeholder
        - openai: uses openai.ChatCompletion if available and OPENAI_API_KEY set
        - ollama: attempts local Ollama HTTP endpoint at http://localhost:11434
        """
        system_prompt = system or ROLE_PROMPTS.get(role, "You are an expert.")
        
        # For Ollama, use shorter prompts to avoid timeouts
        if self.provider == "ollama":
            # Use a condensed version of the system prompt
            short_prompt = self._get_short_prompt(role, prompt)
            full_prompt = short_prompt
        else:
            full_prompt = f"{system_prompt}\n\nTask:\n{prompt}"

        if self.provider == "mock":
            return self._mock(role, prompt)

        if self.provider == "openai":
            try:
                import openai

                openai.api_key = os.environ.get("OPENAI_API_KEY")
                if not openai.api_key:
                    return self._mock(role, prompt)

                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=config.MODEL_MAX_TOKENS,
                )
                return resp.choices[0].message.content
            except Exception:
                return self._mock(role, prompt)

        if self.provider == "ollama":
            # Try local Ollama HTTP API. Prefer non-streaming /api/generate for a single JSON response.
            # Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
            try:
                host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
                url = f"{host}/api/generate"
                payload = {
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": self.temperature,
                    "stream": False,
                }
                r = requests.post(url, json=payload, timeout=15.0)
                if r.ok:
                    data = r.json()
                    if isinstance(data, dict):
                        # Non-streaming returns a 'response' field
                        if "response" in data:
                            return data["response"]
                        # Fallback: best-effort stringify
                        return json.dumps(data)
                else:
                    print(f"Ollama API error: {r.status_code} - {r.text}")
                    return self._mock(role, prompt)
            except Exception as e:
                print(f"Ollama connection error: {e}")
                return self._mock(role, prompt)

        # Unknown provider -> mock
        return self._mock(role, prompt)

    def _mock(self, role: str, prompt: str) -> str:
        # Professional mock responses that simulate real AI behavior
        role_responses = {
            "engagement_manager": f"""Hello! I'm Jennifer Martinez, your Engagement Manager at Elite Consulting Group.

I've reviewed your project details and I'm excited to work with you. Let me start by understanding your vision better.

Based on what you've shared, I can see this is an important initiative for your organization. To ensure we provide the most valuable consulting services, I'd like to explore a few key areas:

1. **Business Objectives**: What specific outcomes are you hoping to achieve?
2. **Target Users**: Who will be the primary users of this solution?
3. **Key Capabilities**: What are the most important features or capabilities?
4. **Timeline & Resources**: What's your target timeline and available resources?

This discovery conversation typically takes about 10-15 minutes and helps our specialist team provide tailored recommendations.

What would you like to start with?""",

            "product_strategist": f"""As your Product Strategist, I'm analyzing the business opportunity here.

**Strategic Assessment:**
- Market opportunity appears significant based on your description
- Clear business value proposition emerging
- Competitive positioning needs refinement

**Key Questions:**
- What's your target market size and competitive landscape?
- How does this align with your overall business strategy?
- What's your expected ROI and success metrics?

**Recommendations:**
- Focus on core value proposition first
- Define measurable success criteria
- Consider phased approach for market validation

Would you like me to dive deeper into any of these areas?""",

            "lead_analyst": f"""As your Lead Business Analyst, I'm documenting the requirements systematically.

**Requirements Analysis:**
- Functional requirements: Core capabilities identified
- Non-functional requirements: Performance, scalability, security needs
- Stakeholder analysis: Key user groups and their needs

**Key Requirements:**
- User authentication and authorization
- Core business functionality
- Data management and reporting
- Integration capabilities

**Next Steps:**
- Detailed user stories with acceptance criteria
- Process flow documentation
- Technical requirements specification

What specific functionality is most critical for your users?""",

            "solutions_architect": f"""As your Solutions Architect, I'm designing the technical approach.

**Architecture Overview:**
- Modern, scalable architecture recommended
- Cloud-native approach for flexibility
- Microservices for maintainability

**Technology Stack:**
- Frontend: Modern web framework
- Backend: Scalable API architecture
- Database: Appropriate data storage solution
- Infrastructure: Cloud-based deployment

**Key Design Decisions:**
- Security-first approach
- Scalability considerations
- Integration capabilities
- Performance optimization

Would you like me to elaborate on any technical aspects?""",

            "project_manager": f"""As your Project Manager, I'm creating a realistic implementation plan.

**Project Timeline:**
- Phase 1: Foundation & Core Features (8-12 weeks)
- Phase 2: Advanced Features & Integration (6-8 weeks)
- Phase 3: Testing, Deployment & Launch (4-6 weeks)

**Resource Requirements:**
- Development team: 4-6 developers
- Project management: Dedicated PM
- QA resources: 1-2 testers
- DevOps support: Infrastructure specialist

**Key Milestones:**
- Requirements finalization
- Architecture approval
- MVP development
- User acceptance testing
- Production deployment

**Risk Assessment:**
- Technical complexity: Medium
- Timeline dependencies: Manageable
- Resource availability: To be confirmed

What's your preferred timeline and resource constraints?"""
        }
        
        return role_responses.get(role, f"""As your {role.replace('_', ' ').title()}, I'm analyzing your requirements and will provide detailed recommendations.

Based on your project description, I can see several key areas that need attention:

1. **Core Requirements**: Understanding the essential functionality
2. **Technical Approach**: Determining the best implementation strategy  
3. **Timeline & Resources**: Planning realistic delivery expectations
4. **Risk Assessment**: Identifying potential challenges and mitigations

I'm working with our specialist team to provide comprehensive analysis and recommendations.

What specific aspects would you like me to focus on first?""")


def render_role_prompt(role: str, context: str) -> str:
    base = ROLE_PROMPTS.get(role, "You are an expert.")
    return f"{base}\n\nContext:\n{context}\n\nPlease respond concisely and in bullet points where helpful."
