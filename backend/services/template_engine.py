from __future__ import annotations

from typing import Any, Dict
from models.resume_schema import Resume, parse_resume_text_to_schema
from services.renderers.html_renderer import render_html
from services.renderers.pdf_renderer import render_pdf_from_html


class TemplateEngine:
    """
    Facade for HTML preview and PDF rendering.
    """

    @staticmethod
    def _ensure_resume(resume_json: Dict[str, Any] | None, resume_text: str | None) -> Resume:
        if resume_json and isinstance(resume_json, dict):
            return Resume.model_validate(resume_json)
        if resume_text:
            return parse_resume_text_to_schema(resume_text)
        return Resume()

    @staticmethod
    def render_preview(template_id: str, resume_json: Dict[str, Any] | None = None, resume_text: str | None = None) -> str:
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        html = render_html(template_id, resume, raw_text=resume_text)
        return html

    @staticmethod
    async def render_pdf(template_id: str, resume_json: Dict[str, Any] | None = None, resume_text: str | None = None) -> bytes:
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        html = render_html(template_id, resume, raw_text=resume_text)
        pdf_bytes = await render_pdf_from_html(html, page_size="A4")
        return pdf_bytes


