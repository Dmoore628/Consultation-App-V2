"""
Multi-Agent Coordination System

This module implements true multi-agent coordination with:
- Agent-to-agent communication and review
- Cross-functional validation and critique
- Collaborative refinement loops
- Quality gates and expert oversight
- Conflict resolution and synthesis
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json


class AgentRole(Enum):
    """Specialized agent roles in the consulting system."""
    ENGAGEMENT_MANAGER = "engagement_manager"
    STRATEGIST = "strategist"
    ANALYST = "analyst"
    ARCHITECT = "architect"
    ML_SPECIALIST = "ml_specialist"
    UX_STRATEGIST = "ux_strategist"
    SECURITY_SPECIALIST = "security_specialist"
    DEVOPS_ENGINEER = "devops_engineer"
    PROJECT_MANAGER = "project_manager"
    QUALITY_ASSURANCE = "quality_assurance"


class AgentTaskStatus(Enum):
    """Status of agent tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW_REQUIRED = "review_required"
    REVISION_NEEDED = "revision_needed"
    APPROVED = "approved"
    COMPLETED = "completed"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    task_id: str
    agent_role: AgentRole
    task_type: str  # e.g., "discovery", "requirements", "architecture"
    context: Dict[str, Any]
    dependencies: List[str]  # task_ids this depends on
    output: Optional[str] = None
    status: AgentTaskStatus = AgentTaskStatus.PENDING
    reviews: List[Dict[str, Any]] = None
    revision_count: int = 0
    
    def __post_init__(self):
        if self.reviews is None:
            self.reviews = []


@dataclass
class AgentReview:
    """Represents a peer review from one agent to another."""
    reviewer_role: AgentRole
    target_task_id: str
    approval: bool
    strengths: List[str]
    concerns: List[str]
    suggestions: List[str]
    critical_issues: List[str]
    confidence_score: float  # 0.0 to 1.0


class AgentCoordinator:
    """
    Coordinates multiple agents in a true multi-agent architecture.
    
    Features:
    - Task dependency management
    - Agent-to-agent peer review
    - Iterative refinement with feedback loops
    - Quality gates and approval workflows
    - Cross-functional validation
    - Conflict resolution and synthesis
    """
    
    def __init__(self, model_client, log_callback=None):
        self.model = model_client
        self.log = log_callback or (lambda msg: None)
        self.tasks: Dict[str, AgentTask] = {}
        self.agent_outputs: Dict[str, str] = {}
        self.coordination_history: List[Dict[str, Any]] = []
        
    def create_discovery_workflow(self, context: Dict[str, Any]) -> List[AgentTask]:
        """
        Create coordinated multi-agent discovery workflow.
        
        Workflow:
        1. Engagement Manager initiates and frames
        2. Strategist + Analyst work in parallel
        3. Cross-review between Strategist and Analyst
        4. Technical specialists (Architect, ML, UX) review and extend
        5. PM synthesizes and creates timeline
        6. Quality Assurance reviews all outputs
        7. Engagement Manager synthesizes final discovery
        """
        tasks = []
        
        # Task 1: Engagement Manager frames the discovery
        tasks.append(AgentTask(
            task_id="discovery_framing",
            agent_role=AgentRole.ENGAGEMENT_MANAGER,
            task_type="discovery_framing",
            context=context,
            dependencies=[]
        ))
        
        # Task 2 & 3: Parallel strategic and requirements analysis
        tasks.append(AgentTask(
            task_id="strategic_analysis",
            agent_role=AgentRole.STRATEGIST,
            task_type="strategic_analysis",
            context=context,
            dependencies=["discovery_framing"]
        ))
        
        tasks.append(AgentTask(
            task_id="requirements_analysis",
            agent_role=AgentRole.ANALYST,
            task_type="requirements_analysis",
            context=context,
            dependencies=["discovery_framing"]
        ))
        
        # Task 4 & 5: Cross-review between strategy and requirements
        tasks.append(AgentTask(
            task_id="strategy_review_by_analyst",
            agent_role=AgentRole.ANALYST,
            task_type="peer_review",
            context={"target": "strategic_analysis"},
            dependencies=["strategic_analysis", "requirements_analysis"]
        ))
        
        tasks.append(AgentTask(
            task_id="requirements_review_by_strategist",
            agent_role=AgentRole.STRATEGIST,
            task_type="peer_review",
            context={"target": "requirements_analysis"},
            dependencies=["strategic_analysis", "requirements_analysis"]
        ))
        
        # Task 6-8: Technical specialists analyze in parallel
        tasks.append(AgentTask(
            task_id="technical_feasibility",
            agent_role=AgentRole.ARCHITECT,
            task_type="technical_assessment",
            context=context,
            dependencies=["strategy_review_by_analyst", "requirements_review_by_strategist"]
        ))
        
        tasks.append(AgentTask(
            task_id="ml_feasibility",
            agent_role=AgentRole.ML_SPECIALIST,
            task_type="ml_assessment",
            context=context,
            dependencies=["strategy_review_by_analyst", "requirements_review_by_strategist"]
        ))
        
        tasks.append(AgentTask(
            task_id="ux_assessment",
            agent_role=AgentRole.UX_STRATEGIST,
            task_type="ux_assessment",
            context=context,
            dependencies=["requirements_analysis"]
        ))
        
        # Task 9: Project Manager synthesizes timeline
        tasks.append(AgentTask(
            task_id="timeline_synthesis",
            agent_role=AgentRole.PROJECT_MANAGER,
            task_type="timeline_planning",
            context=context,
            dependencies=["technical_feasibility", "ml_feasibility", "ux_assessment"]
        ))
        
        # Task 10: Quality Assurance reviews all
        tasks.append(AgentTask(
            task_id="qa_discovery_review",
            agent_role=AgentRole.QUALITY_ASSURANCE,
            task_type="quality_review",
            context={"review_all": True},
            dependencies=["timeline_synthesis"]
        ))
        
        # Task 11: Engagement Manager synthesizes final discovery
        tasks.append(AgentTask(
            task_id="discovery_synthesis",
            agent_role=AgentRole.ENGAGEMENT_MANAGER,
            task_type="synthesis",
            context=context,
            dependencies=["qa_discovery_review"]
        ))
        
        return tasks
    
    def create_sow_workflow(self, context: Dict[str, Any], discovery_output: str) -> List[AgentTask]:
        """
        Create coordinated SOW generation workflow with multi-agent review.
        """
        context_with_discovery = {**context, "discovery": discovery_output}
        tasks = []
        
        # Task 1: Strategist drafts executive summary and business case
        tasks.append(AgentTask(
            task_id="sow_executive_summary",
            agent_role=AgentRole.STRATEGIST,
            task_type="executive_summary",
            context=context_with_discovery,
            dependencies=[]
        ))
        
        # Task 2: Analyst details scope and acceptance criteria
        tasks.append(AgentTask(
            task_id="sow_scope_details",
            agent_role=AgentRole.ANALYST,
            task_type="scope_definition",
            context=context_with_discovery,
            dependencies=[]
        ))
        
        # Task 3: Architect provides technical approach
        tasks.append(AgentTask(
            task_id="sow_technical_approach",
            agent_role=AgentRole.ARCHITECT,
            task_type="technical_approach",
            context=context_with_discovery,
            dependencies=["sow_scope_details"]
        ))
        
        # Task 4: Security Specialist reviews and adds security requirements
        tasks.append(AgentTask(
            task_id="sow_security_review",
            agent_role=AgentRole.SECURITY_SPECIALIST,
            task_type="security_requirements",
            context=context_with_discovery,
            dependencies=["sow_technical_approach"]
        ))
        
        # Task 5: PM creates project plan
        tasks.append(AgentTask(
            task_id="sow_project_plan",
            agent_role=AgentRole.PROJECT_MANAGER,
            task_type="project_planning",
            context=context_with_discovery,
            dependencies=["sow_technical_approach"]
        ))
        
        # Task 6: Cross-review by Strategist (business alignment)
        tasks.append(AgentTask(
            task_id="sow_strategic_review",
            agent_role=AgentRole.STRATEGIST,
            task_type="strategic_review",
            context={"review_targets": ["sow_scope_details", "sow_technical_approach", "sow_project_plan"]},
            dependencies=["sow_scope_details", "sow_technical_approach", "sow_project_plan"]
        ))
        
        # Task 7: QA comprehensive review
        tasks.append(AgentTask(
            task_id="sow_qa_review",
            agent_role=AgentRole.QUALITY_ASSURANCE,
            task_type="comprehensive_qa",
            context={"review_all": True},
            dependencies=["sow_executive_summary", "sow_scope_details", "sow_technical_approach", 
                         "sow_security_review", "sow_project_plan", "sow_strategic_review"]
        ))
        
        # Task 8: Engagement Manager synthesizes final SOW
        tasks.append(AgentTask(
            task_id="sow_final_synthesis",
            agent_role=AgentRole.ENGAGEMENT_MANAGER,
            task_type="sow_synthesis",
            context=context_with_discovery,
            dependencies=["sow_qa_review"]
        ))
        
        return tasks
    
    def execute_workflow(self, tasks: List[AgentTask], max_iterations: int = 3) -> Dict[str, str]:
        """
        Execute a workflow with dependency management and iterative refinement.
        
        Returns: Dict of task_id -> output
        """
        self.tasks = {task.task_id: task for task in tasks}
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            self.log(f"🔄 Workflow Iteration {iteration}/{max_iterations}")
            
            # Find tasks ready to execute (dependencies satisfied)
            ready_tasks = self._get_ready_tasks()
            
            if not ready_tasks:
                self.log("✅ All tasks completed")
                break
            
            # Execute ready tasks
            for task in ready_tasks:
                self._execute_task(task)
            
            # Check for tasks requiring revision
            needs_revision = [t for t in self.tasks.values() 
                            if t.status == AgentTaskStatus.REVISION_NEEDED]
            
            if not needs_revision:
                break
            
            self.log(f"⚠️ {len(needs_revision)} task(s) require revision")
        
        # Compile final outputs
        outputs = {}
        for task_id, task in self.tasks.items():
            if task.output:
                outputs[task_id] = task.output
        
        return outputs
    
    def _get_ready_tasks(self) -> List[AgentTask]:
        """Get tasks ready for execution (dependencies satisfied)."""
        ready = []
        for task in self.tasks.values():
            if task.status in [AgentTaskStatus.PENDING, AgentTaskStatus.REVISION_NEEDED]:
                # Check if all dependencies are completed or approved
                deps_satisfied = all(
                    self.tasks[dep_id].status in [AgentTaskStatus.APPROVED, AgentTaskStatus.COMPLETED]
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                if deps_satisfied:
                    ready.append(task)
        return ready
    
    def _execute_task(self, task: AgentTask):
        """Execute a single agent task."""
        task.status = AgentTaskStatus.IN_PROGRESS
        self.log(f"🤖 {task.agent_role.value}: {task.task_type}")
        
        if task.task_type == "peer_review":
            # Execute peer review
            self._execute_peer_review(task)
        else:
            # Execute content generation
            self._execute_content_task(task)
    
    def _execute_content_task(self, task: AgentTask):
        """Execute a content generation task."""
        from consulting_firm.consulting_personas import get_persona_prompt
        
        # Build context from dependencies
        dep_context = self._build_dependency_context(task)
        
        # Create detailed prompt for this specific task
        prompt = self._create_task_prompt(task, dep_context)
        
        # Execute with appropriate persona
        persona_prompt = get_persona_prompt(task.agent_role.value)
        output = self.model.generate(
            task.agent_role.value,
            prompt,
            system=persona_prompt
        )
        
        task.output = output
        task.status = AgentTaskStatus.REVIEW_REQUIRED
        self.agent_outputs[task.task_id] = output
        
        self.log(f"✅ {task.agent_role.value} completed {task.task_type}")
    
    def _execute_peer_review(self, task: AgentTask):
        """Execute a peer review task."""
        target_task_id = task.context.get("target") or task.context.get("review_targets", [])[0]
        target_task = self.tasks.get(target_task_id)
        
        if not target_task or not target_task.output:
            task.status = AgentTaskStatus.PENDING
            return
        
        # Create review prompt
        review_prompt = f"""You are conducting a peer review of work from {target_task.agent_role.value}.

TASK TYPE: {target_task.task_type}
OUTPUT TO REVIEW:
{target_task.output[:2000]}

Provide a structured review with:
1. STRENGTHS: What is done well (3-5 points)
2. CONCERNS: Issues or gaps that need attention (list all)
3. CRITICAL ISSUES: Blocking issues that must be fixed (if any)
4. SUGGESTIONS: Specific improvements (3-5 actionable suggestions)
5. APPROVAL: YES or NO (approve only if no critical issues)

Be thorough, constructive, and specific. Focus on completeness, accuracy, and business value."""

        from consulting_firm.consulting_personas import get_persona_prompt
        persona_prompt = get_persona_prompt(task.agent_role.value)
        
        review_output = self.model.generate(
            task.agent_role.value,
            review_prompt,
            system=persona_prompt
        )
        
        task.output = review_output
        
        # Parse review (simplified - in production use structured output)
        approved = "APPROVAL: YES" in review_output or "approve" in review_output.lower()
        has_critical = "CRITICAL ISSUES:" in review_output and review_output.split("CRITICAL ISSUES:")[1].split("\n")[1].strip() != ""
        
        if approved and not has_critical:
            target_task.status = AgentTaskStatus.APPROVED
            task.status = AgentTaskStatus.COMPLETED
            self.log(f"✅ Review approved: {target_task_id}")
        else:
            target_task.status = AgentTaskStatus.REVISION_NEEDED
            target_task.revision_count += 1
            task.status = AgentTaskStatus.COMPLETED
            self.log(f"⚠️ Revision required: {target_task_id}")
        
        # Store review
        target_task.reviews.append({
            "reviewer": task.agent_role.value,
            "approved": approved,
            "output": review_output
        })
    
    def _build_dependency_context(self, task: AgentTask) -> str:
        """Build context string from completed dependency tasks."""
        context_parts = []
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.output:
                context_parts.append(f"### {dep_task.task_type} by {dep_task.agent_role.value}:\n{dep_task.output[:1500]}\n")
        
        return "\n".join(context_parts) if context_parts else "No dependency context available."
    
    def _create_task_prompt(self, task: AgentTask, dep_context: str) -> str:
        """Create a detailed prompt for a specific task."""
        base_context = task.context.get("user_input", "") + "\n" + task.context.get("documents", "")
        
        prompt = f"""TASK: {task.task_type}

PROJECT CONTEXT:
{base_context[:1500]}

DEPENDENCY CONTEXT:
{dep_context}

YOUR SPECIFIC ASSIGNMENT:
"""
        
        # Add task-specific instructions
        task_instructions = {
            "discovery_framing": "Frame the discovery process. Identify key questions, stakeholder groups, and discovery objectives. Set clear scope for the discovery phase.",
            "strategic_analysis": "Analyze business strategy: market opportunity, competitive positioning, ROI potential, strategic alignment. Be specific and measurable.",
            "requirements_analysis": "Document comprehensive requirements: functional, non-functional, stakeholder needs, acceptance criteria. Use structured format.",
            "technical_assessment": "Assess technical feasibility: architecture approach, technology choices, integration points, scalability. Provide business justification.",
            "ml_assessment": "Evaluate ML/AI feasibility: data requirements, model approaches, performance targets, ethical considerations. Be realistic about limitations.",
            "ux_assessment": "Define UX requirements: user personas, journeys, usability criteria, accessibility standards. Focus on user value.",
            "timeline_planning": "Create realistic project timeline: phases, milestones, dependencies, resources, risks. Base on technical assessments.",
            "executive_summary": "Write compelling executive summary: problem, solution, value, investment. Decision-focused for executives.",
            "scope_definition": "Define detailed scope: in-scope deliverables with acceptance criteria, explicit out-of-scope items. Prevent scope creep.",
            "technical_approach": "Describe technical approach: architecture, technology stack, data flows, security, scalability. Business-justified choices.",
            "security_requirements": "Define security requirements: threat model, controls, compliance, data protection. Risk-based approach.",
            "project_planning": "Create comprehensive project plan: timeline, resources, risks, governance, communication. Standard PM frameworks.",
            "synthesis": "Synthesize all inputs into coherent, professional deliverable. Resolve conflicts, fill gaps, ensure consistency."
        }
        
        instruction = task_instructions.get(task.task_type, "Complete your specialized analysis for this task.")
        prompt += instruction
        
        # Add revision context if this is a revision
        if task.revision_count > 0 and task.reviews:
            latest_review = task.reviews[-1]
            prompt += f"\n\nREVISION REQUIRED - ADDRESS THESE CONCERNS:\n{latest_review['output'][:1000]}"
        
        prompt += "\n\nProvide detailed, professional output in structured format with clear sections."
        
        return prompt
    
    def generate_coordination_report(self) -> str:
        """Generate a report of the multi-agent coordination process."""
        report = ["# Multi-Agent Coordination Report\n"]
        report.append(f"**Total Tasks:** {len(self.tasks)}\n")
        report.append(f"**Agent Roles:** {len(set(t.agent_role for t in self.tasks.values()))}\n\n")
        
        # Task summary
        report.append("## Task Execution Summary\n\n")
        for task_id, task in self.tasks.items():
            report.append(f"### {task_id}\n")
            report.append(f"- **Agent:** {task.agent_role.value}\n")
            report.append(f"- **Type:** {task.task_type}\n")
            report.append(f"- **Status:** {task.status.value}\n")
            report.append(f"- **Reviews:** {len(task.reviews)}\n")
            report.append(f"- **Revisions:** {task.revision_count}\n\n")
        
        # Review summary
        report.append("## Peer Review Summary\n\n")
        total_reviews = sum(len(t.reviews) for t in self.tasks.values())
        report.append(f"**Total Reviews Conducted:** {total_reviews}\n\n")
        
        for task in self.tasks.values():
            if task.reviews:
                report.append(f"### Reviews for {task.task_id}\n")
                for i, review in enumerate(task.reviews, 1):
                    report.append(f"**Review {i} by {review['reviewer']}:**\n")
                    report.append(f"- Approved: {review['approved']}\n\n")
        
        return "\n".join(report)
