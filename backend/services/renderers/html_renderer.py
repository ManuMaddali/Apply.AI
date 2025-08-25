from __future__ import annotations

from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

from services.template_registry import TemplateRegistry
from models.resume_schema import Resume


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


def render_html(template_id: str, resume: Resume, raw_text: str | None = None) -> str:
    """
    Render HTML from a Jinja2 template bundle, inlining styles.css.
    """
    # Validate template bundle
    TemplateRegistry.validate(template_id)
    template_dir = TemplateRegistry.get_dir(template_id)

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

    # Normalize resume dict to guarantee keys exist for templates
    r = resume.model_dump()
    r.setdefault("contact", {})
    r["contact"].setdefault("email", "")
    r["contact"].setdefault("phone", "")
    r["contact"].setdefault("location", "")
    r["contact"].setdefault("links", [])
    # Sanitize location to avoid entire header line being captured
    try:
        loc_raw = r["contact"].get("location") or ""
        name_hint = (r.get("name") or "").strip()
        if loc_raw:
            if any(x in loc_raw for x in ["@", "http", "|", "•"]):
                import re
                m = re.search(r"([A-Za-z .'-]+,\s*[A-Z]{2})(?![A-Za-z])", loc_raw)
                r["contact"]["location"] = m.group(1).strip() if m else ""
            else:
                # Remove leading name if present
                low_loc = loc_raw.lower()
                low_name = name_hint.lower()
                if low_name and low_loc.startswith(low_name):
                    cleaned = loc_raw[len(name_hint):].lstrip("-|•, ").strip()
                    r["contact"]["location"] = cleaned
    except Exception:
        pass
    # Compute display_name robustly
    raw_name = (r.get("name") or "").strip()
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
        summary_text = (r.get("summary") or "").strip()
        experience_list = r.get("experience") or []
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
        "resume": r,
        "inline_css": inline_css,
        "display_name": display_name,
        "raw_text": raw_text or "",
        "raw_lines": raw_lines,
        "use_fallback": use_fallback,
    }

    return template.render(**context)


