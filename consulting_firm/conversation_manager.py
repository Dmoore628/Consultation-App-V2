"""
Conversation orchestration module.

Handles:
- Turn-taking between AI specialists and client
- Context management
- Specialist assignment based on conversation stage
- Response generation with appropriate persona
"""

from typing import Optional
from dataclasses import dataclass
from consulting_firm.model_client import ModelClient
from consulting_firm.intake_flow import ClientProfile


@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    speaker: Optional[str] = None  # e.g., "Jennifer Martinez (Engagement Manager)"
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConversationContext:
    """Manages conversation history and context."""
    
    def __init__(self, client_profile: ClientProfile):
        self.client_profile = client_profile
        self.messages: list[ConversationMessage] = []
        self.discovery_status: dict[str, bool] = {
            'goals': False,
            'users': False,
            'features': False,
            'tech_stack': False,
            'timeline': False
        }
    
    def add_message(self, role: str, content: str, speaker: Optional[str] = None, **metadata):
        """Add a message to conversation history."""
        msg = ConversationMessage(
            role=role,
            content=content,
            speaker=speaker,
            metadata=metadata
        )
        self.messages.append(msg)
        
        # Update discovery status if user message
        if role == 'user':
            self._update_discovery_status(content)
    
    def _update_discovery_status(self, user_text: str):
        """Analyze user text and update discovery status."""
        text_lower = user_text.lower()
        
        checks = {
            'goals': ['goal', 'objective', 'purpose', 'mission', 'problem', 'solve', 'need', 'want'],
            'users': ['user', 'customer', 'stakeholder', 'audience', 'who', 'persona', 'target'],
            'features': ['feature', 'functionality', 'capability', 'mvp', 'deliver', 'scope', 'requirement'],
            'tech_stack': ['technology', 'stack', 'platform', 'framework', 'language', 'database', 'infrastructure', 'architecture'],
            'timeline': ['timeline', 'deadline', 'schedule', 'month', 'week', 'launch', 'phase', 'milestone']
        }
        
        for area, keywords in checks.items():
            if any(kw in text_lower for kw in keywords):
                self.discovery_status[area] = True
    
    def is_sufficient_for_generation(self) -> bool:
        """Check if enough information gathered to generate deliverables."""
        # Need at least 3 of 5 discovery areas covered
        return sum(self.discovery_status.values()) >= 3
    
    def get_missing_areas(self) -> list[str]:
        """Get list of discovery areas not yet covered."""
        return [area for area, covered in self.discovery_status.items() if not covered]
    
    def get_user_text_combined(self) -> str:
        """Get all user messages combined."""
        return " ".join([msg.content for msg in self.messages if msg.role == 'user'])
    
    def get_recent_context(self, num_messages: int = 6) -> str:
        """Get recent conversation context for AI prompting."""
        recent = self.messages[-num_messages:] if len(self.messages) > num_messages else self.messages
        return "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in recent])


class ConversationOrchestrator:
    """Orchestrates conversation flow and specialist assignment."""
    
    def __init__(self, model_client: ModelClient):
        self.model = model_client
    
    def generate_opening_statement(
        self, 
        client_profile: ClientProfile, 
        team_intro: str,
        document_summary: Optional[str] = None
    ) -> str:
        """Generate Engagement Manager's opening statement after intake."""
        
        prompt = f"""You are Jennifer Martinez, Engagement Manager at Elite Consulting Group.

CLIENT PROFILE:
{client_profile.to_context_string()}

DOCUMENTS PROVIDED: {len(client_profile.uploaded_files) if client_profile.uploaded_files else 0}
{document_summary if document_summary else "No documents uploaded yet."}

YOUR TASK:
Generate a professional, warm opening statement (4-5 sentences) that:
1. Thanks {client_profile.client_name} and confirms engagement for: {client_profile.project_name}
2. If documents provided: Acknowledges receipt and confirms team has reviewed them
3. If no documents: Offers that they can upload documents at any time if helpful
4. Explains the discovery process: We'll have a brief conversation (5-10 minutes) to understand their vision, goals, users, and success criteria
5. Asks the first strategic question focused on their primary business objective or the problem they're solving

TONE: Professional yet approachable, consultative not interrogative. They are the domain expert; we're here to structure and execute their vision.

FORMAT: 4-5 sentences, then end with ONE clear, open-ended question that invites them to share their vision or primary goal."""

        from consulting_firm.consulting_personas import get_persona_prompt
        
        response = self.model.generate(
            "engagement_manager", 
            prompt,
            system=get_persona_prompt("engagement_manager")
        )
        
        return f"{team_intro}\n\n{response.strip()}"
    
    def generate_discovery_question(
        self, 
        context: ConversationContext,
        force_specialist: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate next discovery question.
        
        Returns: (question_text, speaker_name)
        """
        
        if context.is_sufficient_for_generation():
            return (
                "✅ **Excellent progress!** We've gathered comprehensive information across the key discovery areas. "
                "We now have sufficient context to generate your professional deliverables.\n\n"
                "Click **'Generate Deliverables'** when you're ready, or feel free to share any additional details you'd like us to consider.",
                "Jennifer Martinez (Engagement Manager)"
            )
        
        missing = context.get_missing_areas()
        recent_context = context.get_recent_context()
        
        # Determine appropriate specialist
        if force_specialist:
            specialist_role = force_specialist
        else:
            specialist_role = self._assign_specialist(missing, context)
        
        specialist_name = self._get_specialist_name(specialist_role)
        
        # Build focused prompt for question generation
        missing_area_desc = self._get_area_description(missing[0] if missing else 'general')
        
        prompt = f"""Based on this ongoing conversation with {context.client_profile.client_name} about their project "{context.client_profile.project_name}":

RECENT CONVERSATION:
{recent_context}

DISCOVERY STATUS:
- Covered: {[area for area, covered in context.discovery_status.items() if covered]}
- Still needed: {missing}

YOUR CURRENT FOCUS: {missing_area_desc}

Generate ONE specific, insightful question to gather information about: {missing[0] if missing else 'additional context'}.

REQUIREMENTS:
- Ask naturally like a real senior consultant would (conversational, not interrogative)
- Be specific and actionable - focus on concrete details, not vague generalities
- Reference their project context to show you're listening
- Keep it concise (1-2 sentences)
- Focus on business value and outcomes, not technical implementation details
- Make it an open-ended question that invites detailed response

Example good questions:
- "What does success look like for your users in the first 6 months after launch?"
- "Who are the key stakeholders who need to sign off on this initiative, and what matters most to each of them?"
- "What's the biggest pain point your target users experience today that this solution will address?"

Your question:"""

        from consulting_firm.consulting_personas import get_persona_prompt
        
        question = self.model.generate(
            specialist_role,
            prompt,
            system=get_persona_prompt(specialist_role)
        )
        
        return question.strip(), specialist_name
    
    def _assign_specialist(self, missing_areas: list[str], context: ConversationContext) -> str:
        """Assign appropriate specialist based on missing discovery areas and conversation flow."""
        if not missing_areas:
            return "engagement_manager"
        
        # Map discovery areas to specialist roles with intelligent assignment
        area_to_specialist = {
            'goals': 'strategist',      # Business strategist for goals and vision
            'users': 'product',          # Product strategist for user focus
            'features': 'analyst',       # Business analyst for detailed requirements
            'tech_stack': 'architect',   # Solutions architect for technical decisions
            'timeline': 'pm'             # Project manager for scheduling
        }
        
        # Get first missing area
        first_missing = missing_areas[0]
        
        # Check conversation history for intelligent specialist rotation
        # Avoid same specialist asking multiple questions in a row
        if len(context.messages) > 1:
            last_speaker_role = None
            for msg in reversed(context.messages):
                if msg.role == 'assistant' and msg.metadata and 'role' in msg.metadata:
                    last_speaker_role = msg.metadata['role']
                    break
            
            # If same specialist would be assigned, rotate to engagement manager for smooth transition
            assigned_specialist = area_to_specialist.get(first_missing, 'engagement_manager')
            if last_speaker_role == assigned_specialist and len(missing_areas) > 1:
                # Try next missing area or use engagement manager
                return area_to_specialist.get(missing_areas[1], 'engagement_manager')
        
        return area_to_specialist.get(first_missing, 'engagement_manager')
    
    def _get_area_description(self, area: str) -> str:
        """Get human-readable description of discovery area."""
        descriptions = {
            'goals': 'Business objectives, desired outcomes, and strategic goals',
            'users': 'Target users, stakeholders, and their needs',
            'features': 'Key features, capabilities, and functional requirements',
            'tech_stack': 'Technology approach, architecture, and technical constraints',
            'timeline': 'Project timeline, milestones, and critical deadlines',
            'general': 'Additional context and important considerations'
        }
        return descriptions.get(area, 'General project context')
    
    def _get_specialist_name(self, role: str) -> str:
        """Get display name for specialist role."""
        role_names = {
            'engagement_manager': 'Jennifer Martinez (Engagement Manager)',
            'strategist': 'Alex (Product Strategist)',
            'analyst': 'Jordan (Lead Analyst)',
            'product': 'Alex (Product Strategist)',
            'architect': 'Dr. Sarah Chen (Solutions Architect)',
            'pm': 'Robert Taylor (Project Manager)',
            'ml': 'Dr. Michael Zhang (ML Specialist)',
            'ux': 'Maya Patel (UX Strategist)'
        }
        return role_names.get(role, 'Elite Consulting Team')
