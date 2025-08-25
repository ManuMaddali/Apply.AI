from __future__ import annotations

"""
Canonical resume schema and parsing utilities.

This module defines a thin, ATS-friendly schema used by the new template engine.
Parsing uses conservative heuristics to extract basic structure from raw resume text
without being overly aggressive.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Link(BaseModel):
    label: str = Field(default="")
    url: str = Field(default="")


class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    links: List[Link] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    company: str = Field(default="")
    title: str = Field(default="")
    start: Optional[str] = None
    end: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str = Field(default="")
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    school: str = Field(default="")
    degree: Optional[str] = None
    end: Optional[str] = None


class Skill(BaseModel):
    name: str


class Resume(BaseModel):
    name: str = Field(default="")
    headline: Optional[str] = None
    contact: Contact = Field(default_factory=Contact)
    summary: Optional[str] = None
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines()]


def _is_probable_name(line: str) -> bool:
    if not line:
        return False
    low = line.lower().strip()
    if any(t in low for t in ["@", "http", "linkedin", "github", "phone", "email"]):
        return False
    # Avoid bullets or section headers
    if line.lstrip().startswith(("-", "•", "*", "–")):
        return False
    if low.rstrip(":") in {"summary", "professional summary", "experience", "work experience", "professional experience", "education", "skills", "projects"}:
        return False
    if len(line) > 80:
        return False
    words = [w for w in line.replace("  ", " ").split(" ") if w]
    return 1 < len(words) <= 5 and not line.isupper() and not line.endswith(":")


def _extract_contact(lines: List[str]) -> Contact:
    import re
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"\+?\d[\d\-().\s]{7,}\d")
    url_re = re.compile(r"https?://[^\s]+", re.I)

    email = None
    phone = None
    location = None
    links: List[Link] = []

    for line in lines[:6]:
        if not email and (m := email_re.search(line)):
            email = m.group(0)
        if not phone and (m := phone_re.search(line)):
            phone = m.group(0)
        # A naive location heuristic: commas and letters, no @ or http
        if not location and ("," in line) and ("@" not in line) and ("http" not in line.lower()):
            if len(line) <= 80 and any(c.isalpha() for c in line):
                location = line.strip()
        for m in url_re.findall(line):
            label = "Linked" if "linkedin" in m.lower() else ("GitHub" if "github" in m.lower() else "Link")
            links.append(Link(label=label, url=m))

    return Contact(email=email, phone=phone, location=location, links=links)


def _detect_sections(lines: List[str]) -> List[tuple]:
    """
    Detect section headers (supports inline content on the same line).
    Returns list of tuples: (index, section_key:str, inline_content:str)
    """
    import re
    sections_map = {
        "summary": [r"summary", r"professional\s+summary"],
        "experience": [r"experience", r"work\s+experience", r"professional\s+experience"],
        "projects": [r"projects?"],
        "education": [r"education", r"academic"],
        "skills": [r"skills", r"technical\s+skills"],
    }
    compiled = {k: re.compile(rf"^\s*(?:{'|'.join(v)})\s*:?\s*(.*)$", re.I) for k, v in sections_map.items()}
    detected: List[tuple] = []
    for idx, line in enumerate(lines):
        for key, pattern in compiled.items():
            m = pattern.match(line.strip())
            if m:
                inline = m.group(1).strip()
                detected.append((idx, key, inline))
                break
    return detected


def _collect_bullets(lines: List[str]) -> List[str]:
    bullets: List[str] = []
    bullet_prefixes = ("-", "•", "●", "*", "–", "—")
    for l in lines:
        if not l:
            continue
        stripped = l.lstrip()
        if stripped.startswith(bullet_prefixes):
            bullets.append(stripped.lstrip("-•●*–— "))
        else:
            # Treat as paragraph line
            bullets.append(l)
    return bullets


def parse_resume_text_to_schema(resume_text: str) -> Resume:
    lines = [l for l in _split_lines(resume_text) if l]

    # Name and headline detection
    name = ""
    headline = None
    if lines:
        # Try: explicit probable name
        for candidate in lines[:5]:
            if _is_probable_name(candidate):
                name = candidate.strip()
                break
        # Fallback: extract name-like tokens from first line before separators
        if not name:
            first = lines[0]
            token_prefix = first.split("•")[0].split("|")[0].strip()
            tokens = token_prefix.split()
            if len(tokens) >= 2:
                base_name = " ".join(tokens[:2])
                if any(x in token_prefix.lower() for x in ["@", "http"]) or "," in token_prefix or len(tokens) > 3:
                    name = base_name
                else:
                    name = token_prefix
        # Headline: first short, non-contact line after name
        for l in lines[:6]:
            if l != name and len(l) <= 80 and not any(x in l.lower() for x in ["@", "http", "linkedin", "github"]):
                # Avoid obvious section headers
                if l.lower().strip().rstrip(":") not in {"summary", "experience", "projects", "education", "skills"}:
                    headline = l
                    break

    contact = _extract_contact(lines)

    # Detect sections (supports inline content)
    detected = _detect_sections(lines)
    sections: dict = {}
    if detected:
        # Append sentinel to ease slicing
        boundaries = detected + [(len(lines), "_end", "")]
        for i in range(len(boundaries) - 1):
            start_idx, key, inline = boundaries[i]
            end_idx, _, _ = boundaries[i + 1]
            body = []
            if inline:
                body.append(inline)
            body.extend([l for l in lines[start_idx + 1:end_idx] if l])
            sections[key] = body
    else:
        # Fallback if no explicit sections found
        sections["summary"] = lines[:6]
        sections["experience"] = lines[6:]

    # Summary
    summary_lines = sections.get("summary", [])
    summary = " ".join(summary_lines[:8]) if summary_lines else None
    if not summary:
        # Fallback summary from non-contact first lines
        body_candidates = []
        for l in lines[1:10]:
            low = l.lower()
            if any(x in low for x in ["@", "http", "linkedin", "github", "phone"]):
                continue
            if any(low.startswith(h) for h in ["summary", "experience", "projects", "education", "skills"]):
                continue
            body_candidates.append(l)
        if body_candidates:
            summary = " ".join(body_candidates)[:400]

    # Experience items
    experience_items: List[ExperienceItem] = []
    exp_body = (
        sections.get("experience")
        or sections.get("work experience")
        or sections.get("professional experience")
        or []
    )
    if exp_body:
        bullets = _collect_bullets(exp_body)
        if not bullets:
            import re
            joined = " ".join(exp_body)
            candidates = [
                s.strip()
                for s in re.split(r"[•●\-\n\u2013\u2014]|(?<=[.!?])\s+", joined)
                if s.strip()
            ]
            bullets = candidates[:8]
        if bullets:
            experience_items.append(ExperienceItem(company="", title="", bullets=bullets))

    # Projects
    project_items: List[ProjectItem] = []
    proj_body = sections.get("projects") or []
    if proj_body:
        bullets = _collect_bullets(proj_body)
        project_items.append(ProjectItem(name="Projects", bullets=bullets))

    # Education
    education_items: List[EducationItem] = []
    edu_body = sections.get("education") or []
    for l in edu_body[:3]:
        if l:
            education_items.append(EducationItem(school=l[:80]))

    # Skills
    skills: List[Skill] = []
    skills_body = sections.get("skills") or sections.get("technical skills") or []
    if skills_body:
        tokens: List[str] = []
        for l in skills_body:
            tokens.extend([t.strip() for t in l.replace("•", ",").split(",") if t.strip()])
        seen = set()
        for t in tokens:
            tl = t.lower()
            if tl not in seen:
                seen.add(tl)
                skills.append(Skill(name=t))

    return Resume(
        name=name,
        headline=headline,
        contact=contact,
        summary=summary,
        experience=experience_items,
        projects=project_items,
        education=education_items,
        skills=skills,
    )


