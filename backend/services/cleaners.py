from __future__ import annotations

import re
from typing import Any, Dict, List


BANNED_PATTERNS = [
    r"^\s*FOR THIS POSITION:.*$",
    r"^\s*KEY QUALIFICATIONS:.*$",
    r"^\s*OPTIMIZED SUMMARY:.*$",
    r"^\s*Optimized Summary.*$",
    r"^\s*Light Mode.*$",
    r"keyword applied",
    r"\[?This resume has been optimized.*?\]?",
    r"\bWe Offer.*?Challenging.*",
    r"\bOfferChallenging\b",
    r"\bRELEVANT\b",
]


def _strip_banned(text: str) -> str:
    if not isinstance(text, str):
        return text
    result = text
    for pat in BANNED_PATTERNS:
        result = re.sub(pat, "", result, flags=re.IGNORECASE)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def sanitize_text(val: Any) -> Any:
    if isinstance(val, str):
        return _strip_banned(val)
    if isinstance(val, list):
        return [sanitize_text(v) for v in val]
    if isinstance(val, dict):
        return {k: sanitize_text(v) for k, v in val.items()}
    return val


def dedupe_summary(items: List[str], max_chars: int = 280) -> str:
    text = " ".join(i.strip() for i in items if i and isinstance(i, str) and i.strip())
    if not text:
        return ""
    seen: set[str] = set()
    out: List[str] = []
    for sent in re.split(r"(?<=[.!?]) +", text):
        cleaned = _strip_banned(sent)
        if not cleaned:
            continue
        key = re.sub(r"\W+", "", cleaned.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
        if sum(len(piece) for piece in out) >= max_chars:
            break
    result = " ".join(out)[:max_chars].rstrip()
    result = re.sub(r"\b(I|I'm|I am|seeking|looking)\b.*", "", result, flags=re.IGNORECASE).strip()
    return result


def compact_skills(skills: Any, limit_low: int = 8, limit_high: int = 16) -> List[str]:
    if not skills:
        return []
    parts: List[str] = []
    if isinstance(skills, str):
        parts = re.split(r"[,\|;/•]+", skills)
    else:
        for item in skills:
            if isinstance(item, str):
                parts.extend(re.split(r"[,\|;/•]+", item))
            elif isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str):
                    parts.extend(re.split(r"[,\|;/•]+", name))
    cleaned: List[str] = []
    for part in parts:
        token = _strip_banned(part)
        if not token:
            continue
        if len(token.split()) > 5:
            continue
        cleaned.append(token)
    seen: set[str] = set()
    output: List[str] = []
    for token in cleaned:
        lower = token.lower()
        if lower in seen:
            continue
        seen.add(lower)
        output.append(token)
        if len(output) >= limit_high:
            break
    if len(output) < limit_low and cleaned:
        extra = [t for t in cleaned if t.lower() not in seen]
        for token in extra:
            lower = token.lower()
            if lower in seen:
                continue
            seen.add(lower)
            output.append(token)
            if len(output) >= limit_low:
                break
    return output


def truncate_bullets(bullets: List[str], limit: int) -> List[str]:
    trimmed: List[str] = []
    for bullet in bullets or []:
        if not bullet:
            continue
        cleaned = re.sub(r"^[\-\u2022•]+", "", bullet).strip()
        cleaned = _strip_banned(cleaned)
        if not cleaned:
            continue
        trimmed.append(cleaned)
        if len(trimmed) >= limit:
            break
    return trimmed


def clean_and_compact(resume: Dict[str, Any]) -> Dict[str, Any]:
    data: Dict[str, Any] = sanitize_text(resume or {})
    summary = dedupe_summary([
        data.get("summary", ""),
        data.get("professional_summary", ""),
        data.get("optimized_summary", ""),
    ])
    data["summary"] = summary

    for key in (
        "optimized_summary",
        "professional_summary",
        "key_qualifications",
        "keyword_applied",
        "ats_score_panel",
        "light_mode",
        "target_company_blob",
    ):
        data.pop(key, None)

    data["skills"] = compact_skills(data.get("skills"))

    experience = data.get("experience") or []
    if isinstance(experience, list):
        for role in experience:
            if isinstance(role, dict):
                role["bullets"] = truncate_bullets(role.get("bullets", []), 5)

    projects = data.get("projects") or []
    if isinstance(projects, list):
        projects = projects[:2]
        for project in projects:
            if isinstance(project, dict):
                project["bullets"] = truncate_bullets(project.get("bullets", []), 3)
        data["projects"] = projects

    allowed = {
        "name",
        "location",
        "email",
        "phone",
        "links",
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "extras",
        "contact",
    }

    cleaned = {k: v for k, v in data.items() if k in allowed and v not in (None, "", [], {})}
    if "contact" in cleaned and isinstance(cleaned["contact"], dict):
        contact = {k: v for k, v in cleaned["contact"].items() if v not in (None, "", [], {})}
        if contact:
            cleaned["contact"] = contact
        else:
            cleaned.pop("contact", None)

    return cleaned


