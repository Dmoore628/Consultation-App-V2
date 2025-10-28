"""Simple pluggable model client supporting mock/openai/ollama calls.

This file implements a minimal abstraction to allow role-specific prompts
in `expert_team.py`. It avoids hard failures when cloud clients aren't
installed by providing a deterministic mock provider.
"""
from typing import Optional, Dict
import json
import os
import subprocess
import requests
from . import config


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

    def generate(self, role: str, prompt: str, system: Optional[str] = None) -> str:
        """Generate text for a role+prompt using configured provider.

        Providers supported:
        - mock: deterministic placeholder
        - openai: uses openai.ChatCompletion if available and OPENAI_API_KEY set
        - ollama: attempts local Ollama HTTP endpoint at http://localhost:11434
        """
        system_prompt = system or ROLE_PROMPTS.get(role, "You are an expert.")
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
                r = requests.post(url, json=payload, timeout=30.0)
                if r.ok:
                    data = r.json()
                    if isinstance(data, dict):
                        # Non-streaming returns a 'response' field
                        if "response" in data:
                            return data["response"]
                        # Fallback: best-effort stringify
                        return json.dumps(data)
            except Exception:
                return self._mock(role, prompt)

        # Unknown provider -> mock
        return self._mock(role, prompt)

    def _mock(self, role: str, prompt: str) -> str:
        # Deterministic placeholder to keep local runs fast and offline-safe.
        header = f"[{role.upper()} RESPONSE - provider={self.provider}]\n"
        summary = f"Summary for role={role}. Prompt preview: {prompt[:120]}"
        return header + summary + "\n\n(Use MODEL_PROVIDER=openai|ollama to enable real models.)"


def render_role_prompt(role: str, context: str) -> str:
    base = ROLE_PROMPTS.get(role, "You are an expert.")
    return f"{base}\n\nContext:\n{context}\n\nPlease respond concisely and in bullet points where helpful."
