"""
Team assembly module.

Assembles appropriate specialist teams based on project domain.
"""

from consulting_firm.domain_detector import ProjectDomain


class TeamAssembler:
    """Assembles specialist teams for different project domains."""
    
    # Specialist definitions
    SPECIALISTS = {
        'engagement_manager': {
            'name': 'Jennifer Martinez',
            'title': 'Engagement Manager',
            'expertise': 'Client Relations, Project Coordination',
            'always_included': True
        },
        'strategist': {
            'name': 'Alex',
            'title': 'Product Strategist',
            'expertise': 'Business Strategy, Market Analysis'
        },
        'analyst': {
            'name': 'Jordan',
            'title': 'Lead Business Analyst',
            'expertise': 'Requirements Gathering, Stakeholder Mapping'
        },
        'architect': {
            'name': 'Dr. Sarah Chen',
            'title': 'Solutions Architect',
            'expertise': 'System Design, Technical Architecture'
        },
        'pm': {
            'name': 'Robert Taylor',
            'title': 'Project Manager',
            'expertise': 'Timeline Planning, Risk Management'
        },
        'ml_specialist': {
            'name': 'Dr. Michael Zhang',
            'title': 'Quantitative Researcher',
            'expertise': 'Machine Learning, Data Science'
        },
        'ux': {
            'name': 'Maya Patel',
            'title': 'UX Strategist',
            'expertise': 'User Experience, Design Systems'
        },
        'devops': {
            'name': 'Carlos Rodriguez',
            'title': 'DevOps Lead',
            'expertise': 'Infrastructure, Deployment'
        },
        'security': {
            'name': 'Lisa Chang',
            'title': 'Security Architect',
            'expertise': 'Security Controls, Compliance'
        },
        'quant_researcher': {
            'name': 'Dr. Michael Zhang',
            'title': 'Quantitative Researcher',
            'expertise': 'Trading Algorithms, Risk Analytics'
        },
        'risk_director': {
            'name': 'Victoria Chen',
            'title': 'Risk Management Director',
            'expertise': 'Portfolio Risk, Compliance'
        },
        'trading_architect': {
            'name': 'David Kim',
            'title': 'Trading Systems Architect',
            'expertise': 'Low-Latency Systems, Market Data'
        },
        'robotics_engineer': {
            'name': 'Dr. Thomas Anderson',
            'title': 'Robotics Engineer',
            'expertise': 'Control Systems, Embedded Software'
        },
        'hardware_architect': {
            'name': 'Elena Volkov',
            'title': 'Hardware Systems Architect',
            'expertise': 'Embedded Systems, IoT Architecture'
        },
        'data_engineer': {
            'name': 'Priya Sharma',
            'title': 'Data Platform Engineer',
            'expertise': 'Data Pipelines, Analytics Infrastructure'
        }
    }
    
    # Domain-specific team compositions
    DOMAIN_TEAMS = {
        ProjectDomain.QUANTITATIVE_TRADING: [
            'engagement_manager',
            'strategist',
            'quant_researcher',
            'risk_director',
            'trading_architect',
            'data_engineer',
            'security',
            'pm'
        ],
        ProjectDomain.ROBOTICS_IOT: [
            'engagement_manager',
            'strategist',
            'robotics_engineer',
            'hardware_architect',
            'architect',
            'security',
            'devops',
            'pm'
        ],
        ProjectDomain.AI_ML: [
            'engagement_manager',
            'strategist',
            'analyst',
            'ml_specialist',
            'data_engineer',
            'architect',
            'devops',
            'pm'
        ],
        ProjectDomain.HEALTHCARE: [
            'engagement_manager',
            'strategist',
            'analyst',
            'architect',
            'security',
            'devops',
            'ux',
            'pm'
        ],
        ProjectDomain.ECOMMERCE: [
            'engagement_manager',
            'strategist',
            'analyst',
            'architect',
            'ux',
            'data_engineer',
            'devops',
            'pm'
        ],
        ProjectDomain.SOFTWARE_DEVELOPMENT: [
            'engagement_manager',
            'strategist',
            'analyst',
            'architect',
            'ux',
            'devops',
            'security',
            'pm'
        ],
        ProjectDomain.FINTECH: [
            'engagement_manager',
            'strategist',
            'analyst',
            'architect',
            'security',
            'devops',
            'pm'
        ],
        ProjectDomain.GENERAL: [
            'engagement_manager',
            'strategist',
            'analyst',
            'architect',
            'pm'
        ]
    }
    
    @classmethod
    def assemble_team(cls, domain: ProjectDomain) -> list[dict]:
        """
        Assemble specialist team for given domain.
        
        Returns:
            List of specialist dictionaries with name, title, expertise
        """
        team_roles = cls.DOMAIN_TEAMS.get(domain, cls.DOMAIN_TEAMS[ProjectDomain.GENERAL])
        
        team = []
        for role_key in team_roles:
            if role_key in cls.SPECIALISTS:
                specialist = cls.SPECIALISTS[role_key].copy()
                specialist['role_key'] = role_key
                team.append(specialist)
        
        return team
    
    @classmethod
    def format_team_introduction(cls, domain: ProjectDomain, client_name: str = "") -> str:
        """
        Format team introduction message.
        
        Args:
            domain: Project domain
            client_name: Client name for personalization
            
        Returns:
            Formatted team introduction string
        """
        team = cls.assemble_team(domain)
        
        greeting = f"Hello{' ' + client_name if client_name else ''}! "
        intro = f"I've assembled a specialist team for your {cls._get_domain_name(domain)} project:\n\n"
        
        # Format team list
        team_list = []
        for specialist in team:
            team_list.append(f"• **{specialist['name']}**, {specialist['title']}")
        
        return greeting + intro + "\n".join(team_list)
    
    @staticmethod
    def _get_domain_name(domain: ProjectDomain) -> str:
        """Get friendly domain name."""
        from consulting_firm.domain_detector import DomainDetector
        return DomainDetector.get_domain_description(domain)
    
    @classmethod
    def get_specialist_by_role(cls, role_key: str) -> dict:
        """Get specialist info by role key."""
        return cls.SPECIALISTS.get(role_key, {
            'name': 'Consultant',
            'title': 'Specialist',
            'expertise': 'General Consulting'
        })
