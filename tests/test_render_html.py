from models.resume_schema import Resume, Contact, ExperienceItem
from services.renderers.html_renderer import render_html


def test_render_html_includes_name_and_summary():
    resume = Resume(
        name="Alex Johnson",
        headline="Software Engineer",
        contact=Contact(email="alex@example.com"),
        summary="Experienced engineer building web apps.",
        experience=[ExperienceItem(company="Acme", title="Engineer", bullets=["Built things"])],
    )
    html = render_html("modern", resume, raw_text=None)
    assert "Alex Johnson" in html
    assert "Summary" in html


