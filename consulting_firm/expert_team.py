import os
import sys
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_client import ModelClient, render_role_prompt
from agent_coordinator import AgentCoordinator, AgentRole


class ExpertTeam:
    """Expert team implementing TRUE multi-agent coordination
    
    Features:
    - Agent-to-agent peer review and collaboration
    - Cross-functional validation
    - Iterative refinement with feedback loops
    - Quality gates and approval workflows
    - Parallel task execution where possible
    - Synthesis of multiple agent perspectives

    Implements a sophisticated multi-agent orchestration where specialist roles:
    1. Work in parallel on independent tasks
    2. Review each other's work (peer review)
    3. Provide feedback and request revisions
    4. Synthesize outputs into coherent deliverables
    5. Validate through quality assurance gates
    """

    def __init__(self, outputs_path: str = "outputs", model_provider: str | None = None, log_callback=None):
        self.outputs_path = outputs_path
        self.model = ModelClient(model_provider)
        self.coordinator = AgentCoordinator(self.model, log_callback=log_callback)
        self.log_callback = log_callback or (lambda msg: None)
        
    def _log(self, message: str):
        """Send progress message to callback"""
        self.log_callback(message)

    def _write(self, path: str, text: str):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def _gather_project_context(self, project_path: str) -> str:
        """Read any files under project_documents/ and build a brief context block.

        Includes up to ~8000 characters combined to avoid blowing past token limits.
        """
        docs_dir = os.path.join(project_path, "project_documents")
        if not os.path.isdir(docs_dir):
            return "(No prior documents provided.)"
        parts = []
        total = 0
        for root, _, files in os.walk(docs_dir):
            for fn in sorted(files):
                fp = os.path.join(root, fn)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                        txt = f.read()
                    rel = os.path.relpath(fp, project_path)
                    snippet = txt[:4000]
                    parts.append(f"\n---\nFile: {rel}\n\n{snippet}")
                    total += len(snippet)
                    if total > 8000:
                        parts.append("\n(Note: Additional content truncated.)")
                        break
                except Exception:
                    continue
            if total > 8000:
                break
        return "".join(parts) if parts else "(project_documents/ exists but no readable files)"

    def run(self, project_path: str, maturity: str, previous_sow: str | None = None, feedback: str | None = None, use_multi_agent: bool = True) -> Dict[str, str]:
        """Run deliverable generation with option for true multi-agent coordination.
        
        Args:
            project_path: Path to project documents
            maturity: Project maturity level
            previous_sow: Previous SOW text for refinement
            feedback: Validation feedback to address
            use_multi_agent: If True, use advanced multi-agent coordination with peer review
        
        Returns:
            Dict of artifact paths
        """
        os.makedirs(self.outputs_path, exist_ok=True)
        artifacts: Dict[str, str] = {}

        discovery_path = os.path.join(self.outputs_path, "01_discovery_report.md")
        sow_path = os.path.join(self.outputs_path, "02_scope_of_work.md")
        tech_path = os.path.join(self.outputs_path, "03_technical_architecture.md")
        roadmap_path = os.path.join(self.outputs_path, "04_implementation_roadmap.md")
        coordination_report_path = os.path.join(self.outputs_path, "00_agent_coordination_report.md")

        # Gather context
        ctx = f"Project path: {project_path}\nMaturity: {maturity}"
        docs_context = self._gather_project_context(project_path)
        if docs_context:
            ctx += "\n\nProvided Documents:\n" + docs_context
        
        context_dict = {
            "user_input": ctx,
            "documents": docs_context,
            "maturity": maturity,
            "previous_sow": previous_sow,
            "feedback": feedback
        }
        
        if use_multi_agent:
            # Use true multi-agent coordination with peer review
            return self._run_multi_agent_workflow(context_dict, artifacts)
        else:
            # Use original sequential workflow
            return self._run_sequential_workflow(context_dict, artifacts)
    
    def _run_multi_agent_workflow(self, context: Dict, artifacts: Dict[str, str]) -> Dict[str, str]:
        """Run with true multi-agent coordination, peer review, and quality gates."""
        
        self._log("🤖 Initiating Multi-Agent Coordination System")
        self._log("=" * 60)
        
        # Phase 1: Discovery with multi-agent collaboration
        self._log("\n📋 PHASE 1: Collaborative Discovery")
        discovery_tasks = self.coordinator.create_discovery_workflow(context)
        discovery_outputs = self.coordinator.execute_workflow(discovery_tasks, max_iterations=2)
        
        # Synthesize discovery report
        discovery_text = self._synthesize_discovery(discovery_outputs)
        discovery_path = os.path.join(self.outputs_path, "01_discovery_report.md")
        self._write(discovery_path, discovery_text)
        artifacts['discovery'] = discovery_path
        self._log("✅ Collaborative Discovery Report completed with peer reviews")
        
        # Phase 2: SOW with multi-agent coordination
        self._log("\n📝 PHASE 2: Collaborative Scope of Work")
        sow_tasks = self.coordinator.create_sow_workflow(context, discovery_text)
        sow_outputs = self.coordinator.execute_workflow(sow_tasks, max_iterations=2)
        
        # Synthesize SOW
        sow_text = self._synthesize_sow(sow_outputs)
        sow_path = os.path.join(self.outputs_path, "02_scope_of_work.md")
        self._write(sow_path, sow_text)
        artifacts['sow'] = sow_path
        self._log("✅ Collaborative Scope of Work completed with quality gates")
        
        # Generate coordination report
        coord_report = self.coordinator.generate_coordination_report()
        coord_path = os.path.join(self.outputs_path, "00_agent_coordination_report.md")
        self._write(coord_path, coord_report)
        self._log("📊 Multi-Agent Coordination Report saved")
        
        # Continue with technical architecture and roadmap (can be enhanced with multi-agent later)
        self._log("\n🏗️ PHASE 3: Technical Architecture")
        tech_text = self._generate_technical_architecture(context, sow_text)
        tech_path = os.path.join(self.outputs_path, "03_technical_architecture.md")
        self._write(tech_path, tech_text)
        artifacts['tech'] = tech_path
        
        self._log("\n🗺️ PHASE 4: Implementation Roadmap")
        roadmap_text = self._generate_roadmap(context, tech_text)
        roadmap_path = os.path.join(self.outputs_path, "04_implementation_roadmap.md")
        self._write(roadmap_path, roadmap_text)
        artifacts['roadmap'] = roadmap_path
        
        self._log("\n" + "=" * 60)
        self._log("🎉 Multi-Agent Workflow Complete!")
        self._log(f"   • {len(discovery_tasks)} discovery tasks with peer review")
        self._log(f"   • {len(sow_tasks)} SOW tasks with quality gates")
        self._log(f"   • Cross-functional validation throughout")
        
        return artifacts
    
    def _synthesize_discovery(self, outputs: Dict[str, str]) -> str:
        """Synthesize discovery outputs from multiple agents into coherent report."""
        report = "# Project Discovery Report\n\n"
        report += "*This report was collaboratively generated through multi-agent coordination with peer review*\n\n"
        report += "---\n\n"
        
        # Map task outputs to sections
        section_mapping = {
            "discovery_framing": "## Discovery Framework\n",
            "strategic_analysis": "## Strategic Analysis & Business Case\n",
            "requirements_analysis": "## Requirements & Stakeholder Analysis\n",
            "technical_feasibility": "## Technical Feasibility Assessment\n",
            "ml_feasibility": "## AI/ML Feasibility & Data Strategy\n",
            "ux_assessment": "## User Experience Requirements\n",
            "data_science_assessment": "## Data Science Assessment (Signals, Baselines, Evaluation)\n",
            "timeline_synthesis": "## Project Timeline & Milestones\n",
            "discovery_synthesis": "## Executive Summary\n"
        }
        
        # Add synthesis first (executive summary)
        if "discovery_synthesis" in outputs:
            report += section_mapping["discovery_synthesis"]
            report += outputs["discovery_synthesis"] + "\n\n"
        
        # Add other sections in logical order
        section_order = [
            "discovery_framing", "strategic_analysis", "requirements_analysis",
            "technical_feasibility", "ml_feasibility", "ux_assessment", "data_science_assessment", "timeline_synthesis"
        ]
        
        for task_id in section_order:
            if task_id in outputs and task_id != "discovery_synthesis":
                report += section_mapping.get(task_id, f"## {task_id}\n")
                report += outputs[task_id] + "\n\n"
        
        return report
    
    def _synthesize_sow(self, outputs: Dict[str, str]) -> str:
        """Synthesize SOW outputs from multiple agents into coherent document."""
        sow = "# Scope of Work\n\n"
        sow += "*This SOW was collaboratively generated through multi-agent coordination with quality assurance review*\n\n"
        sow += "---\n\n"
        
        section_mapping = {
            "sow_executive_summary": "## EXECUTIVE SUMMARY\n",
            "sow_scope_details": "## SCOPE & DELIVERABLES\n",
            "sow_technical_approach": "## TECHNICAL APPROACH\n",
            "sow_security_review": "## SECURITY & COMPLIANCE\n",
            "sow_project_plan": "## PROJECT PLAN & TIMELINE\n",
            "sow_final_synthesis": "## ENGAGEMENT OVERVIEW\n"
        }
        
        # Start with final synthesis if available
        if "sow_final_synthesis" in outputs:
            sow += section_mapping["sow_final_synthesis"]
            sow += outputs["sow_final_synthesis"] + "\n\n"
        
        # Add sections in logical order
        section_order = [
            "sow_executive_summary", "sow_scope_details", "sow_technical_approach",
            "sow_security_review", "sow_project_plan"
        ]
        
        for task_id in section_order:
            if task_id in outputs:
                sow += section_mapping.get(task_id, f"## {task_id}\n")
                sow += outputs[task_id] + "\n\n"
        
        return sow
    
    def _generate_technical_architecture(self, context: Dict, sow_text: str) -> str:
        """Generate technical architecture section."""
        ctx_str = context["user_input"]
        tech_context = ctx_str + "\n\nSOW Summary:\n" + sow_text[:3000]
        
        self._log("🏗️ Solution Architect designing system components...")
        arch_prompt = tech_context + "\n\nDesign the technical architecture with: 1) System components (with descriptions), 2) Component relationships (use format: ComponentA -> ComponentB), 3) Data flows, 4) Technology stack with justifications, 5) Scalability approach. Use clear, structured format."
        tech_prompt = render_role_prompt("architect", arch_prompt)
        tech_text = "# Technical Architecture\n\n"
        tech_text += "## System Architecture Overview\n" + self.model.generate("architect", tech_prompt)
        
        self._log("💻 Full-Stack Developer validating implementation...")
        fullstack_prompt = tech_context + "\n\nValidate implementation: 1) Key technical components with interfaces, 2) Development stack recommendations, 3) Implementation complexity assessment, 4) Potential technical challenges, 5) Recommended development phases. Be practical and realistic."
        tech_text += "\n\n## Implementation Validation\n" + self.model.generate("fullstack", render_role_prompt("fullstack", fullstack_prompt))
        
        self._log("⚙️ DevOps Engineer designing infrastructure...")
        devops_prompt = tech_context + "\n\nProvide infrastructure design: 1) Deployment topology (cloud provider, regions, services), 2) CI/CD pipeline approach, 3) Monitoring and observability, 4) Scalability and auto-scaling, 5) Disaster recovery (RTO/RPO), 6) Estimated infrastructure costs."
        tech_text += "\n\n## Infrastructure & DevOps\n" + self.model.generate("devops", render_role_prompt("devops", devops_prompt))
        
        self._log("🔒 Security Specialist reviewing security architecture...")
        security_prompt = tech_context + "\n\nProvide security architecture: 1) Threat model (key threats and attack vectors), 2) Security controls (preventive, detective, corrective), 3) Compliance requirements and approach, 4) Identity and access management, 5) Data protection (encryption, privacy), 6) Security monitoring and incident response."
        tech_text += "\n\n## Security Architecture\n" + self.model.generate("security", render_role_prompt("security", security_prompt))
        
        return tech_text
    
    def _generate_roadmap(self, context: Dict, tech_text: str) -> str:
        """Generate implementation roadmap section."""
        ctx_str = context["user_input"]
        roadmap_context = ctx_str + "\n\nTechnical Architecture Summary:\n" + tech_text[:2000]
        
        self._log("🗺️ Project Manager creating phased roadmap...")
        pm_roadmap_prompt = roadmap_context + "\n\nCreate a phased implementation roadmap with: 1) Phase 1: MVP (core features, duration, milestones), 2) Phase 2: Enhancements (additional features, duration), 3) Phase 3: Scale & Optimize (performance, scale, duration), 4) For each phase: objectives, key deliverables, success criteria, timeline. Include dependencies between phases."
        roadmap_text = "# Implementation Roadmap\n\n"
        roadmap_text += "## Phased Delivery Plan\n" + self.model.generate("pm", render_role_prompt("pm", pm_roadmap_prompt))
        
        self._log("⚙️ DevOps Engineer defining deployment milestones...")
        devops_roadmap_prompt = roadmap_context + "\n\nProvide deployment roadmap: 1) Key deployment milestones for each phase, 2) Infrastructure setup milestones, 3) Deployment gates and verification steps, 4) Performance and security testing checkpoints, 5) Go-live criteria and rollback procedures."
        roadmap_text += "\n\n## Deployment Milestones & Gates\n" + self.model.generate("devops", render_role_prompt("devops", devops_roadmap_prompt))
        
        return roadmap_text
    
    def _run_sequential_workflow(self, context: Dict, artifacts: Dict[str, str]) -> Dict[str, str]:
        """Original sequential workflow (kept for backward compatibility)."""
        ctx = context["user_input"]
        previous_sow = context.get("previous_sow")
        feedback = context.get("feedback")
        
        discovery_path = os.path.join(self.outputs_path, "01_discovery_report.md")
        sow_path = os.path.join(self.outputs_path, "02_scope_of_work.md")
        tech_path = os.path.join(self.outputs_path, "03_technical_architecture.md")
        roadmap_path = os.path.join(self.outputs_path, "04_implementation_roadmap.md")
        
        self._log("📋 Phase 1: Discovery - Sequential Mode")
        # Discovery implementation (original code)
        strategist_prompt = ctx + "\n\nAnalyze the business opportunity, strategic alignment, competitive positioning, and ROI potential. Identify key business goals and success metrics. Format as structured sections."
        strategist = render_role_prompt("strategist", strategist_prompt)
        
        analyst_prompt = ctx + "\n\nIdentify all stakeholders (internal and external), document high-level requirements, note initial gaps and assumptions, and flag early-stage risks. Use structured format with clear sections."
        analyst = render_role_prompt("analyst", analyst_prompt)
        
        pm_prompt = ctx + "\n\nProvide high-level project phases, key milestones with target durations, critical dependencies, and initial risk assessment. Include assumptions about team size and availability."
        pm_prompt_rendered = render_role_prompt("pm", pm_prompt)
        
        ml_prompt = ctx + "\n\nAssess AI/ML feasibility for stated goals. Identify data requirements (volume, quality, sources), recommend model approaches in plain language, estimate development effort, and note ethical considerations."
        ml_prompt_rendered = render_role_prompt("ml", ml_prompt)
        
        self._log("🎨 UX Strategist defining user experience requirements...")
        ux_prompt = ctx + "\n\nDefine target user personas, outline key user journeys and workflows, identify UX requirements and accessibility considerations. Focus on user needs and pain points."
        ux_prompt_rendered = render_role_prompt("ux", ux_prompt)

        discovery_text = "# Project Discovery Report\n\n"
        discovery_text += "## Business Strategy & Viability\n" + self.model.generate("strategist", strategist)
        discovery_text += "\n\n## Requirements & Stakeholder Analysis\n" + self.model.generate("analyst", analyst)
        discovery_text += "\n\n## Project Timeline & Milestones\n" + self.model.generate("pm", pm_prompt_rendered)
        discovery_text += "\n\n## AI/ML Feasibility Assessment\n" + self.model.generate("ml", ml_prompt_rendered)
        discovery_text += "\n\n## User Experience Requirements\n" + self.model.generate("ux", ux_prompt_rendered)
        self._write(discovery_path, discovery_text)
        self._log("✅ Discovery Report created")


        # SOW: compiled from multiple roles; include previous context and feedback if provided
        self._log("📝 Phase 2: Scope of Work Generation...")
        sow_context = ctx + "\n\nDiscovery Insights:\n" + discovery_text[:3000]  # Include discovery summary
        if previous_sow:
            sow_context += "\n\nPrior SOW Draft:\n" + previous_sow[:4000]
            self._log("🔄 Refining previous SOW draft based on validation feedback...")
        if feedback:
            sow_context += "\n\nValidator Feedback to Address:\n" + feedback[:2000]
            self._log(f"⚠️ Addressing validation feedback...")

        # Executive Summary
        exec_summary_prompt = sow_context + "\n\nWrite a compelling executive summary that includes: 1) Business problem and opportunity, 2) Proposed solution approach, 3) Expected business value and ROI, 4) Investment required (timeline, resources). Keep it executive-level and decision-focused."
        exec_summary = self.model.generate("strategist", render_role_prompt("strategist", exec_summary_prompt))
        
        # Success Criteria and KPIs
        success_prompt = sow_context + "\n\nDefine 5-7 specific, measurable success criteria and KPIs. Each should have: metric name, target value, measurement method, and business rationale. Focus on business outcomes, not technical metrics."
        success = self.model.generate("product", render_role_prompt("product", success_prompt))
        
        # Detailed Scope with Acceptance Criteria
        scope_prompt = sow_context + "\n\nProvide detailed scope: 1) In-scope deliverables with descriptions, 2) Out-of-scope items (explicitly listed), 3) For each major deliverable, provide 2-4 specific acceptance criteria. Be comprehensive but clear."
        scope = self.model.generate("analyst", render_role_prompt("analyst", scope_prompt))
        
        # Feature-Level Acceptance Criteria
        criteria_prompt = sow_context + "\n\nFor the top 5 most critical features/capabilities, provide specific acceptance criteria in format: Feature Name, Acceptance Criteria (3-5 measurable criteria), Priority (Must-Have/Should-Have/Nice-to-Have). Make criteria testable."
        criteria = self.model.generate("product", render_role_prompt("product", criteria_prompt))
        
        # Technical Approach
        tech_prompt = sow_context + "\n\nDescribe the technical approach: 1) High-level system architecture, 2) Key technology choices with business justification, 3) Data flows and integrations, 4) Security approach, 5) Scalability strategy. Explain in business terms with clear rationale."
        tech = self.model.generate("architect", render_role_prompt("architect", tech_prompt))
        
        # AI/ML Section
        ai_sec_prompt = sow_context + "\n\nProvide AI/ML section: 1) AI feasibility and approach, 2) Data requirements (sources, volume, quality), 3) Model development phases, 4) Performance targets, 5) Ethical AI considerations (bias, fairness, transparency), 6) Ongoing monitoring and maintenance."
        ai_sec = self.model.generate("ml", render_role_prompt("ml", ai_sec_prompt))
        
        # UX Requirements
        ux_sec_prompt = sow_context + "\n\nProvide UX requirements: 1) User personas (2-3 key personas), 2) Critical user journeys (3-5 journeys), 3) Usability requirements, 4) Accessibility standards (WCAG 2.1 AA), 5) Design system approach, 6) UX success metrics."
        ux_sec = self.model.generate("ux", render_role_prompt("ux", ux_sec_prompt))
        
        # Project Management Approach
        pm_sec_prompt = sow_context + "\n\nProvide comprehensive project plan: 1) Phased timeline with milestones and durations, 2) Resource requirements (roles, skills, FTE), 3) Risk register (top 5 risks with mitigation), 4) Project governance and communication plan, 5) Change management approach."
        pm_sec = self.model.generate("pm", render_role_prompt("pm", pm_sec_prompt))
        
        # Assumptions and Constraints
        assumptions_prompt = sow_context + "\n\nList critical assumptions and constraints: 1) Business assumptions, 2) Technical assumptions, 3) Resource/budget constraints, 4) Timeline constraints, 5) Dependencies on external parties. Be explicit and comprehensive."
        assumptions = self.model.generate("pm", render_role_prompt("pm", assumptions_prompt))

        sow_text = "# Scope of Work\n\n"
        sow_text += "## EXECUTIVE SUMMARY\n" + exec_summary + "\n\n"
        sow_text += "## SUCCESS CRITERIA & KPIs\n" + success + "\n\n"
        sow_text += "## SCOPE & DELIVERABLES\n" + scope + "\n\n"
        sow_text += "## ACCEPTANCE CRITERIA\n" + criteria + "\n\n"
        sow_text += "## TECHNICAL APPROACH\n" + tech + "\n\n"
        sow_text += "## AI/ML FEASIBILITY & DATA REQUIREMENTS\n" + ai_sec + "\n\n"
        sow_text += "## USER EXPERIENCE REQUIREMENTS\n" + ux_sec + "\n\n"
        sow_text += "## PROJECT MANAGEMENT\n" + pm_sec + "\n\n"
        sow_text += "## ASSUMPTIONS & CONSTRAINTS\n" + assumptions + "\n"
        self._write(sow_path, sow_text)
        self._log("✅ Scope of Work created")


        # Technical architecture: architect + fullstack + devops + security
        self._log("🏗️ Phase 3: Technical Architecture Design...")
        tech_context = ctx + "\n\nSOW Summary:\n" + sow_text[:3000]  # Include SOW context
        
        self._log("🏗️ Solution Architect designing system components and data flows...")
        arch_prompt = tech_context + "\n\nDesign the technical architecture with: 1) System components (with descriptions), 2) Component relationships (use format: ComponentA -> ComponentB), 3) Data flows, 4) Technology stack with justifications, 5) Scalability approach. Use clear, structured format."
        tech_prompt = render_role_prompt("architect", arch_prompt)
        tech_text = "# Technical Architecture\n\n"
        tech_text += "## System Architecture Overview\n" + self.model.generate("architect", tech_prompt)
        
        self._log("💻 Full-Stack Developer validating implementation approach...")
        fullstack_prompt = tech_context + "\n\nValidate implementation: 1) Key technical components with interfaces, 2) Development stack recommendations, 3) Implementation complexity assessment, 4) Potential technical challenges, 5) Recommended development phases. Be practical and realistic."
        tech_text += "\n\n## Implementation Validation\n" + self.model.generate("fullstack", render_role_prompt("fullstack", fullstack_prompt))
        
        self._log("⚙️ DevOps Engineer designing infrastructure and deployment...")
        devops_prompt = tech_context + "\n\nProvide infrastructure design: 1) Deployment topology (cloud provider, regions, services), 2) CI/CD pipeline approach, 3) Monitoring and observability, 4) Scalability and auto-scaling, 5) Disaster recovery (RTO/RPO), 6) Estimated infrastructure costs."
        tech_text += "\n\n## Infrastructure & DevOps\n" + self.model.generate("devops", render_role_prompt("devops", devops_prompt))
        
        self._log("🔒 Security Specialist reviewing security architecture...")
        security_prompt = tech_context + "\n\nProvide security architecture: 1) Threat model (key threats and attack vectors), 2) Security controls (preventive, detective, corrective), 3) Compliance requirements and approach, 4) Identity and access management, 5) Data protection (encryption, privacy), 6) Security monitoring and incident response."
        tech_text += "\n\n## Security Architecture\n" + self.model.generate("security", render_role_prompt("security", security_prompt))
        self._write(tech_path, tech_text)
        self._log("✅ Technical Architecture created")


        # Roadmap: pm + devops
        self._log("🗺️ Phase 4: Implementation Roadmap Creation...")
        roadmap_context = ctx + "\n\nTechnical Architecture Summary:\n" + tech_text[:2000]  # Include tech context
        
        self._log("🗺️ Project Manager creating phased implementation roadmap...")
        pm_roadmap_prompt = roadmap_context + "\n\nCreate a phased implementation roadmap with: 1) Phase 1: MVP (core features, duration, milestones), 2) Phase 2: Enhancements (additional features, duration), 3) Phase 3: Scale & Optimize (performance, scale, duration), 4) For each phase: objectives, key deliverables, success criteria, timeline. Include dependencies between phases."
        roadmap_text = "# Implementation Roadmap\n\n"
        roadmap_text += "## Phased Delivery Plan\n" + self.model.generate("pm", render_role_prompt("pm", pm_roadmap_prompt))
        
        self._log("⚙️ DevOps Engineer defining deployment milestones and gates...")
        devops_roadmap_prompt = roadmap_context + "\n\nProvide deployment roadmap: 1) Key deployment milestones for each phase, 2) Infrastructure setup milestones, 3) Deployment gates and verification steps, 4) Performance and security testing checkpoints, 5) Go-live criteria and rollback procedures."
        roadmap_text += "\n\n## Deployment Milestones & Gates\n" + self.model.generate("devops", render_role_prompt("devops", devops_roadmap_prompt))
        self._write(roadmap_path, roadmap_text)
        self._log("✅ Implementation Roadmap created")


        artifacts['discovery'] = discovery_path
        artifacts['sow'] = sow_path
        artifacts['tech'] = tech_path
        artifacts['roadmap'] = roadmap_path

        return artifacts


if __name__ == '__main__':
    et = ExpertTeam(outputs_path='outputs')
    print(et.run('.', 'Greenfield Discovery Path'))
