"""
Comprehensive Feasibility Analysis System

This module provides sophisticated feasibility analysis capabilities that:
- Analyzes technical feasibility from multiple perspectives
- Assesses business viability and market fit
- Evaluates resource requirements and constraints
- Provides risk assessment and mitigation strategies
- Integrates with conversation context for personalized analysis
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_client import ModelClient
from consulting_personas import CONSULTING_PERSONAS


class FeasibilityCategory(Enum):
    """Categories of feasibility analysis."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    MARKET = "market"
    RESOURCE = "resource"
    TIMELINE = "timeline"


class RiskLevel(Enum):
    """Risk levels for feasibility assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FeasibilityAssessment:
    """Represents a feasibility assessment result."""
    category: FeasibilityCategory
    feasibility_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    key_findings: List[str]
    risks: List[str]
    recommendations: List[str]
    dependencies: List[str]
    assumptions: List[str]


@dataclass
class ComprehensiveFeasibilityReport:
    """Comprehensive feasibility report."""
    overall_feasibility_score: float
    overall_risk_level: RiskLevel
    assessments: Dict[FeasibilityCategory, FeasibilityAssessment]
    critical_risks: List[str]
    key_recommendations: List[str]
    go_no_go_recommendation: str
    next_steps: List[str]
    generated_at: datetime


class FeasibilityAnalyzer:
    """Comprehensive feasibility analysis system."""
    
    def __init__(self, model_client: ModelClient):
        self.model = model_client
        
    def analyze_comprehensive_feasibility(self, conversation_context: Dict[str, Any]) -> ComprehensiveFeasibilityReport:
        """Perform comprehensive feasibility analysis based on conversation context."""
        
        # Extract key information from conversation
        client_profile = conversation_context.get("client_profile", {})
        project_description = client_profile.get("project_description", "")
        project_domain = conversation_context.get("project_domain", "general")
        discovered_requirements = conversation_context.get("discovered_requirements", {})
        
        # Perform assessments for each category
        assessments = {}
        
        # Technical Feasibility
        assessments[FeasibilityCategory.TECHNICAL] = self._assess_technical_feasibility(
            project_description, project_domain, discovered_requirements
        )
        
        # Business Feasibility
        assessments[FeasibilityCategory.BUSINESS] = self._assess_business_feasibility(
            client_profile, project_description, project_domain
        )
        
        # Financial Feasibility
        assessments[FeasibilityCategory.FINANCIAL] = self._assess_financial_feasibility(
            client_profile, project_description, discovered_requirements
        )
        
        # Operational Feasibility
        assessments[FeasibilityCategory.OPERATIONAL] = self._assess_operational_feasibility(
            client_profile, project_description, discovered_requirements
        )
        
        # Regulatory Feasibility
        assessments[FeasibilityCategory.REGULATORY] = self._assess_regulatory_feasibility(
            client_profile, project_description, project_domain
        )
        
        # Market Feasibility
        assessments[FeasibilityCategory.MARKET] = self._assess_market_feasibility(
            client_profile, project_description, project_domain
        )
        
        # Resource Feasibility
        assessments[FeasibilityCategory.RESOURCE] = self._assess_resource_feasibility(
            client_profile, project_description, discovered_requirements
        )
        
        # Timeline Feasibility
        assessments[FeasibilityCategory.TIMELINE] = self._assess_timeline_feasibility(
            client_profile, project_description, discovered_requirements
        )
        
        # Calculate overall feasibility
        overall_score = self._calculate_overall_feasibility(assessments)
        overall_risk = self._calculate_overall_risk(assessments)
        
        # Generate recommendations
        critical_risks = self._identify_critical_risks(assessments)
        key_recommendations = self._generate_key_recommendations(assessments)
        go_no_go = self._generate_go_no_go_recommendation(overall_score, overall_risk, critical_risks)
        next_steps = self._generate_next_steps(assessments, go_no_go)
        
        return ComprehensiveFeasibilityReport(
            overall_feasibility_score=overall_score,
            overall_risk_level=overall_risk,
            assessments=assessments,
            critical_risks=critical_risks,
            key_recommendations=key_recommendations,
            go_no_go_recommendation=go_no_go,
            next_steps=next_steps,
            generated_at=datetime.now()
        )
    
    def _assess_technical_feasibility(self, project_description: str, project_domain: str, requirements: Dict[str, Any]) -> FeasibilityAssessment:
        """Assess technical feasibility."""
        prompt = f"""
PROJECT DESCRIPTION: {project_description}
PROJECT DOMAIN: {project_domain}
REQUIREMENTS: {requirements}

As a Solutions Architect, assess the technical feasibility of this project:

1. TECHNICAL COMPLEXITY: Rate complexity (1-10) and explain
2. TECHNOLOGY STACK: Assess technology choices and maturity
3. INTEGRATION CHALLENGES: Identify integration complexity
4. SCALABILITY REQUIREMENTS: Assess scalability needs vs. feasibility
5. PERFORMANCE REQUIREMENTS: Evaluate performance feasibility
6. SECURITY REQUIREMENTS: Assess security implementation feasibility

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("solutions_architect", prompt, system=CONSULTING_PERSONAS["solutions_architect"]["prompt"])
        
        # Parse response (simplified - in production use structured output)
        return self._parse_feasibility_response(response, FeasibilityCategory.TECHNICAL)
    
    def _assess_business_feasibility(self, client_profile: Dict[str, Any], project_description: str, project_domain: str) -> FeasibilityAssessment:
        """Assess business feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT: {client_profile.get('project_name', 'Unknown')}
PROJECT DESCRIPTION: {project_description}
PROJECT DOMAIN: {project_domain}

As a Product Strategist, assess the business feasibility of this project:

1. BUSINESS VALUE: Assess potential business value and ROI
2. MARKET FIT: Evaluate market demand and competitive landscape
3. STRATEGIC ALIGNMENT: Assess alignment with business strategy
4. STAKEHOLDER BUY-IN: Evaluate stakeholder support and commitment
5. COMPETITIVE ADVANTAGE: Assess competitive positioning
6. BUSINESS MODEL: Evaluate business model viability

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("product_strategist", prompt, system=CONSULTING_PERSONAS["product_strategist"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.BUSINESS)
    
    def _assess_financial_feasibility(self, client_profile: Dict[str, Any], project_description: str, requirements: Dict[str, Any]) -> FeasibilityAssessment:
        """Assess financial feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
REQUIREMENTS: {requirements}

As a Project Manager with financial expertise, assess the financial feasibility:

1. BUDGET REQUIREMENTS: Estimate total project cost
2. ROI POTENTIAL: Assess return on investment potential
3. FUNDING AVAILABILITY: Evaluate funding sources and availability
4. COST-BENEFIT ANALYSIS: Compare costs vs. benefits
5. FINANCIAL RISKS: Identify financial risks and constraints
6. PAYBACK PERIOD: Estimate payback period

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("project_manager", prompt, system=CONSULTING_PERSONAS["project_manager"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.FINANCIAL)
    
    def _assess_operational_feasibility(self, client_profile: Dict[str, Any], project_description: str, requirements: Dict[str, Any]) -> FeasibilityAssessment:
        """Assess operational feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
REQUIREMENTS: {requirements}

As a DevOps Engineer, assess the operational feasibility:

1. INFRASTRUCTURE REQUIREMENTS: Assess infrastructure needs
2. OPERATIONAL COMPLEXITY: Evaluate operational complexity
3. MAINTENANCE REQUIREMENTS: Assess ongoing maintenance needs
4. SCALABILITY OPERATIONS: Evaluate operational scalability
5. MONITORING & OBSERVABILITY: Assess monitoring requirements
6. DISASTER RECOVERY: Evaluate disaster recovery feasibility

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("devops_engineer", prompt, system=CONSULTING_PERSONAS["devops_engineer"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.OPERATIONAL)
    
    def _assess_regulatory_feasibility(self, client_profile: Dict[str, Any], project_description: str, project_domain: str) -> FeasibilityAssessment:
        """Assess regulatory feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
PROJECT DOMAIN: {project_domain}

As a Security Specialist, assess the regulatory feasibility:

1. REGULATORY REQUIREMENTS: Identify applicable regulations
2. COMPLIANCE COMPLEXITY: Assess compliance complexity
3. DATA PROTECTION: Evaluate data protection requirements
4. PRIVACY REGULATIONS: Assess privacy regulation compliance
5. INDUSTRY STANDARDS: Evaluate industry-specific standards
6. AUDIT REQUIREMENTS: Assess audit and reporting requirements

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("security_specialist", prompt, system=CONSULTING_PERSONAS["security_specialist"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.REGULATORY)
    
    def _assess_market_feasibility(self, client_profile: Dict[str, Any], project_description: str, project_domain: str) -> FeasibilityAssessment:
        """Assess market feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
PROJECT DOMAIN: {project_domain}

As a Product Strategist, assess the market feasibility:

1. MARKET SIZE: Assess target market size and growth
2. COMPETITIVE LANDSCAPE: Evaluate competitive environment
3. CUSTOMER DEMAND: Assess customer demand and needs
4. MARKET TIMING: Evaluate market timing and readiness
5. DISTRIBUTION CHANNELS: Assess distribution channel feasibility
6. MARKET BARRIERS: Identify market entry barriers

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("product_strategist", prompt, system=CONSULTING_PERSONAS["product_strategist"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.MARKET)
    
    def _assess_resource_feasibility(self, client_profile: Dict[str, Any], project_description: str, requirements: Dict[str, Any]) -> FeasibilityAssessment:
        """Assess resource feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
REQUIREMENTS: {requirements}

As a Project Manager, assess the resource feasibility:

1. HUMAN RESOURCES: Assess team availability and skills
2. TECHNICAL RESOURCES: Evaluate technical resource requirements
3. INFRASTRUCTURE RESOURCES: Assess infrastructure resource needs
4. EXTERNAL DEPENDENCIES: Identify external resource dependencies
5. RESOURCE CONSTRAINTS: Evaluate resource limitations
6. RESOURCE SCALABILITY: Assess resource scalability needs

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("project_manager", prompt, system=CONSULTING_PERSONAS["project_manager"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.RESOURCE)
    
    def _assess_timeline_feasibility(self, client_profile: Dict[str, Any], project_description: str, requirements: Dict[str, Any]) -> FeasibilityAssessment:
        """Assess timeline feasibility."""
        prompt = f"""
CLIENT: {client_profile.get('client_name', 'Unknown')}
ORGANIZATION: {client_profile.get('organization', 'Not specified')}
PROJECT DESCRIPTION: {project_description}
REQUIREMENTS: {requirements}

As a Project Manager, assess the timeline feasibility:

1. PROJECT COMPLEXITY: Assess project complexity and timeline impact
2. RESOURCE AVAILABILITY: Evaluate resource availability timeline
3. DEPENDENCIES: Identify timeline dependencies and constraints
4. MILESTONE FEASIBILITY: Assess milestone achievability
5. RISK FACTORS: Identify timeline risk factors
6. BUFFER REQUIREMENTS: Assess need for timeline buffers

Provide:
- Feasibility score (0.0-1.0)
- Risk level (low/medium/high/critical)
- Key findings (3-5 points)
- Risks (3-5 points)
- Recommendations (3-5 points)
- Dependencies (2-3 points)
- Assumptions (2-3 points)
"""
        
        response = self.model.generate("project_manager", prompt, system=CONSULTING_PERSONAS["project_manager"]["prompt"])
        
        return self._parse_feasibility_response(response, FeasibilityCategory.TIMELINE)
    
    def _parse_feasibility_response(self, response: str, category: FeasibilityCategory) -> FeasibilityAssessment:
        """Parse feasibility assessment response."""
        # Simplified parsing - in production use structured output
        lines = response.split('\n')
        
        # Extract feasibility score (look for number between 0.0 and 1.0)
        feasibility_score = 0.7  # Default
        for line in lines:
            if "feasibility score" in line.lower() or "score" in line.lower():
                try:
                    # Extract number from line
                    import re
                    numbers = re.findall(r'0\.\d+', line)
                    if numbers:
                        feasibility_score = float(numbers[0])
                        break
                except:
                    pass
        
        # Extract risk level
        risk_level = RiskLevel.MEDIUM  # Default
        for line in lines:
            line_lower = line.lower()
            if "risk level" in line_lower or "risk:" in line_lower:
                if "low" in line_lower:
                    risk_level = RiskLevel.LOW
                elif "medium" in line_lower:
                    risk_level = RiskLevel.MEDIUM
                elif "high" in line_lower:
                    risk_level = RiskLevel.HIGH
                elif "critical" in line_lower:
                    risk_level = RiskLevel.CRITICAL
                break
        
        # Extract key findings, risks, recommendations, etc.
        key_findings = self._extract_list_items(response, "key findings")
        risks = self._extract_list_items(response, "risks")
        recommendations = self._extract_list_items(response, "recommendations")
        dependencies = self._extract_list_items(response, "dependencies")
        assumptions = self._extract_list_items(response, "assumptions")
        
        return FeasibilityAssessment(
            category=category,
            feasibility_score=feasibility_score,
            risk_level=risk_level,
            key_findings=key_findings,
            risks=risks,
            recommendations=recommendations,
            dependencies=dependencies,
            assumptions=assumptions
        )
    
    def _extract_list_items(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section."""
        items = []
        lines = text.split('\n')
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            if section_name.lower() in line_lower:
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith('-') or line.strip().startswith('•') or line.strip().startswith('*'):
                    items.append(line.strip()[1:].strip())
                elif line.strip() and not line.strip().startswith('#'):
                    items.append(line.strip())
                elif line.strip().startswith('#'):
                    break
        
        return items[:5]  # Limit to 5 items
    
    def _calculate_overall_feasibility(self, assessments: Dict[FeasibilityCategory, FeasibilityAssessment]) -> float:
        """Calculate overall feasibility score."""
        if not assessments:
            return 0.0
        
        scores = [assessment.feasibility_score for assessment in assessments.values()]
        return sum(scores) / len(scores)
    
    def _calculate_overall_risk(self, assessments: Dict[FeasibilityCategory, FeasibilityAssessment]) -> RiskLevel:
        """Calculate overall risk level."""
        if not assessments:
            return RiskLevel.MEDIUM
        
        risk_levels = [assessment.risk_level for assessment in assessments.values()]
        
        # Return highest risk level
        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_critical_risks(self, assessments: Dict[FeasibilityCategory, FeasibilityAssessment]) -> List[str]:
        """Identify critical risks across all assessments."""
        critical_risks = []
        
        for assessment in assessments.values():
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                critical_risks.extend(assessment.risks[:2])  # Top 2 risks per category
        
        return critical_risks[:10]  # Limit to 10 critical risks
    
    def _generate_key_recommendations(self, assessments: Dict[FeasibilityCategory, FeasibilityAssessment]) -> List[str]:
        """Generate key recommendations across all assessments."""
        recommendations = []
        
        for assessment in assessments.values():
            recommendations.extend(assessment.recommendations[:2])  # Top 2 recommendations per category
        
        return recommendations[:10]  # Limit to 10 key recommendations
    
    def _generate_go_no_go_recommendation(self, overall_score: float, overall_risk: RiskLevel, critical_risks: List[str]) -> str:
        """Generate go/no-go recommendation."""
        if overall_score >= 0.8 and overall_risk in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            return "GO - Project is highly feasible with manageable risks"
        elif overall_score >= 0.6 and overall_risk == RiskLevel.MEDIUM:
            return "CONDITIONAL GO - Project is feasible but requires risk mitigation"
        elif overall_score >= 0.4 and overall_risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            return "CAUTIOUS GO - Project has significant challenges but may be viable with major changes"
        else:
            return "NO GO - Project has critical feasibility issues that need to be resolved"
    
    def _generate_next_steps(self, assessments: Dict[FeasibilityCategory, FeasibilityAssessment], go_no_go: str) -> List[str]:
        """Generate next steps based on assessment results."""
        next_steps = []
        
        if "GO" in go_no_go:
            next_steps.extend([
                "Proceed with detailed project planning",
                "Finalize resource allocation and timeline",
                "Begin stakeholder communication and buy-in",
                "Start detailed technical design"
            ])
        elif "CONDITIONAL" in go_no_go:
            next_steps.extend([
                "Address identified risks before proceeding",
                "Develop risk mitigation strategies",
                "Reassess feasibility after risk mitigation",
                "Consider phased approach to reduce risk"
            ])
        elif "CAUTIOUS" in go_no_go:
            next_steps.extend([
                "Conduct additional feasibility analysis",
                "Consider alternative approaches or scope reduction",
                "Address critical feasibility issues",
                "Reassess project viability"
            ])
        else:
            next_steps.extend([
                "Conduct root cause analysis of feasibility issues",
                "Consider alternative project approaches",
                "Reassess project scope and objectives",
                "Evaluate project cancellation or postponement"
            ])
        
        return next_steps
    
    def generate_feasibility_report(self, report: ComprehensiveFeasibilityReport) -> str:
        """Generate a comprehensive feasibility report."""
        report_text = f"""# Comprehensive Feasibility Analysis Report

**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Overall Feasibility Score:** {report.overall_feasibility_score:.2f}/1.0
**Overall Risk Level:** {report.overall_risk_level.value.title()}
**Recommendation:** {report.go_no_go_recommendation}

---

## Detailed Assessment by Category

"""
        
        for category, assessment in report.assessments.items():
            report_text += f"""### {category.value.title()} Feasibility

**Score:** {assessment.feasibility_score:.2f}/1.0
**Risk Level:** {assessment.risk_level.value.title()}

**Key Findings:**
"""
            for finding in assessment.key_findings:
                report_text += f"- {finding}\n"
            
            report_text += f"""
**Risks:**
"""
            for risk in assessment.risks:
                report_text += f"- {risk}\n"
            
            report_text += f"""
**Recommendations:**
"""
            for rec in assessment.recommendations:
                report_text += f"- {rec}\n"
            
            report_text += f"""
**Dependencies:**
"""
            for dep in assessment.dependencies:
                report_text += f"- {dep}\n"
            
            report_text += f"""
**Assumptions:**
"""
            for assumption in assessment.assumptions:
                report_text += f"- {assumption}\n"
            
            report_text += "\n---\n\n"
        
        report_text += f"""## Critical Risks

"""
        for risk in report.critical_risks:
            report_text += f"- {risk}\n"
        
        report_text += f"""

## Key Recommendations

"""
        for rec in report.key_recommendations:
            report_text += f"- {rec}\n"
        
        report_text += f"""

## Next Steps

"""
        for step in report.next_steps:
            report_text += f"- {step}\n"
        
        return report_text
