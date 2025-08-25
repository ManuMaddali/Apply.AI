import pytest
from services.template_registry import TemplateRegistry


def test_template_ids_exist():
    ids = TemplateRegistry.list_ids()
    # We expect at least these ids
    for expected in ["modern", "classic", "technical", "executive", "creative"]:
        assert expected in ids


def test_validate_required_files():
    for template_id in ["modern", "classic"]:
        TemplateRegistry.validate(template_id)


