from __future__ import annotations

import re

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from services.template_engine import TemplateEngine
from models.resume_schema import Resume, Contact, ExperienceItem, ProjectItem, EducationItem, Skill


def _render_sample_html() -> str:
    resume = Resume(
        name="Jane Doe",
        contact=Contact(email="jane@example.com", phone="(555) 555-1212", location="Austin, TX"),
        summary=(
            "Optimized Summary: I am a software engineer. I am a software engineer. "
            "FOR THIS POSITION you need Python."
        ),
        skills=[Skill(name="Python"), Skill(name="SQL"), Skill(name="AWS")],
        experience=[
            ExperienceItem(
                title="Senior Engineer",
                company="Acme",
                bullets=[
                    "- Led team of 5 engineers to deliver features",
                    "• Improved latency by 30%",
                    "I implemented CI/CD with GitHub Actions",
                    "Refactored modules",
                    "Optimized database indexes",
                    "Extra bullet that should be trimmed",
                ],
            )
        ],
        projects=[
            ProjectItem(
                name="Personal Projects",
                bullets=[
                    "Built data pipeline",
                    "Deployed on AWS",
                    "Added monitoring",
                    "One more that should be trimmed",
                ],
            ),
            ProjectItem(name="Side App", bullets=["Created REST API", "Added tests", "Dockerized"]),
            ProjectItem(name="Overflow", bullets=["Should be dropped"])  # third project should be dropped
        ],
        education=[EducationItem(school="State University", degree="BS CS", end="2020")],
    )
    html = TemplateEngine.render_preview("executive_compact", resume_json=resume.model_dump())
    return html


def test_banned_fragments_removed():
    html = _render_sample_html()
    banned = [
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
    hay = html.upper()
    for frag in banned:
        assert frag.upper() not in hay


def test_summary_length_and_dedupe():
    html = _render_sample_html()
    # Extract Summary paragraph
    m = re.search(r"<section class=\"summary[^>]*>.*?<p class=\"summary-text\">(.*?)</p>", html, re.S)
    assert m, "Summary section missing"
    text = re.sub(r"<[^>]+>", "", m.group(1))
    assert len(text) <= 280
    # Duplicated sentence should be deduped (appears once)
    assert text.lower().count("software engineer") == 1


def test_bullet_limits():
    html = _render_sample_html()
    # Experience bullets max 5
    exp_ul = re.findall(r"<section class=\"experience\">[\s\S]*?<ul>([\s\S]*?)</ul>", html)
    assert exp_ul, "Experience bullets missing"
    first_count = len(re.findall(r"<li>", exp_ul[0]))
    assert first_count <= 5
    # Projects limited to 2 and 3 bullets each
    proj_sections = re.findall(r"<section class=\"projects\">([\s\S]*?)</section>", html)
    assert proj_sections, "Projects section missing"
    items = re.findall(r"<div class=\"project avoid-break\">([\s\S]*?)</div>", proj_sections[0])
    assert len(items) <= 2
    for it in items:
        assert len(re.findall(r"<li>", it)) <= 3


def test_single_page_hint():
    html = _render_sample_html()
    # Check CSS contains single page hints
    assert "@page" in html and "margin: 0.5in" in html
    assert "page-break-inside: avoid" in html



