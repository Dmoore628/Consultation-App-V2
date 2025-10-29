"""
Structured consultation state and extractor.

Captures features, functional/non-functional requirements, acceptance criteria,
constraints, deliverables, user stories, and expectations as a normalized
schema updated incrementally from chat.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

from model_client import ModelClient
from consulting_personas import get_persona_prompt


@dataclass
class RequirementItem:
    id: str
    title: str
    description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    priority: str = ""


@dataclass
class NonFunctionalRequirement:
    category: str
    details: List[str] = field(default_factory=list)


@dataclass
class UserStory:
    role: str
    capability: str
    benefit: str
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class ConsultationData:
    features: List[RequirementItem] = field(default_factory=list)
    functional_requirements: List[RequirementItem] = field(default_factory=list)
    non_functional_requirements: List[NonFunctionalRequirement] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    expectations: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    user_stories: List[UserStory] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines: List[str] = []
        if self.features:
            lines.append("## Features")
            for f in self.features:
                lines.append(f"- {f.title}: {f.description}")
        if self.functional_requirements:
            lines.append("\n## Functional Requirements")
            for r in self.functional_requirements:
                lines.append(f"- {r.title}: {r.description}")
                if r.acceptance_criteria:
                    for ac in r.acceptance_criteria:
                        lines.append(f"  - [AC] {ac}")
        if self.non_functional_requirements:
            lines.append("\n## Non-Functional Requirements")
            for nfr in self.non_functional_requirements:
                lines.append(f"- {nfr.category}")
                for d in nfr.details:
                    lines.append(f"  - {d}")
        if self.expectations:
            lines.append("\n## Expectations")
            for e in self.expectations:
                lines.append(f"- {e}")
        if self.constraints:
            lines.append("\n## Constraints")
            for c in self.constraints:
                lines.append(f"- {c}")
        if self.deliverables:
            lines.append("\n## Deliverables")
            for d in self.deliverables:
                lines.append(f"- {d}")
        if self.user_stories:
            lines.append("\n## User Stories")
            for us in self.user_stories:
                lines.append(f"- As {us.role}, I need {us.capability} so that {us.benefit}.")
                for ac in us.acceptance_criteria:
                    lines.append(f"  - [AC] {ac}")
        if self.risks:
            lines.append("\n## Risks")
            for r in self.risks:
                lines.append(f"- {r}")
        return "\n".join(lines)


def extract_structured_from_chat(profile: Dict[str, Any], notes: str, messages: List[Dict[str, str]]) -> ConsultationData:
    """Use QA persona to produce structured JSON of consultation data from chat.

    The model returns a JSON payload; if parsing fails, return minimal defaults.
    """
    model = ModelClient()
    qa_persona = get_persona_prompt("quality_assurance")
    recent = "\n".join([
        ("Client: " + m['content']) if m['role'] == 'user' else ("Consultant: " + m['content'])
        for m in messages[-30:]
    ])
    prompt = (
        "Extract a complete, consistent structured representation from the consultation.\n"
        "Return STRICT JSON with keys: features (list of {id,title,description,acceptance_criteria,priority}),"
        " functional_requirements (same structure as features), non_functional_requirements (list of {category,details}),"
        " expectations (list), constraints (list), deliverables (list), user_stories (list of {role,capability,benefit,acceptance_criteria}), risks (list).\n"
        "Ensure correctness, deduplicate, and consolidate overlapping items.\n\n"
        f"Profile:\nClient={profile.get('client_name','')}\nProject={profile.get('project_name','')}\nIndustry={profile.get('industry','')}\nDescription={profile.get('project_description','')}\nNotes={notes[:1200]}\n\n"
        f"Chat:\n{recent}\n\n"
        "Respond with JSON only."
    )
    raw = model.generate("quality_assurance", prompt, system=qa_persona)
    import json
    data: Dict[str, Any] = {}
    try:
        # Try to locate JSON content
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            data = json.loads(raw[start:end+1])
    except Exception:
        data = {}

    def _items(src: List[Dict[str, Any]]) -> List[RequirementItem]:
        out: List[RequirementItem] = []
        if not isinstance(src, list):
            return out
        for i, it in enumerate(src):
            if not isinstance(it, dict):
                continue
            out.append(RequirementItem(
                id=str(it.get('id', i+1)),
                title=str(it.get('title', '')).strip(),
                description=str(it.get('description', '')).strip(),
                acceptance_criteria=[str(a).strip() for a in (it.get('acceptance_criteria') or [])],
                priority=str(it.get('priority', '')).strip()
            ))
        return out

    def _nfrs(src: List[Dict[str, Any]]) -> List[NonFunctionalRequirement]:
        out: List[NonFunctionalRequirement] = []
        if not isinstance(src, list):
            return out
        for it in src:
            if not isinstance(it, dict):
                continue
            out.append(NonFunctionalRequirement(
                category=str(it.get('category', '')).strip(),
                details=[str(d).strip() for d in (it.get('details') or [])]
            ))
        return out

    def _stories(src: List[Dict[str, Any]]) -> List[UserStory]:
        out: List[UserStory] = []
        if not isinstance(src, list):
            return out
        for it in src:
            if not isinstance(it, dict):
                continue
            out.append(UserStory(
                role=str(it.get('role', '')).strip(),
                capability=str(it.get('capability', '')).strip(),
                benefit=str(it.get('benefit', '')).strip(),
                acceptance_criteria=[str(a).strip() for a in (it.get('acceptance_criteria') or [])]
            ))
        return out

    cd = ConsultationData(
        features=_items(data.get('features', [])),
        functional_requirements=_items(data.get('functional_requirements', [])),
        non_functional_requirements=_nfrs(data.get('non_functional_requirements', [])),
        constraints=[str(c).strip() for c in (data.get('constraints') or [])],
        expectations=[str(e).strip() for e in (data.get('expectations') or [])],
        deliverables=[str(d).strip() for d in (data.get('deliverables') or [])],
        user_stories=_stories(data.get('user_stories', [])),
        risks=[str(r).strip() for r in (data.get('risks') or [])]
    )
    return cd


