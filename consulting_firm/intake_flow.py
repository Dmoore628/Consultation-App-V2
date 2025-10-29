"""
Professional client intake workflow module.

Handles the initial engagement process following industry-standard practices:
1. Client identification
2. Project overview
3. Industry/domain detection
4. Document collection
5. Engagement confirmation
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class IntakeStage(Enum):
    """Stages of the client intake process."""
    WELCOME = "welcome"
    CLIENT_INFO = "client_info"
    DOCUMENT_UPLOAD = "document_upload"
    PROJECT_OVERVIEW = "project_overview"
    ENGAGEMENT_CONFIRMED = "engagement_confirmed"


@dataclass
class ClientProfile:
    """Client and project information collected during intake."""
    client_name: str = ""
    organization: str = ""
    project_name: str = ""
    project_description: str = ""
    industry: str = ""
    primary_objectives: str = ""
    has_existing_docs: bool = False
    uploaded_files: list[str] = None
    inferred_project_info: dict = None
    
    def __post_init__(self):
        if self.uploaded_files is None:
            self.uploaded_files = []
        if self.inferred_project_info is None:
            self.inferred_project_info = {}
    
    def is_complete(self) -> bool:
        """Check if minimum required information is collected."""
        return bool(
            self.client_name 
            and self.project_name 
            and self.project_description
        )
    
    def to_context_string(self) -> str:
        """Format profile as context for AI agents."""
        parts = [
            f"Client: {self.client_name}",
            f"Organization: {self.organization}" if self.organization else "",
            f"Project: {self.project_name}",
            f"Industry: {self.industry}" if self.industry else "",
            f"Description: {self.project_description}",
            f"Objectives: {self.primary_objectives}" if self.primary_objectives else "",
        ]
        return "\n".join(p for p in parts if p)


class IntakeWorkflow:
    """Manages the progression through intake stages."""
    
    @staticmethod
    def get_stage_description(stage: IntakeStage) -> dict[str, str]:
        """Get UI text for each stage."""
        descriptions = {
            IntakeStage.WELCOME: {
                "title": "Welcome to Elite Consulting Group",
                "subtitle": "Let's begin your engagement",
                "instruction": "We'll start with some basic information to ensure we assemble the right team for your project."
            },
            IntakeStage.CLIENT_INFO: {
                "title": "Client Information",
                "subtitle": "Tell us about yourself",
                "instruction": "This helps us personalize our engagement and assign the appropriate specialists."
            },
            IntakeStage.DOCUMENT_UPLOAD: {
                "title": "Existing Documentation",
                "subtitle": "Share any materials you have",
                "instruction": "Upload any existing documents (requirements, architecture, notes, etc.). This is optional but helps us provide better insights."
            },
            IntakeStage.PROJECT_OVERVIEW: {
                "title": "Project Overview",
                "subtitle": "Share your vision",
                "instruction": "Help us understand your project at a high level. We'll dive deeper during discovery."
            },
            IntakeStage.ENGAGEMENT_CONFIRMED: {
                "title": "Engagement Confirmed",
                "subtitle": "Your specialist team is ready",
                "instruction": "We've assembled your team and reviewed your materials. Let's begin the discovery process."
            }
        }
        return descriptions.get(stage, {"title": "", "subtitle": "", "instruction": ""})
    
    @staticmethod
    def validate_stage_completion(stage: IntakeStage, profile: ClientProfile) -> tuple[bool, str]:
        """Validate if current stage requirements are met."""
        if stage == IntakeStage.CLIENT_INFO:
            if not profile.client_name:
                return False, "Please provide your name"
            return True, ""
        
        elif stage == IntakeStage.DOCUMENT_UPLOAD:
            # This stage is optional - always valid
            return True, ""
        
        elif stage == IntakeStage.PROJECT_OVERVIEW:
            if not profile.project_name:
                return False, "Please provide a project name"
            if not profile.project_description:
                return False, "Please provide a project description"
            return True, ""
        
        return True, ""
    
    @staticmethod
    def next_stage(current: IntakeStage) -> Optional[IntakeStage]:
        """Get next stage in workflow."""
        stages = list(IntakeStage)
        try:
            current_idx = stages.index(current)
            if current_idx < len(stages) - 1:
                return stages[current_idx + 1]
        except (ValueError, IndexError):
            pass
        return None
    
    @staticmethod
    def get_engagement_manager_greeting(profile: ClientProfile, has_documents: bool) -> str:
        """Generate personalized greeting after intake completion."""
        greeting_parts = [
            f"Thank you, {profile.client_name}. I'm Jennifer Martinez, your Engagement Manager.",
            f"\nI've assembled a specialist team for your {profile.industry if profile.industry else 'project'} initiative: **{profile.project_name}**.",
        ]
        
        if has_documents:
            greeting_parts.append(
                f"\n\nI've reviewed the {len(profile.uploaded_files)} document(s) you've shared. "
                "Our team will reference these throughout our engagement."
            )
        
        greeting_parts.append(
            "\n\nLet's begin with discovery. I'll ask targeted questions to ensure we understand your "
            "vision, requirements, and constraints. This typically takes 5-10 minutes."
        )
        
        return "".join(greeting_parts)


def create_intake_form_data() -> dict:
    """Define form fields for each intake stage."""
    return {
        IntakeStage.CLIENT_INFO: [
            {
                "key": "client_name",
                "label": "Your Name",
                "type": "text",
                "required": True,
                "placeholder": "e.g., John Smith",
                "help": "Primary point of contact for this engagement"
            },
            {
                "key": "organization",
                "label": "Organization (Optional)",
                "type": "text",
                "required": False,
                "placeholder": "e.g., Acme Corporation",
                "help": "Company or entity name"
            }
        ],
        IntakeStage.PROJECT_OVERVIEW: [
            {
                "key": "project_name",
                "label": "Project Name",
                "type": "text",
                "required": True,
                "placeholder": "e.g., AI-Powered Customer Support Platform",
                "help": "Working title for your initiative"
            },
            {
                "key": "industry",
                "label": "Industry/Domain (Optional)",
                "type": "select",
                "required": False,
                "options": [
                    "",
                    "Financial Services / Trading",
                    "Healthcare / Life Sciences",
                    "E-commerce / Retail",
                    "Robotics / IoT / Hardware",
                    "AI / Machine Learning",
                    "Enterprise Software / SaaS",
                    "Other"
                ],
                "help": "Helps us assign domain specialists"
            },
            {
                "key": "project_description",
                "label": "Project Description",
                "type": "textarea",
                "required": True,
                "placeholder": "Describe your project vision in 2-3 sentences...",
                "help": "High-level overview - we'll explore details during discovery"
            },
            {
                "key": "primary_objectives",
                "label": "Primary Objectives (Optional)",
                "type": "textarea",
                "required": False,
                "placeholder": "e.g., Reduce support costs by 40%, improve response time, scale to 10K users",
                "help": "Key business outcomes you're targeting"
            }
        ]
    }
