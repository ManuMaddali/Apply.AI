from __future__ import annotations

from typing import Any, Dict


def _prefer_backend(module_path: str, fallback_path: str, attr: str | None = None):
    try:
        mod = __import__(module_path, fromlist=['*'])
    except ImportError:
        mod = __import__(fallback_path, fromlist=['*'])
    return getattr(mod, attr) if attr else mod

from jinja2 import Environment, FileSystemLoader, select_autoescape

TemplateRegistry = _prefer_backend('backend.services.template_registry', 'services.template_registry', attr='TemplateRegistry')
Resume = _prefer_backend('backend.models.resume_schema', 'models.resume_schema', attr='Resume')
_content_filters = _prefer_backend('backend.services.content_filters', 'services.content_filters')
clean_and_compact = _prefer_backend('backend.services.cleaners', 'services.cleaners', attr='clean_and_compact')


sanitize_resume_dict = _content_filters.sanitize_resume_dict
sanitize_raw_lines = _content_filters.sanitize_raw_lines


def scrub_noise(text: str | None) -> str:
    """Remove banned fragments and squeeze whitespace for safer rendering."""
    return _content_filters.scrub_noise(text or "")


def dedupe_summary(summary: str | list[str] | None) -> str:
    """Collapse summary content into ≤280 characters without duplicates."""
    return _content_filters.dedupe_summary(summary or "", max_chars=280)


def truncate_bullets(bullets: list[str] | None, limit: int) -> list[str]:
    """Limit bullet lists while removing filler and first-person phrasing."""
    return _content_filters.truncate_bullets(bullets or [], max_bullets=limit)


def _deep_scrub(value: Any) -> Any:
    """Recursively apply ``scrub_noise`` to nested structures."""
    if value is None:
        return None
    if isinstance(value, str):
        return scrub_noise(value)
    if isinstance(value, list):
        return [_deep_scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: _deep_scrub(v) for k, v in value.items()}
    return value


def _present_if_none(end: str | None) -> str:
    return end if end else "Present"


def _join_comma(values: list[str] | None) -> str:
    if not values:
        return ""
    return ", ".join(values)


def _date_range(start: str | None, end: str | None) -> str:
    s = start or ""
    e = end or "Present"
    return f"{s} – {e}".strip()


def render_html(
    template_id: str,
    resume: Resume,
    raw_text: str | None = None,
    request_params: Dict[str, Any] | None = None,
) -> str:
    """
    Render HTML from a Jinja2 template bundle, inlining styles.css.
    """
    params = request_params or {}
    if not template_id:
        template_id = "executive_compact"
    template_name = params.get("template") or template_id or "executive_compact"

    # Allow explicit bypass of sanitisation when caller guarantees trusted data
    bypass_sanitization = bool(params.get("bypass_sanitization"))

    # Validate template bundle
    TemplateRegistry.validate(template_name)
    template_dir = TemplateRegistry.get_dir(template_name)

    # Inline CSS
    css_path = template_dir / "styles.css"
    inline_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    # Jinja environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["present_if_none"] = _present_if_none
    env.filters["join_comma"] = _join_comma
    env.filters["date_range"] = _date_range

    template = env.get_template("template.html.j2")

    # Normalize and sanitize resume dict to guarantee keys and enforce whitelist/limits
    raw_resume = resume.model_dump()
    raw_resume.setdefault("contact", {})
    raw_resume["contact"].setdefault("email", "")
    raw_resume["contact"].setdefault("phone", "")
    raw_resume["contact"].setdefault("location", "")
    raw_resume["contact"].setdefault("links", [])
    if not bypass_sanitization:
        raw_resume = _deep_scrub(raw_resume)
        raw_resume = sanitize_resume_dict(raw_resume)
    cleaned = clean_and_compact(raw_resume)
    contact = cleaned.setdefault("contact", {}) if isinstance(cleaned.get("contact"), dict) else {}
    contact.setdefault("email", "")
    contact.setdefault("phone", "")
    contact.setdefault("location", "")
    contact.setdefault("links", [])
    # Sanitize location to avoid entire header line being captured
    try:
        loc_raw = contact.get("location") or ""
        name_hint = (cleaned.get("name") or "").strip()
        if loc_raw:
            if any(x in loc_raw for x in ["@", "http", "|", "•"]):
                import re
                m = re.search(r"([A-Za-z .'-]+,\s*[A-Z]{2})(?![A-Za-z])", loc_raw)
                contact["location"] = m.group(1).strip() if m else ""
            else:
                # Remove leading name if present
                low_loc = loc_raw.lower()
                low_name = name_hint.lower()
                if low_name and low_loc.startswith(low_name):
                    trimmed = loc_raw[len(name_hint):].lstrip("-|•, ").strip()
                    contact["location"] = trimmed
    except Exception:
        pass
    # Compute display_name robustly
    raw_name = (cleaned.get("name") or "").strip()
    display_name = raw_name
    if raw_name:
        first_piece = raw_name.split("•")[0].split("|")[0].strip()
        tokens = [t for t in first_piece.replace("  ", " ").split(" ") if t]
        if len(tokens) >= 2:
            display_name = " ".join(tokens[:2])
        else:
            display_name = first_piece

    # Provide raw text and pre-split lines for graceful fallbacks in templates
    raw_lines = []
    if raw_text:
        raw_lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        raw_lines = sanitize_raw_lines(raw_lines)
        # Try to improve display_name from first raw line when needed
        try:
            if raw_lines:
                first = raw_lines[0]
                first_piece = first.split("•")[0].split("|")[0]
                # Drop trailing location after comma
                if "," in first_piece:
                    first_piece = first_piece.split(",")[0]
                tokens = [t for t in first_piece.replace("  ", " ").split(" ") if t]
                if len(tokens) >= 2:
                    display_name = " ".join(tokens[:2])
                elif tokens:
                    display_name = tokens[0]
        except Exception:
            pass

    # Heuristic content score to decide if we should show a raw-text fallback
    try:
        summary_text = (cleaned.get("summary") or "").strip()
        experience_list = cleaned.get("experience") or []
        bullets_count = 0
        titles_count = 0
        for item in experience_list:
            if isinstance(item, dict):
                bullets_count += len(item.get("bullets") or [])
                if (item.get("title") or "").strip():
                    titles_count += 1
        # Strong fallback rule: empty bullets or very short summary is insufficient
        insufficient_structure = (bullets_count == 0) or (len(summary_text) < 12)
        approx_len = len(summary_text) + bullets_count * 12 + titles_count * 6
        # Also consider templates that only show section headings with no body
        use_fallback = (insufficient_structure or approx_len < 60) and len(raw_lines) > 0
    except Exception:
        use_fallback = bool(raw_lines)

    context: Dict[str, Any] = {
        "resume": cleaned,
        "inline_css": inline_css,
        "display_name": display_name,
        "raw_text": raw_text or "",
        "raw_lines": raw_lines,
        "use_fallback": use_fallback,
    }

    html = template.render(**context)
    html = "<!-- EXECUTIVE_COMPACT v1 -->\n" + html
    return html


