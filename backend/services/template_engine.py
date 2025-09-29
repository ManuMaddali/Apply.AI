from __future__ import annotations

from typing import Any, Dict
import asyncio
import threading


def _prefer_backend(module_path: str, fallback_path: str, attr: str | None = None):
    try:
        mod = __import__(module_path, fromlist=['*'])
    except ImportError:
        mod = __import__(fallback_path, fromlist=['*'])
    return getattr(mod, attr) if attr else mod

Resume = _prefer_backend('backend.models.resume_schema', 'models.resume_schema', attr='Resume')
parse_resume_text_to_schema = _prefer_backend('backend.models.resume_schema', 'models.resume_schema', attr='parse_resume_text_to_schema')
_content_filters = _prefer_backend('backend.services.content_filters', 'services.content_filters')
clean_and_compact = _prefer_backend('backend.services.cleaners', 'services.cleaners', attr='clean_and_compact')
render_html = _prefer_backend('backend.services.renderers.html_renderer', 'services.renderers.html_renderer', attr='render_html')
render_pdf_from_html = _prefer_backend('backend.services.renderers.pdf_renderer', 'services.renderers.pdf_renderer', attr='render_pdf_from_html')
render_pdf_from_html_sync = _prefer_backend('backend.services.renderers.pdf_renderer', 'services.renderers.pdf_renderer', attr='render_pdf_from_html_sync')


DEFAULT_TEMPLATE = "executive_compact"

sanitize_input_text = _content_filters.sanitize_input_text


def scrub_noise(text: str | None) -> str:
    """ATS-safe scrubber that removes banned fragments and squeezes whitespace."""
    return _content_filters.scrub_noise(text or "")


def dedupe_summary(summary: str | list[str] | None) -> str:
    """Collapse multiple summary entries into a single ≤280 character line."""
    return _content_filters.dedupe_summary(summary or "", max_chars=280)


def truncate_bullets(bullets: list[str] | None, limit: int) -> list[str]:
    """Trim bullet lists to the specified limit while removing first-person tone."""
    return _content_filters.truncate_bullets(bullets or [], max_bullets=limit)


def _deep_scrub(value: Any) -> Any:
    """Recursively apply ``scrub_noise`` to strings inside nested structures."""
    if value is None:
        return None
    if isinstance(value, str):
        return scrub_noise(value)
    if isinstance(value, list):
        return [_deep_scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: _deep_scrub(v) for k, v in value.items()}
    return value


def _normalize_resume(resume: Resume) -> Resume:
    """Apply global sanitisation, section whitelisting, and bullet limits."""
    raw = resume.model_dump()
    raw = _deep_scrub(raw)

    # Enforce tone and length rules before structural sanitisation
    raw["summary"] = dedupe_summary(raw.get("summary"))

    for item in raw.get("experience", []) or []:
        if isinstance(item, dict):
            item["bullets"] = truncate_bullets(item.get("bullets") or [], 5)

    for project in raw.get("projects", []) or []:
        if isinstance(project, dict):
            project["bullets"] = truncate_bullets(project.get("bullets") or [], 3)

    # ``sanitize_resume_dict`` enforces section whitelist and final scrubbing
    normalized = _content_filters.sanitize_resume_dict(raw)
    return Resume.model_validate(normalized)


class TemplateEngine:
    """
    Facade for HTML preview and PDF rendering.
    """

    @staticmethod
    def _ensure_resume(resume_json: Dict[str, Any] | None, resume_text: str | None):
        from models.resume_schema import Resume
        
        if resume_json and isinstance(resume_json, dict):
            resume_obj = Resume.model_validate(resume_json)
            return _normalize_resume(resume_obj)
        if resume_text:
            print(f"🔍 TemplateEngine: Parsing resume text of length {len(resume_text)}")
            print(f"📝 Resume preview (first 200 chars): {resume_text[:200]}...")
            
            # Use our comprehensive resume parser for better section extraction
            try:
                from services.resume_parser import ResumeParser
                parser = ResumeParser()
                parsed_data = parser.parse(sanitize_input_text(resume_text))
                print(f"✅ Comprehensive parser extracted: name='{parsed_data.get('name')}', experience={len(parsed_data.get('experience', []))} items")
                
                # Convert to Resume schema format
                from models.resume_schema import Resume, Contact, ExperienceItem, EducationItem, Skill
                
                # Create contact info
                contact = Contact(
                    email=parsed_data.get('email', ''),
                    phone=parsed_data.get('phone', ''),
                    location=parsed_data.get('location', ''),
                    links=[]
                )
                
                # Add LinkedIn/GitHub links
                if parsed_data.get('linkedin'):
                    contact.links.append({'label': 'LinkedIn', 'url': parsed_data['linkedin']})
                if parsed_data.get('github'):
                    contact.links.append({'label': 'GitHub', 'url': parsed_data['github']})
                
                # Convert experience with proper bullet points
                experience_items = []
                for exp in parsed_data.get('experience', []):
                    bullets = exp.get('responsibilities', [])
                    if isinstance(bullets, list) and bullets:
                        experience_items.append(ExperienceItem(
                            title=exp.get('title', ''),
                            company=exp.get('company', ''),
                            dates=exp.get('dates', ''),
                            bullets=bullets
                        ))
                
                # Convert education
                education_items = []
                for edu in parsed_data.get('education', []):
                    school_info = []
                    if edu.get('degree'):
                        school_info.append(edu['degree'])
                    if edu.get('field'):
                        school_info.append(edu['field'])
                    if edu.get('institution'):
                        school_info.append(f"from {edu['institution']}")
                    if edu.get('year'):
                        school_info.append(f"({edu['year']})")
                    
                    if school_info:
                        education_items.append(EducationItem(school=' '.join(school_info)))
                
                # Convert skills
                skills_list = []
                skills_dict = parsed_data.get('skills', {})
                if isinstance(skills_dict, dict):
                    for category, skill_list in skills_dict.items():
                        skills_list.extend([Skill(name=skill) for skill in skill_list if skill])
                
                resume = Resume(
                    name=parsed_data.get('name', ''),
                    headline=parsed_data.get('summary', '')[:100] if parsed_data.get('summary') else None,
                    contact=contact,
                    summary=parsed_data.get('summary', ''),
                    experience=experience_items,
                    education=education_items,
                    skills=skills_list
                )
                
                print(f"✅ Converted to Resume schema: {len(experience_items)} experience, {len(education_items)} education, {len(skills_list)} skills")
                return _normalize_resume(resume)
                
            except Exception as e:
                print(f"⚠️ Comprehensive parser failed, using fallback: {e}")
                # Fallback to original parser
                fallback = parse_resume_text_to_schema(sanitize_input_text(resume_text))
                return _normalize_resume(fallback)
        
        return _normalize_resume(Resume())

    @staticmethod
    def render_preview(template_id: str, resume_json: Dict[str, Any] | None = None, resume_text: str | None = None, bundle: str | None = None) -> str:
        print(f"🔥 TEMPLATE ENGINE RECEIVED:")
        print(f"  - template_id: {template_id}")
        print(f"  - resume_json keys: {resume_json.keys() if resume_json else 'None'}")
        print(f"  - resume_text length: {len(resume_text) if resume_text else 0}")
        if resume_json:
            print(f"  - resume_json['name']: {resume_json.get('name', 'NO NAME')}")
            print(f"  - resume_json['experience']: {str(resume_json.get('experience', ''))[:100]}")
        
        print(f"🎨 TemplateEngine: Rendering template '{template_id}' with resume_text length: {len(resume_text) if resume_text else 0}")
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        print(f"📊 Resume object: name='{resume.name}', experience={len(resume.experience)}, education={len(resume.education)}")
        # Force template to executive_compact; scrub raw_text too
        raw = sanitize_input_text(resume_text) if resume_text else None
        raw = scrub_noise(raw) if raw else None
        cleaned_resume = clean_and_compact(resume.model_dump())
        html = render_html(
            bundle or DEFAULT_TEMPLATE,
            Resume.model_validate(cleaned_resume),
            raw_text=raw,
            request_params={"template": DEFAULT_TEMPLATE, "bypass_sanitization": True},
        )
        print(f"📄 Generated HTML length: {len(html)} characters")
        return html

    @staticmethod
    async def render_pdf(
        template_id: str,
        resume_json: Dict[str, Any] | None = None,
        resume_text: str | None = None,
        bundle: str | None = None
    ) -> bytes:
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        cleaned = clean_and_compact(resume.model_dump())
        raw = sanitize_input_text(resume_text) if resume_text else None
        raw = scrub_noise(raw) if raw else None
        html = render_html(
            bundle or DEFAULT_TEMPLATE,
            Resume.model_validate(cleaned),
            raw_text=raw,
            request_params={"template": DEFAULT_TEMPLATE, "bypass_sanitization": True},
        )
        pdf_bytes = await render_pdf_from_html(html, page_size="Letter")
        return pdf_bytes

    @staticmethod
    def render_pdf_sync(
        template_id: str,
        resume_json: Dict[str, Any] | None = None,
        resume_text: str | None = None,
        bundle: str | None = None,
    ) -> bytes:
        result: bytes | None = None
        error: Exception | None = None

        def _worker():
            nonlocal result, error
            try:
                result = asyncio.run(
                    TemplateEngine.render_pdf(
                        template_id=template_id,
                        resume_json=resume_json,
                        resume_text=resume_text,
                        bundle=bundle,
                    )
                )
            except Exception as exc:  # pragma: no cover
                error = exc

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        thread.join()

        if error:
            raise error
        if result is None:
            raise RuntimeError("PDF generation returned no result")
        return result


