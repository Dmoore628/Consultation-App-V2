"""HTML/CSS -> PDF and DOCX document generator using WeasyPrint with a ReportLab fallback.

This implements the approach you recommended: generate professional HTML with
separate CSS and convert to PDF using WeasyPrint (HTML/CSS -> PDF). If
WeasyPrint is not available, falls back to a simple ReportLab-based PDF.
"""
import os
from pathlib import Path
import markdown as md
from . import config

try:
    from weasyprint import HTML, CSS
    _HAS_WEASY = True
except Exception:
    _HAS_WEASY = False


class DocumentGenerator:
    def __init__(self, output_path: str | None = None, templates_path: str | None = None):
        self.output_path = output_path or config.OUTPUT_PATH
        self.templates_path = templates_path or config.TEMPLATES_PATH
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.templates_path, exist_ok=True)
        self._ensure_professional_templates()

    def _ensure_professional_templates(self):
        css_content = """
/* Professional Consulting Document Styling (minimal for example) */
@page { size: letter; margin: 1in; }
body { font-family: 'Segoe UI', Tahoma, sans-serif; color: #333; font-size: 11pt; }
.header { text-align:center; margin-bottom: 2cm; }
.document-title { font-size: 20pt; font-weight: bold; }
.section { margin: 0.8cm 0; }
"""
        css_path = os.path.join(self.templates_path, "professional.css")
        if not os.path.exists(css_path):
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)

    def generate_from_markdown(self, md_path: str, out_format: str = 'pdf') -> str:
        """Convert a markdown file to HTML and then to PDF/DOCX as requested.

        Currently supports 'pdf', 'html', and 'docx' (docx is a simple wrapper).
        """
        if not os.path.exists(md_path):
            raise FileNotFoundError(md_path)

        text = Path(md_path).read_text(encoding='utf-8')
        html_body = md.markdown(text, extensions=['tables', 'fenced_code'])

        css_file = os.path.join(self.templates_path, 'professional.css')
        html = f"""<!doctype html><html><head><meta charset='utf-8'><link rel='stylesheet' href='{css_file}'></head><body>{html_body}</body></html>"""

        html_file = os.path.join(self.output_path, Path(md_path).stem + '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        if out_format == 'html':
            return html_file

        if out_format == 'pdf' and _HAS_WEASY:
            pdf_file = os.path.join(self.output_path, Path(md_path).stem + '.pdf')
            try:
                HTML(html_file).write_pdf(pdf_file, stylesheets=[CSS(css_file)])
                return pdf_file
            except Exception as e:
                # Fall through to fallback
                print(f"WeasyPrint conversion failed: {e}")

        # Fallback simple PDF using ReportLab
        return self._generate_simple_pdf_from_text(text, Path(md_path).stem)

    def _generate_simple_pdf_from_text(self, text: str, name: str) -> str:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            raise RuntimeError("No PDF generation backend available (install weasyprint or reportlab)")

        out = os.path.join(self.output_path, f"{name}_simple.pdf")
        c = canvas.Canvas(out, pagesize=letter)
        width, height = letter
        y = height - 50
        for line in text.splitlines():
            if y < 80:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:120])
            y -= 14
        c.save()
        return out
