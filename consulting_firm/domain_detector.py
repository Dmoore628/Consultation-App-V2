"""
Domain detection and classification module.

Analyzes user input and document context to determine project domain,
enabling appropriate specialist team assembly.
"""

from enum import Enum
import re


class ProjectDomain(Enum):
    """Project domain classifications."""
    SOFTWARE_DEVELOPMENT = "software_development"
    AI_ML = "ai_ml"
    QUANTITATIVE_TRADING = "quantitative_trading"
    ROBOTICS_IOT = "robotics_iot"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    GENERAL = "general"


class DomainDetector:
    """Detects project domain from user input and context."""
    
    # Domain-specific keyword patterns
    DOMAIN_PATTERNS = {
        ProjectDomain.QUANTITATIVE_TRADING: [
            r'\b(trading|trader|futures|options|portfolio|quant|quantitative)\b',
            r'\b(alpha|beta|sharpe|drawdown|backtest|strategy)\b',
            r'\b(market|tick|order|execution|risk management)\b',
            r'\b(algorithmic trading|high frequency|market making)\b'
        ],
        ProjectDomain.ROBOTICS_IOT: [
            r'\b(robot|robotic|automation|iot|sensor|actuator)\b',
            r'\b(hardware|embedded|firmware|microcontroller)\b',
            r'\b(ros|gazebo|plc|scada|industrial)\b',
            r'\b(telemetry|control system|motion planning)\b'
        ],
        ProjectDomain.AI_ML: [
            r'\b(ai|artificial intelligence|machine learning|ml|deep learning)\b',
            r'\b(neural|network|model|training|inference)\b',
            r'\b(nlp|computer vision|cv|recommendation)\b',
            r'\b(tensorflow|pytorch|scikit|hugging face)\b'
        ],
        ProjectDomain.FINTECH: [
            r'\b(fintech|payment|banking|financial services)\b',
            r'\b(blockchain|crypto|defi|wallet)\b',
            r'\b(transaction|ledger|settlement|compliance)\b'
        ],
        ProjectDomain.HEALTHCARE: [
            r'\b(healthcare|medical|clinical|patient|diagnosis)\b',
            r'\b(ehr|emr|hipaa|fhir|hl7)\b',
            r'\b(telemedicine|health record|pharma)\b'
        ],
        ProjectDomain.ECOMMERCE: [
            r'\b(ecommerce|e-commerce|retail|shopping|marketplace)\b',
            r'\b(cart|checkout|inventory|fulfillment)\b',
            r'\b(product catalog|order management)\b'
        ],
        ProjectDomain.SOFTWARE_DEVELOPMENT: [
            r'\b(web app|mobile app|saas|platform|api)\b',
            r'\b(microservice|backend|frontend|full stack)\b',
            r'\b(react|angular|vue|node|django|flask)\b'
        ]
    }
    
    @classmethod
    def detect(cls, user_input: str, document_context: str = "", industry_hint: str = "") -> ProjectDomain:
        """
        Detect project domain from multiple sources.
        
        Args:
            user_input: User's description of their project
            document_context: Context from uploaded documents (filenames, content)
            industry_hint: Explicit industry selection from intake form
            
        Returns:
            ProjectDomain enum value
        """
        # Combine all context
        combined_text = f"{user_input} {document_context} {industry_hint}".lower()
        
        # Check industry hint first (explicit selection)
        if industry_hint:
            explicit_domain = cls._map_industry_to_domain(industry_hint)
            if explicit_domain != ProjectDomain.GENERAL:
                return explicit_domain
        
        # Score each domain based on keyword matches
        scores = {}
        for domain, patterns in cls.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
                score += matches
            scores[domain] = score
        
        # Return domain with highest score, or GENERAL if no strong match
        if not scores or max(scores.values()) == 0:
            return ProjectDomain.GENERAL
        
        # Require at least 2 matches for confidence
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] >= 2:
            return best_domain
        
        return ProjectDomain.GENERAL
    
    @staticmethod
    def _map_industry_to_domain(industry: str) -> ProjectDomain:
        """Map intake form industry selection to domain."""
        industry_lower = industry.lower()
        
        if "trading" in industry_lower or "financial services" in industry_lower:
            return ProjectDomain.QUANTITATIVE_TRADING
        elif "robotics" in industry_lower or "iot" in industry_lower or "hardware" in industry_lower:
            return ProjectDomain.ROBOTICS_IOT
        elif "ai" in industry_lower or "machine learning" in industry_lower:
            return ProjectDomain.AI_ML
        elif "healthcare" in industry_lower or "life sciences" in industry_lower:
            return ProjectDomain.HEALTHCARE
        elif "ecommerce" in industry_lower or "retail" in industry_lower:
            return ProjectDomain.ECOMMERCE
        elif "software" in industry_lower or "saas" in industry_lower:
            return ProjectDomain.SOFTWARE_DEVELOPMENT
        
        return ProjectDomain.GENERAL
    
    @staticmethod
    def get_domain_description(domain: ProjectDomain) -> str:
        """Get human-readable description of domain."""
        descriptions = {
            ProjectDomain.QUANTITATIVE_TRADING: "Quantitative Trading & Financial Systems",
            ProjectDomain.ROBOTICS_IOT: "Robotics, IoT & Hardware Systems",
            ProjectDomain.AI_ML: "AI & Machine Learning",
            ProjectDomain.FINTECH: "Financial Technology",
            ProjectDomain.HEALTHCARE: "Healthcare & Life Sciences",
            ProjectDomain.ECOMMERCE: "E-commerce & Retail",
            ProjectDomain.SOFTWARE_DEVELOPMENT: "Software Development",
            ProjectDomain.GENERAL: "General Consulting"
        }
        return descriptions.get(domain, "General Consulting")
