from __future__ import annotations

import re
from typing import Any, Dict, List, Union


JUNK_SECTION_HEADERS = {
    "LIGHT MODE TAILORED RESUME",
    "HEAVY MODE TAILORED RESUME",
    "KEYWORD OPTIMIZATION APPLIED",
    "OPTIMIZED SUMMARY",
    "KEY QUALIFICATIONS",
    "ATS SCORE",
    "ATS ANALYSIS",
    "ATS DETAILS",
    "MATCHED SKILLS",
    "MISSING SKILLS",
    "RECOMMENDATIONS",
}

# Global banned fragments to scrub from any text content (case-insensitive)
BANNED_FRAGMENTS = [
    "FOR THIS POSITION",
    "KEY QUALIFICATIONS",
    "OPTIMIZED SUMMARY",
    "Light Mode",
    "keyword enhancement",
    "keyword applied",
    "RELEVANT",
    "Company Name Not Found",
    "Understanding Recruitment",
]

PLACEHOLDER_COMPANIES = {
    "Company Name",
    "Unknown Company",
    "LinkedIn Company",
    "Indeed Partner Company",
}


def sanitize_input_text(raw_text: str) -> str:
    """Remove JD-derived junk and debug labels from raw input text.

    - Strips known debug blocks and ATS-related headings
    - Removes fence separators and redundant headers
    - Normalizes bullets
    """
    if not raw_text:
        return raw_text

    lines = [ln.rstrip() for ln in raw_text.splitlines()]
    cleaned: List[str] = []
    skip_block = False

    for line in lines:
        stripped = line.strip()

        # Detect and enter junk block as soon as we hit the heading
        if stripped:
            upper = stripped.upper()
            if any(hdr in upper for hdr in JUNK_SECTION_HEADERS):
                skip_block = True
                continue

        if skip_block:
            if not stripped:
                # Blank line ends the junk block
                skip_block = False
                continue
            if set(stripped) <= {"-"} or set(stripped) <= {"="}:
                # Separator line ends the junk block
                skip_block = False
                continue
            # Skip all lines inside the junk block
            continue

        if not stripped:
            continue

        # Normalize LaTeX bullets
        stripped = stripped.replace("\\bullet", "•")

        # Remove lingering labels like "Professional Summary:" at line start
        stripped = re.sub(r"^(professional\s+summary|summary|optimized\s+summary)\s*:?\s*",
                          "",
                          stripped,
                          flags=re.IGNORECASE)

        cleaned.append(stripped)

    return "\n".join(cleaned)


def _truncate_text(text: str, max_chars: int) -> str:
    if not text:
        return text
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    # Try to cut at a sentence boundary or word boundary
    truncated = text[:max_chars]
    # Backtrack to nearest space to avoid cutting a word
    space_idx = truncated.rfind(" ")
    if space_idx >= max_chars * 0.7:
        truncated = truncated[:space_idx]
    return truncated.rstrip(" ,.;:-") + "…"


def dedupe_summary(summary: Union[str, List[str]], max_chars: int = 280) -> str:
    """Collapse multiple summaries into one ≤ max_chars with sentence-level dedupe.

    Accepts string or list of strings. Removes labels, duplicated sentences, filler,
    first-person tone, and normalizes whitespace and dashes.
    """
    if not summary:
        return ""
    if isinstance(summary, list):
        summary = " ".join([str(s) for s in summary if s])
    # Remove common labels
    clean = re.sub(r"^(professional\s+summary|summary|optimized\s+summary)\s*:?\s*",
                   "",
                   str(summary).strip(),
                   flags=re.IGNORECASE)
    # Normalize whitespace and dashes
    clean = re.sub(r"\s+", " ", clean)
    clean = re.sub(r"\s*[\-\u2014\u2013]\s*", " – ", clean)
    clean = clean.lstrip(" :;,-")
    # Remove obvious first-person intros/filler
    clean = re.sub(r"\b(i\s+am|i'm|i\s+have|i\s+like|my\s+passion\s+is)\b[^.]*\.\s*", "", clean, flags=re.I)
    # Sentence-level dedupe (case-insensitive)
    parts = [p.strip(" :;,-") for p in re.split(r"(?<=[.!?])\s+", clean) if p.strip()]
    seen = set()
    unique_parts: List[str] = []
    for p in parts:
        norm = re.sub(r"^[^A-Za-z0-9]+", "", p.lower())
        norm = re.sub(r"^(am|are|was|were)\s+", "", norm)
        if norm in seen:
            continue
        seen.add(norm)
        unique_parts.append(p)
    # Scrub noise and truncate
    return _truncate_text(scrub_noise(" ".join(unique_parts)), max_chars)


def truncate_bullets(bullets: List[str], max_bullets: int = 5, max_chars_per_bullet: int = 200) -> List[str]:
    """Limit bullets count, drop leading markers, remove first-person tone, and truncate."""
    if not bullets:
        return []
    result: List[str] = []
    for b in bullets[:max_bullets]:
        raw = str(b or "")
        # Strip leading symbols and normalize whitespace
        bb = re.sub(r"^\s*([•\-*–]\s*)", "", raw).strip()
        # Remove first-person pronouns at start and common filler
        bb = re.sub(r"^(i\s+|i'm\s+|my\s+|we\s+|our\s+)", "", bb, flags=re.I)
        # Normalize dashes
        bb = re.sub(r"\s*[\-\u2014\u2013]\s*", " – ", bb)
        # Scrub banned fragments
        bb = scrub_noise(bb)
        result.append(_truncate_text(bb, max_chars_per_bullet))
    return result


def scrub_noise(text: str) -> str:
    """Remove banned fragments, ATS/junk labels, and squeeze whitespace.

    - Drops occurrences of phrases in BANNED_FRAGMENTS (case-insensitive)
    - Removes stray section labels in ALL CAPS (with optional colon)
    - Fixes common typos (e.g., 'Projets' -> 'Projects')
    - Normalizes whitespace and dashes
    """
    if not text:
        return ""
    s = str(text)
    # Remove banned fragments (case-insensitive)
    for frag in BANNED_FRAGMENTS:
        s = re.sub(re.escape(frag), "", s, flags=re.I)
    # Remove obvious all-caps labels like "SUMMARY:" at start
    s = re.sub(r"^(?:[A-Z][A-Z\s]{2,}):?\s*", "", s)
    # Fix common typos
    s = re.sub(r"\bProjets\b", "Projects", s, flags=re.I)
    # Normalize first-person pronouns mid-sentence where safe (drop pronoun only)
    s = re.sub(r"\b(I|I'm|I've|I'd|Me|My|We|We're|We've|Our|Ours)\b\s*", "", s, flags=re.I)
    # Normalize dashes and whitespace
    s = re.sub(r"\s*[\-\u2014\u2013]\s*", " – ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _deep_scrub(value: Any) -> Any:
    """Recursively scrub strings within dicts/lists using scrub_noise."""
    if value is None:
        return None
    if isinstance(value, str):
        return scrub_noise(value)
    if isinstance(value, list):
        return [_deep_scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: _deep_scrub(v) for k, v in value.items()}
    return value


def sanitize_resume_dict(r: Dict[str, Any]) -> Dict[str, Any]:
    """Apply whitelist, sanitize text, and enforce one-pager heuristics.

    Keeps only [header/name/contact, summary, skills, experience, projects, education, extras].
    Drops empty content, trims long sections.
    """
    if not isinstance(r, dict):
        return r

    # Global deep scrub first
    r = _deep_scrub(r)

    # Ensure expected keys exist
    r.setdefault("name", "")
    r.setdefault("contact", {})
    r.setdefault("summary", "")
    r.setdefault("skills", [])
    r.setdefault("experience", [])
    r.setdefault("projects", [])
    r.setdefault("education", [])
    r.setdefault("extras", [])

    # Sanitize name/contact
    name = (r.get("name") or "").strip()
    r["name"] = re.sub(r"\s+", " ", name)

    # Clean contact fields
    contact = r.get("contact") or {}
    for k in ["email", "phone", "location"]:
        if k in contact and contact[k]:
            contact[k] = re.sub(r"\s+", " ", str(contact[k]).strip())
    # Filter links to http(s) and non-empty
    links = contact.get("links") or []
    safe_links = []
    for link in links:
        if isinstance(link, dict):
            label = (link.get("label") or "").strip()
            url = (link.get("url") or "").strip()
            if url and (url.startswith("http://") or url.startswith("https://")):
                safe_links.append({"label": label or "Link", "url": url})
    contact["links"] = safe_links
    r["contact"] = contact

    # Summary
    r["summary"] = dedupe_summary(r.get("summary") or "", max_chars=280)

    # Skills: list of dicts {name} or raw strings
    skills = r.get("skills") or []
    normalized_skills: List[str] = []
    for s in skills:
        if isinstance(s, dict):
            nm = (s.get("name") or "").strip()
        else:
            nm = str(s).strip()
        if nm:
            normalized_skills.append(nm)
    # Dedupe order-preserving and cap total
    seen = set()
    unique_skills: List[str] = []
    for nm in normalized_skills:
        low = nm.lower()
        if low in seen:
            continue
        seen.add(low)
        unique_skills.append(nm)
    # Keep as objects for templates expecting s.name
    r["skills"] = [{"name": nm} for nm in unique_skills[:20]]

    # Experience: list of dict items
    exp_items = r.get("experience") or []
    cleaned_exp: List[Dict[str, Any]] = []
    for item in exp_items[:4]:  # Soft cap to help one-pager
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        company = (item.get("company") or "").strip()
        if company in PLACEHOLDER_COMPANIES:
            company = ""
        dates = (item.get("dates") or "").strip()
        bullets = item.get("bullets") or []
        bullets = truncate_bullets(bullets, max_bullets=5, max_chars_per_bullet=200)
        # Drop items with no content
        if not (title or company or dates or bullets):
            continue
        cleaned_exp.append({
            "title": title,
            "company": company,
            "dates": dates,
            "bullets": bullets if len(bullets) >= 1 else bullets,
        })
    r["experience"] = cleaned_exp

    # Projects: limit to 2
    projects = r.get("projects") or []
    cleaned_projects: List[Dict[str, Any]] = []
    for proj in projects[:2]:
        if not isinstance(proj, dict):
            continue
        name = (proj.get("name") or "Project").strip()
        bullets = truncate_bullets(proj.get("bullets") or [], max_bullets=3, max_chars_per_bullet=180)
        if not (name or bullets):
            continue
        cleaned_projects.append({"name": name, "bullets": bullets})
    r["projects"] = cleaned_projects

    # Education: keep as-is but drop empties
    edu_items = []
    for edu in (r.get("education") or [])[:3]:
        if isinstance(edu, dict):
            school = (edu.get("school") or "").strip()
            if school:
                edu_items.append({"school": school})
        elif isinstance(edu, str) and edu.strip():
            edu_items.append({"school": edu.strip()})
    r["education"] = edu_items

    # Extras: optional additional bullets, limit for one-pager
    extras_items: List[str] = []
    extras = r.get("extras") or []
    if isinstance(extras, list):
        for it in extras[:4]:
            if isinstance(it, str) and it.strip():
                extras_items.append(_truncate_text(it.strip(), 160))
            elif isinstance(it, dict):
                # support {text: "..."}
                txt = (it.get("text") or "").strip()
                if txt:
                    extras_items.append(_truncate_text(txt, 160))
    r["extras"] = extras_items

    # Enforce section whitelist by returning a filtered dict used for rendering
    allowed = {
        "name": r.get("name"),
        "headline": r.get("headline"),
        "contact": r.get("contact"),
        "summary": r.get("summary"),
        "skills": r.get("skills"),
        "experience": r.get("experience"),
        "projects": r.get("projects"),
        "education": r.get("education"),
        "extras": r.get("extras"),
    }

    # Drop empty sections completely (rendering templates should check truthiness)
    for key in list(allowed.keys()):
        val = allowed[key]
        if val in (None, ""):
            del allowed[key]
        elif isinstance(val, list) and len(val) == 0:
            del allowed[key]

    # Final deep scrub to ensure no banned fragments leak through
    return _deep_scrub(allowed)


def sanitize_raw_lines(raw_lines: List[str]) -> List[str]:
    """Filter raw_lines used by fallback templates to remove junk and ATS panels."""
    if not raw_lines:
        return raw_lines
    out: List[str] = []
    for ln in raw_lines:
        u = ln.strip().upper()
        if not u:
            continue
        if any(h in u for h in JUNK_SECTION_HEADERS):
            continue
        if u.startswith("PROFESSIONAL SUMMARY") or u.startswith("SUMMARY"):
            # drop the label; keep actual text if on same line after colon
            after = re.sub(r"^(professional\s+summary|summary)\s*:?\s*",
                           "",
                           ln.strip(),
                           flags=re.IGNORECASE)
            if after:
                out.append(after)
            continue
        if u in {"---", "--", "==", "==="}:
            continue
        # Strip LaTeX bullets
        ln = ln.replace("\\bullet", "•")
        out.append(ln)
    return out


