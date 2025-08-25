import asyncio
import pytest
from models.resume_schema import Resume
from services.template_engine import TemplateEngine


async def _render():
    resume = Resume(name="Test User")
    pdf = await TemplateEngine.render_pdf("modern", resume_json=resume.model_dump(), resume_text="Test User\nAtlanta, GA\ntest@example.com\n\nExperience\n- Did something")
    return pdf


def test_render_pdf_smoke():
    try:
        import playwright  # noqa: F401
    except Exception:
        pytest.skip("Playwright not installed")
    pdf_bytes = asyncio.get_event_loop().run_until_complete(_render())
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 1000  # minimal sanity
    assert pdf_bytes[:4] == b"%PDF"


