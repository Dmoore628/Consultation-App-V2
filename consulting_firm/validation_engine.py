from typing import Dict, List
import os
import re


class ValidationEngine:
    """Comprehensive validation engine for consulting deliverables.

    Validates:
    - Document presence and quality
    - Professional deliverable standards
    - Cross-artifact consistency
    - Technical architecture validity
    - SOW completeness and professional standards
    - Industry standards compliance
    - Business logic consistency
    """

    def __init__(self):
        self.validation_results = {}

    def _read(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_components(self, txt: str) -> List[str]:
        # Look for a Components list or lines like 'A -> B'
        comps = set()
        # bullet list components
        for m in re.findall(r"^-\s*(.+)$", txt, flags=re.MULTILINE):
            if len(m.strip()) < 80:
                comps.add(m.strip())
        # arrow connections
        for m in re.findall(r"([A-Za-z0-9_ \-]+)\s*->\s*([A-Za-z0-9_ \-]+)", txt):
            comps.add(m[0].strip())
            comps.add(m[1].strip())
        return sorted(c for c in comps if c)

    def _find_arrows(self, txt: str) -> List[tuple]:
        return [(a.strip(), b.strip()) for a, b in re.findall(r"([A-Za-z0-9_ \-]+)\s*->\s*([A-Za-z0-9_ \-]+)", txt)]

    def validate(self, artifacts: Dict[str, str]) -> str:
        report_lines = ["# Validation Report\n"]
        report_lines.append(f"**Generated:** {self._get_timestamp()}\n")
        report_lines.append("---\n\n")

        # store small summaries for cross-checks
        summaries: Dict[str, str] = {}
        all_issues = []
        all_warnings = []
        all_passes = []

        # Phase 1: Individual artifact validation
        report_lines.append("## Phase 1: Individual Artifact Quality\n\n")
        for name, path in artifacts.items():
            report_lines.append(f"### {name.upper()}: `{path}`\n")
            if not os.path.exists(path):
                report_lines.append("- ❌ **Status:** MISSING\n")
                all_issues.append(f"{name}: File missing")
                continue
            
            size = os.path.getsize(path)
            report_lines.append(f"- ✅ **Status:** Present ({size:,} bytes)\n")

            txt = self._read(path)
            summaries[name] = txt

            # Quality checks
            quality_result = self._assess_document_quality(txt, name)
            if quality_result['issues']:
                for issue in quality_result['issues']:
                    report_lines.append(f"- ❌ {issue}\n")
                    all_issues.append(f"{name}: {issue}")
            if quality_result['warnings']:
                for warning in quality_result['warnings']:
                    report_lines.append(f"- ⚠️ {warning}\n")
                    all_warnings.append(f"{name}: {warning}")
            if quality_result['passes']:
                for pass_item in quality_result['passes']:
                    report_lines.append(f"- ✅ {pass_item}\n")
                    all_passes.append(f"{name}: {pass_item}")
            
            report_lines.append("\n")

        # Phase 2: Professional standards validation
        report_lines.append("## Phase 2: Professional Deliverable Standards\n\n")
        
        # SOW completeness check
        sow_path = artifacts.get('sow')
        if sow_path and os.path.exists(sow_path):
            sow_text = summaries.get('sow', self._read(sow_path))
            sow_result = self.evaluate_sow_professional_standards(sow_text)
            report_lines.append("### Scope of Work (SOW) Completeness\n")
            report_lines.append(f"- **Overall Completeness:** {'✅ PASS' if sow_result['complete'] else '❌ FAIL'}\n")
            if sow_result['missing_sections']:
                report_lines.append(f"- ❌ Missing required sections: {', '.join(sow_result['missing_sections'])}\n")
                all_issues.extend([f"SOW: Missing {s}" for s in sow_result['missing_sections']])
            if sow_result['issues']:
                for issue in sow_result['issues']:
                    report_lines.append(f"- ❌ {issue}\n")
                    all_issues.append(f"SOW: {issue}")
            if sow_result['warnings']:
                for warning in sow_result['warnings']:
                    report_lines.append(f"- ⚠️ {warning}\n")
                    all_warnings.append(f"SOW: {warning}")
            if sow_result['passes']:
                for pass_item in sow_result['passes']:
                    report_lines.append(f"- ✅ {pass_item}\n")
            report_lines.append("\n")

        # Phase 3: Cross-artifact consistency checks
        report_lines.append("## Phase 3: Cross-Artifact Consistency\n\n")
        consistency_results = self._check_cross_artifact_consistency(summaries)
        if consistency_results['issues']:
            for issue in consistency_results['issues']:
                report_lines.append(f"- ❌ {issue}\n")
                all_issues.append(f"Consistency: {issue}")
        if consistency_results['warnings']:
            for warning in consistency_results['warnings']:
                report_lines.append(f"- ⚠️ {warning}\n")
                all_warnings.append(f"Consistency: {warning}")
        if consistency_results['passes']:
            for pass_item in consistency_results['passes']:
                report_lines.append(f"- ✅ {pass_item}\n")
        report_lines.append("\n")

        # Phase 4: Technical architecture validation
        tech_path = artifacts.get('tech')
        if tech_path and os.path.exists(tech_path):
            report_lines.append("## Phase 4: Technical Architecture Validation\n\n")
            tech_txt = summaries.get('tech', '')
            tech_results = self._validate_technical_architecture(tech_txt)
            
            if tech_results['components']:
                report_lines.append(f"- ✅ **Components Identified:** {', '.join(tech_results['components'][:10])}")
                if len(tech_results['components']) > 10:
                    report_lines.append(f" ... and {len(tech_results['components']) - 10} more")
                report_lines.append("\n")
            else:
                report_lines.append("- ⚠️ No components explicitly identified\n")
                all_warnings.append("Technical Architecture: No components identified")
            
            report_lines.append(f"- **Connections Documented:** {tech_results['connections_count']}\n")
            
            if tech_results['issues']:
                for issue in tech_results['issues']:
                    report_lines.append(f"- ❌ {issue}\n")
                    all_issues.append(f"Tech Architecture: {issue}")
            if tech_results['warnings']:
                for warning in tech_results['warnings']:
                    report_lines.append(f"- ⚠️ {warning}\n")
                    all_warnings.append(f"Tech Architecture: {warning}")
            if tech_results['passes']:
                for pass_item in tech_results['passes']:
                    report_lines.append(f"- ✅ {pass_item}\n")
            report_lines.append("\n")

        # Phase 5: Industry standards compliance
        if summaries:
            report_lines.append("## Phase 5: Industry Standards & Best Practices\n\n")
            all_text = "\n\n".join(summaries.values())
            referenced, missing_std = self._check_industry_standards(all_text)
            if referenced:
                report_lines.append(f"- ✅ **Referenced Standards:** {', '.join(referenced)}\n")
            else:
                report_lines.append("- ⚠️ No explicit industry standards referenced\n")
                all_warnings.append("No industry standards (OWASP, ISO, SOC2, etc.) referenced")
            
            if missing_std:
                report_lines.append(f"- 💡 **Suggested Standards:** {', '.join(missing_std)}\n")
            report_lines.append("\n")

        # Summary
        report_lines.append("---\n")
        report_lines.append("## Validation Summary\n\n")
        report_lines.append(f"- ❌ **Issues (Must Fix):** {len(all_issues)}\n")
        report_lines.append(f"- ⚠️ **Warnings (Should Review):** {len(all_warnings)}\n")
        report_lines.append(f"- ✅ **Passes:** {len(all_passes)}\n\n")
        
        if len(all_issues) == 0:
            report_lines.append("**✅ VALIDATION PASSED** - All deliverables meet professional standards.\n")
        elif len(all_issues) <= 3:
            report_lines.append("**⚠️ VALIDATION PARTIAL** - Minor issues detected. Review and address before client delivery.\n")
        else:
            report_lines.append("**❌ VALIDATION FAILED** - Significant issues detected. Major revisions required.\n")

        # Write report
        out = os.path.join('outputs', 'validation_report.md')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return out
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- SOW evaluation helpers ---
    def evaluate_sow(self, text: str):
        """Legacy method for backward compatibility."""
        result = self.evaluate_sow_professional_standards(text)
        return result['complete'], result['missing_sections'], result['issues']
    
    def evaluate_sow_professional_standards(self, text: str) -> dict:
        """Comprehensive SOW validation against professional standards."""
        required = [
            'EXECUTIVE SUMMARY',
            'SUCCESS CRITERIA',
            'SCOPE & DELIVERABLES',
            'TECHNICAL APPROACH',
            'PROJECT MANAGEMENT',
            'ASSUMPTIONS',
        ]
        # Optional but recommended
        recommended = ['OUT-OF-SCOPE', 'RISKS', 'KPI', 'SUCCESS METRICS', 'ACCEPTANCE CRITERIA']
        
        issues = []
        warnings = []
        passes = []
        
        # Check required sections
        text_upper = text.upper()
        present = [s for s in required if s in text_upper]
        missing = [s for s in required if s not in present]
        
        if not missing:
            passes.append("All required sections present")
        
        # Check acceptance criteria
        has_acceptance = any('acceptance criteria' in line.lower() for line in text.splitlines())
        if not has_acceptance:
            issues.append('Acceptance criteria section missing or not clearly labeled')
        else:
            passes.append("Acceptance criteria section present")
        
        # Check timeline heuristic
        has_timeline = 'timeline' in text.lower() or 'milestone' in text.lower()
        if not has_timeline:
            warnings.append('Timeline or milestones not explicitly mentioned')
        else:
            passes.append("Timeline and milestones addressed")
        
        # Check for measurable success criteria
        has_metrics = any(term in text.lower() for term in ['kpi', 'metric', 'measure', 'target', '%', 'percent'])
        if not has_metrics:
            warnings.append('Success criteria may not be measurable (no metrics/KPIs found)')
        else:
            passes.append("Measurable success criteria included")
        
        # Check for out-of-scope
        has_out_of_scope = 'out-of-scope' in text.lower() or 'out of scope' in text.lower()
        if not has_out_of_scope:
            warnings.append('Out-of-scope items not explicitly listed (recommended for clarity)')
        else:
            passes.append("Out-of-scope items explicitly defined")
        
        # Check for risk management
        has_risks = 'risk' in text.lower()
        if not has_risks:
            warnings.append('Risk management not explicitly addressed')
        else:
            passes.append("Risk management addressed")
        
        # Check length (professional SOW should be substantial)
        if len(text) < 2000:
            warnings.append('Document appears short for professional SOW (< 2000 characters)')
        elif len(text) > 50000:
            warnings.append('Document very long (> 50000 characters) - consider summarizing')
        else:
            passes.append(f"Document length appropriate ({len(text):,} characters)")
        
        complete = (len(missing) == 0 and has_acceptance and has_timeline)
        
        return {
            'complete': complete,
            'missing_sections': missing,
            'issues': issues,
            'warnings': warnings,
            'passes': passes
        }
    
    def _assess_document_quality(self, text: str, doc_name: str) -> dict:
        """Assess individual document quality."""
        issues = []
        warnings = []
        passes = []
        
        # Length check
        if len(text.strip()) < 100:
            issues.append("Document too short (< 100 characters)")
        elif len(text.strip()) < 500:
            warnings.append("Document quite short (< 500 characters)")
        else:
            passes.append(f"Adequate length ({len(text):,} characters)")
        
        # Structure check (headings)
        heading_count = len(re.findall(r'^#{1,6}\s+.+', text, re.MULTILINE))
        if heading_count == 0:
            warnings.append("No markdown headings found - document may lack structure")
        elif heading_count < 3:
            warnings.append(f"Only {heading_count} heading(s) - consider adding more structure")
        else:
            passes.append(f"Well-structured with {heading_count} sections")
        
        # Jargon check for client-facing documents
        if doc_name in ['sow', 'discovery']:
            jargon_terms = ['api', 'db', 'crud', 'orm', 'jwt', 'oauth', 'k8s', 'kubectl', 'dockerfile']
            found = [t for t in jargon_terms if t in text.lower()]
            if len(found) > 5:
                warnings.append(f"High technical jargon count ({len(found)} terms) - consider simplifying for client audience")
            elif len(found) > 0:
                passes.append(f"Moderate technical jargon ({len(found)} terms) - acceptable")
            else:
                passes.append("Client-friendly language (minimal jargon)")
        
        # Completeness markers
        has_todos = 'todo' in text.lower() or 'tbd' in text.lower() or 'xxx' in text.lower()
        if has_todos:
            issues.append("Document contains TODO/TBD placeholders - needs completion")
        else:
            passes.append("No placeholder markers (TODO/TBD) found")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passes': passes
        }
    
    def _check_cross_artifact_consistency(self, summaries: dict) -> dict:
        """Check for inconsistencies across artifacts."""
        issues = []
        warnings = []
        passes = []
        
        # Timeline consistency
        timelines = {}
        for name, txt in summaries.items():
            m = re.search(r"(phase|milestone).*?(\d+\s*(week|weeks|month|months))", txt, flags=re.I)
            if m:
                timelines[name] = m.group(2)
        
        if len(set(timelines.values())) > 1:
            warnings.append(f"Timeline inconsistency detected: {timelines}")
        elif len(timelines) > 1:
            passes.append("Timeline mentions consistent across artifacts")
        
        # Tech stack consistency
        tech_mentions = {}
        tech_terms = ['postgres', 'mysql', 'mongodb', 'redis', 'kafka', 'rabbitmq', 'aws', 'azure', 'gcp']
        for name, txt in summaries.items():
            found = [t for t in tech_terms if t in txt.lower()]
            if found:
                tech_mentions[name] = found
        
        # Check for contradictory tech choices
        all_tech = set(t for vals in tech_mentions.values() for t in vals)
        contradictions = []
        if 'mysql' in all_tech and 'mongodb' in all_tech:
            contradictions.append("Relational (MySQL) and NoSQL (MongoDB) both mentioned")
        if 'aws' in all_tech and 'azure' in all_tech and 'gcp' in all_tech:
            warnings.append("Multiple cloud providers mentioned - clarify primary platform")
        
        if contradictions:
            warnings.append(f"Potential tech contradictions: {'; '.join(contradictions)}")
        elif len(tech_mentions) > 1:
            passes.append("Technology stack consistent across artifacts")
        
        # Scope consistency - check if SOW and technical architecture align
        if 'sow' in summaries and 'tech' in summaries:
            sow_components = set(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', summaries['sow']))
            tech_components = set(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', summaries['tech']))
            overlap = len(sow_components & tech_components)
            if overlap > 3:
                passes.append("Good alignment between SOW and technical architecture")
            elif overlap > 0:
                warnings.append("Limited alignment between SOW and technical architecture")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passes': passes
        }
    
    def _validate_technical_architecture(self, tech_text: str) -> dict:
        """Validate technical architecture document."""
        issues = []
        warnings = []
        passes = []
        
        components = self._extract_components(tech_text)
        edges = self._find_arrows(tech_text)
        
        # Component validation
        if not components:
            warnings.append("No components explicitly identified")
        elif len(components) < 3:
            warnings.append(f"Only {len(components)} component(s) identified - consider expanding")
        else:
            passes.append(f"{len(components)} components documented")
        
        # Connection validation
        if len(edges) == 0 and len(components) > 1:
            warnings.append("No connections (arrows) documented between components")
        elif len(edges) > 0:
            passes.append(f"{len(edges)} component connections documented")
        
        # Check for orphan connections
        unknown_refs = []
        for a, b in edges:
            if a not in components or b not in components:
                unknown_refs.append((a, b))
        if unknown_refs:
            issues.append(f"Connections reference undefined components: {unknown_refs[:3]}")
        elif edges:
            passes.append("All connections reference defined components")
        
        # Check for architecture diagrams or visual aids
        has_diagram_markers = any(marker in tech_text.lower() for marker in ['```mermaid', '```dot', 'diagram', 'figure'])
        if has_diagram_markers:
            passes.append("Diagram or visual representation included")
        else:
            warnings.append("No diagrams detected - consider adding visual architecture diagram")
        
        return {
            'components': components,
            'connections_count': len(edges),
            'issues': issues,
            'warnings': warnings,
            'passes': passes
        }

    def _check_industry_standards(self, text: str):
        known = [
            'OWASP', 'ASVS', 'ISO 27001', 'SOC 2', 'SOC2', 'GDPR', 'HIPAA', 'PCI', 'PCI-DSS', 'NIST', 'CIS',
        ]
        present = []
        for k in known:
            if k.lower() in text.lower():
                present.append(k)
        # Recommend some that are commonly expected if none of that class is present
        recommendations = []
        if not any(s in present for s in ['OWASP', 'ASVS']):
            recommendations.append('OWASP ASVS')
        if not any(s in present for s in ['ISO 27001', 'SOC 2', 'SOC2']):
            recommendations.append('ISO 27001 or SOC 2')
        if not any(s in present for s in ['GDPR', 'HIPAA', 'PCI', 'PCI-DSS']):
            recommendations.append('GDPR/HIPAA/PCI (as applicable)')
        if not any(s in present for s in ['NIST', 'CIS']):
            recommendations.append('NIST or CIS Benchmarks')
        return sorted(set(present)), recommendations


if __name__ == '__main__':
    ve = ValidationEngine()
    print(ve.validate({'a': 'nonexistent.md'}))
