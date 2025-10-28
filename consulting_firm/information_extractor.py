"""
Expert Information Extraction System

This module implements sophisticated information extraction with:
- Minimal question sets using information theory
- Active listening and context awareness
- Intelligent follow-up questions
- Gap identification and targeted probing
- Efficient information gathering
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class InformationDomain(Enum):
    """Critical information domains for consulting engagements."""
    BUSINESS_OBJECTIVE = "business_objective"  # Why, what business problem
    SUCCESS_METRICS = "success_metrics"        # How to measure success
    TARGET_USERS = "target_users"              # Who benefits, user segments
    CORE_CAPABILITIES = "core_capabilities"    # What it must do
    CONSTRAINTS = "constraints"                # Budget, time, technical, regulatory
    STAKEHOLDERS = "stakeholders"              # Decision makers, influencers
    EXISTING_CONTEXT = "existing_context"      # Current state, systems, data
    RISKS_ASSUMPTIONS = "risks_assumptions"    # Known risks, critical assumptions


@dataclass
class InformationGap:
    """Represents a gap in our understanding."""
    domain: InformationDomain
    severity: str  # "critical", "important", "nice-to-have"
    specific_question: str
    context: str
    dependencies: List[str]  # Other domains that must be known first


@dataclass
class ExtractedInformation:
    """Structured information extracted from user responses."""
    domain: InformationDomain
    confidence: float  # 0.0 to 1.0
    key_facts: List[str]
    inferred_facts: List[str]
    ambiguities: List[str]
    follow_up_needed: bool


class InformationExtractor:
    """
    Extracts and organizes information efficiently using consultative techniques.
    
    Principles:
    1. Ask open-ended questions that gather multiple domains simultaneously
    2. Listen actively for implicit information and context
    3. Identify gaps systematically
    4. Ask follow-ups only for critical missing information
    5. Confirm understanding before moving forward
    """
    
    def __init__(self, model_client):
        self.model = model_client
        self.extracted_info: Dict[InformationDomain, ExtractedInformation] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.identified_gaps: List[InformationGap] = []
        
    def analyze_user_response(self, user_input: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze user response to extract structured information across all domains.
        
        Returns:
            Dict with extracted_info, identified_gaps, confidence_scores
        """
        analysis_prompt = f"""You are an expert consultant analyzing a client's response to extract ALL relevant information efficiently.

CLIENT RESPONSE:
{user_input}

EXISTING CONTEXT:
{context}

Extract information across these domains:
1. BUSINESS_OBJECTIVE - Why they need this, what problem it solves
2. SUCCESS_METRICS - How they'll measure success (explicit or implied)
3. TARGET_USERS - Who will use/benefit from this
4. CORE_CAPABILITIES - What functionality is essential
5. CONSTRAINTS - Budget, timeline, technical, regulatory limitations
6. STAKEHOLDERS - Who makes decisions, who's affected
7. EXISTING_CONTEXT - Current systems, data, processes
8. RISKS_ASSUMPTIONS - What could go wrong, what we're assuming

For EACH domain, provide:
- KEY_FACTS: Explicit facts stated (list each)
- INFERRED_FACTS: Reasonable inferences (list each with confidence)
- AMBIGUITIES: What's unclear or could mean multiple things
- CONFIDENCE: 0.0-1.0 score for how well we understand this domain

Format as structured sections. Be thorough - extract EVERYTHING mentioned, even briefly."""

        analysis = self.model.generate("analyst", analysis_prompt)
        
        # Parse analysis (in production, use structured output format)
        domains_covered = self._parse_domain_analysis(analysis)
        
        # Update extracted information
        for domain, info in domains_covered.items():
            if domain not in self.extracted_info:
                self.extracted_info[domain] = info
            else:
                # Merge with existing information
                self.extracted_info[domain] = self._merge_information(
                    self.extracted_info[domain], info
                )
        
        # Identify gaps
        self.identified_gaps = self._identify_information_gaps()
        
        return {
            "extracted_info": self.extracted_info,
            "gaps": self.identified_gaps,
            "coverage_score": self._calculate_coverage_score()
        }
    
    def generate_next_question(self, conversation_stage: str = "discovery") -> Tuple[str, str]:
        """
        Generate the most effective next question to fill critical gaps.
        
        Principles:
        - Start with open-ended question that covers multiple domains
        - Move to specific questions only for critical gaps
        - Confirm understanding when nearing completion
        - Always maintain conversational, consultative tone
        
        Returns: (question, rationale)
        """
        # Check if we have sufficient information
        coverage = self._calculate_coverage_score()
        
        if coverage >= 0.85:
            return self._generate_confirmation_question()
        
        # Get most critical gaps
        critical_gaps = [g for g in self.identified_gaps if g.severity == "critical"]
        important_gaps = [g for g in self.identified_gaps if g.severity == "important"]
        
        if conversation_stage == "discovery" and len(self.conversation_history) < 2:
            # Start with broad, open-ended question
            return self._generate_opening_question()
        
        if critical_gaps:
            # Address most critical gap with context-aware question
            return self._generate_targeted_question(critical_gaps[0])
        
        if important_gaps and coverage < 0.70:
            # Address important gaps if coverage still low
            return self._generate_targeted_question(important_gaps[0])
        
        # Near completion - confirm and wrap up
        return self._generate_confirmation_question()
    
    def _generate_opening_question(self) -> Tuple[str, str]:
        """Generate an effective opening question that gathers broad context."""
        
        # Check what we already know from intake
        known_context = self._summarize_known_context()
        
        question_prompt = f"""You are Jennifer Martinez, Engagement Manager leading a discovery conversation.

WHAT WE KNOW SO FAR:
{known_context}

Generate ONE powerful opening question that will efficiently gather information across multiple domains:
- Business objectives and problem being solved
- Target users and their needs
- Success criteria and metrics
- Key capabilities required
- Critical constraints

REQUIREMENTS:
- Open-ended question that invites detailed response
- Conversational and consultative (not interrogative)
- Shows you've reviewed their initial information
- Encourages client to share their vision broadly
- 2-3 sentences maximum

Example good openings:
"I've reviewed your project overview for [PROJECT NAME]. To ensure we design the right solution, help me understand: what's the core business challenge your users face today, and what does success look like for them in 6 months?"

"Thank you for sharing [SPECIFIC DETAIL]. I'd like to understand the bigger picture: walk me through a day in the life of your target user - what pain points will this solution eliminate, and how will you measure the impact?"

Your opening question:"""

        from consulting_firm.consulting_personas import get_persona_prompt
        question = self.model.generate(
            "engagement_manager",
            question_prompt,
            system=get_persona_prompt("engagement_manager")
        )
        
        rationale = "Opening question designed to gather broad context across multiple information domains"
        return (question.strip(), rationale)
    
    def _generate_targeted_question(self, gap: InformationGap) -> Tuple[str, str]:
        """Generate a specific question to fill an identified gap."""
        
        context_summary = self._summarize_known_context()
        
        question_prompt = f"""You are an expert consultant conducting discovery.

WHAT WE KNOW:
{context_summary}

CRITICAL GAP:
Domain: {gap.domain.value}
Severity: {gap.severity}
Context: {gap.context}

Generate ONE specific question to fill this gap:
- Reference what we already know to show you're listening
- Ask specifically about the missing information
- Keep it conversational and consultative
- 1-2 sentences only
- Frame in business terms, not technical jargon

Examples of good targeted questions:
"You mentioned [SPECIFIC THING THEY SAID]. To ensure we scope this correctly, what are the 3-5 core features that absolutely must be in the MVP for launch?"

"I understand [WHAT THEY WANT]. Help me understand the constraints we're working within - what's your target timeline and budget range for this initiative?"

"You've described [THEIR VISION] well. Who are the key stakeholders who need to sign off on this, and what matters most to each of them?"

Your targeted question:"""

        from consulting_firm.consulting_personas import get_persona_prompt
        question = self.model.generate(
            "analyst",
            question_prompt,
            system=get_persona_prompt("analyst")
        )
        
        rationale = f"Targeted question to address {gap.severity} gap in {gap.domain.value}"
        return (question.strip(), rationale)
    
    def _generate_confirmation_question(self) -> Tuple[str, str]:
        """Generate a confirmation question to validate understanding."""
        
        summary = self._generate_understanding_summary()
        
        confirmation_prompt = f"""You are wrapping up discovery with the client.

SUMMARY OF WHAT WE'VE LEARNED:
{summary}

Generate a confirmation statement and final question:
1. Briefly summarize key points (3-4 sentences)
2. Ask if there's anything important we haven't covered
3. Professional, warm tone
4. Give them confidence we understand their needs

Example:
"Let me confirm my understanding: you're building [SOLUTION] to help [USERS] [ACHIEVE GOAL]. Success will be measured by [METRICS], and you need this delivered in [TIMELINE] with [KEY CONSTRAINTS]. The core MVP must include [CAPABILITIES]. 

Is there anything critical I'm missing, or any constraints we should be aware of before we create your deliverables?"

Your confirmation:"""

        from consulting_firm.consulting_personas import get_persona_prompt
        confirmation = self.model.generate(
            "engagement_manager",
            confirmation_prompt,
            system=get_persona_prompt("engagement_manager")
        )
        
        rationale = "Confirmation question to validate understanding and catch any remaining gaps"
        return (confirmation.strip(), rationale)
    
    def _summarize_known_context(self) -> str:
        """Create a concise summary of what we know so far."""
        summary_parts = []
        
        for domain, info in self.extracted_info.items():
            if info.confidence >= 0.5 and info.key_facts:
                facts_str = "; ".join(info.key_facts[:3])
                summary_parts.append(f"- {domain.value}: {facts_str}")
        
        return "\n".join(summary_parts) if summary_parts else "Minimal context from intake"
    
    def _generate_understanding_summary(self) -> str:
        """Generate a comprehensive summary of our understanding."""
        summary_parts = []
        
        for domain in InformationDomain:
            if domain in self.extracted_info:
                info = self.extracted_info[domain]
                if info.key_facts:
                    summary_parts.append(f"**{domain.value}:**")
                    for fact in info.key_facts[:5]:
                        summary_parts.append(f"  - {fact}")
        
        return "\n".join(summary_parts)
    
    def _calculate_coverage_score(self) -> float:
        """Calculate how complete our information is (0.0 to 1.0)."""
        total_domains = len(InformationDomain)
        weighted_coverage = 0.0
        
        # Critical domains have higher weight
        critical_domains = [
            InformationDomain.BUSINESS_OBJECTIVE,
            InformationDomain.TARGET_USERS,
            InformationDomain.CORE_CAPABILITIES
        ]
        
        for domain in InformationDomain:
            if domain in self.extracted_info:
                confidence = self.extracted_info[domain].confidence
                weight = 2.0 if domain in critical_domains else 1.0
                weighted_coverage += confidence * weight
        
        # Normalize
        max_possible = sum(2.0 if d in critical_domains else 1.0 for d in InformationDomain)
        return min(1.0, weighted_coverage / max_possible)
    
    def _identify_information_gaps(self) -> List[InformationGap]:
        """Identify gaps in our information systematically."""
        gaps = []
        
        # Define required confidence levels
        critical_threshold = 0.7
        important_threshold = 0.5
        
        for domain in InformationDomain:
            confidence = 0.0
            if domain in self.extracted_info:
                confidence = self.extracted_info[domain].confidence
            
            if confidence < critical_threshold:
                severity = "critical" if domain in [
                    InformationDomain.BUSINESS_OBJECTIVE,
                    InformationDomain.TARGET_USERS,
                    InformationDomain.CORE_CAPABILITIES
                ] else "important" if confidence < important_threshold else "nice-to-have"
                
                gaps.append(InformationGap(
                    domain=domain,
                    severity=severity,
                    specific_question="",  # Generated on demand
                    context=self._get_gap_context(domain),
                    dependencies=self._get_domain_dependencies(domain)
                ))
        
        # Sort by severity
        severity_order = {"critical": 0, "important": 1, "nice-to-have": 2}
        gaps.sort(key=lambda g: severity_order[g.severity])
        
        return gaps
    
    def _get_gap_context(self, domain: InformationDomain) -> str:
        """Get context for why this domain is important."""
        contexts = {
            InformationDomain.BUSINESS_OBJECTIVE: "Need to understand core business problem and desired outcomes",
            InformationDomain.SUCCESS_METRICS: "Need measurable criteria to define project success",
            InformationDomain.TARGET_USERS: "Need to identify who benefits and their specific needs",
            InformationDomain.CORE_CAPABILITIES: "Need to understand essential features for MVP",
            InformationDomain.CONSTRAINTS: "Need to know budget, timeline, technical, and regulatory constraints",
            InformationDomain.STAKEHOLDERS: "Need to identify decision makers and their priorities",
            InformationDomain.EXISTING_CONTEXT: "Need to understand current systems and data",
            InformationDomain.RISKS_ASSUMPTIONS: "Need to identify known risks and critical assumptions"
        }
        return contexts.get(domain, "")
    
    def _get_domain_dependencies(self, domain: InformationDomain) -> List[str]:
        """Get domains that should be understood before this one."""
        dependencies = {
            InformationDomain.SUCCESS_METRICS: [InformationDomain.BUSINESS_OBJECTIVE.value],
            InformationDomain.CORE_CAPABILITIES: [InformationDomain.TARGET_USERS.value],
            InformationDomain.RISKS_ASSUMPTIONS: [InformationDomain.CORE_CAPABILITIES.value]
        }
        return dependencies.get(domain, [])
    
    def _parse_domain_analysis(self, analysis_text: str) -> Dict[InformationDomain, ExtractedInformation]:
        """Parse the AI's analysis into structured information."""
        # Simplified parsing - in production use structured output format
        domains = {}
        
        for domain in InformationDomain:
            # Extract section for this domain from analysis
            # This is simplified - real implementation would use structured parsing
            if domain.value.upper() in analysis_text.upper():
                domains[domain] = ExtractedInformation(
                    domain=domain,
                    confidence=0.6,  # Default confidence
                    key_facts=["Extracted fact 1", "Extracted fact 2"],
                    inferred_facts=[],
                    ambiguities=[],
                    follow_up_needed=False
                )
        
        return domains
    
    def _merge_information(self, existing: ExtractedInformation, new: ExtractedInformation) -> ExtractedInformation:
        """Merge new information with existing information for a domain."""
        return ExtractedInformation(
            domain=existing.domain,
            confidence=max(existing.confidence, new.confidence),
            key_facts=list(set(existing.key_facts + new.key_facts)),
            inferred_facts=list(set(existing.inferred_facts + new.inferred_facts)),
            ambiguities=list(set(existing.ambiguities + new.ambiguities)),
            follow_up_needed=existing.follow_up_needed or new.follow_up_needed
        )
    
    def export_structured_brief(self) -> Dict[str, Any]:
        """Export all extracted information as a structured brief for agents."""
        brief = {
            "coverage_score": self._calculate_coverage_score(),
            "domains": {}
        }
        
        for domain, info in self.extracted_info.items():
            brief["domains"][domain.value] = {
                "confidence": info.confidence,
                "key_facts": info.key_facts,
                "inferred_facts": info.inferred_facts,
                "ambiguities": info.ambiguities
            }
        
        brief["remaining_gaps"] = [
            {
                "domain": gap.domain.value,
                "severity": gap.severity,
                "context": gap.context
            }
            for gap in self.identified_gaps
            if gap.severity in ["critical", "important"]
        ]
        
        return brief
