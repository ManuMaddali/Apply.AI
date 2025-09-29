from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def _resolve_templates_root() -> Path:
    """Resolve templates root robustly regardless of working directory.

    Prefer path relative to this file: backend/templates.
    Fallback to repo-root/backed/templates when process cwd is repo root.
    """
    # Relative to this file: .../backend/services/template_registry.py -> .../backend/templates
    file_relative = Path(__file__).resolve().parents[1] / "templates"
    if file_relative.exists():
        return file_relative

    # Common alternate: running from repo root
    cwd_backend = Path.cwd() / "backend" / "templates"
    if cwd_backend.exists():
        return cwd_backend

    # Last resort: just return file_relative (validate() will raise a clear error later)
    return file_relative


TEMPLATES_ROOT = _resolve_templates_root()


class TemplateRegistry:
    """
    Registry for template bundles. Each bundle has:
      - template.html.j2
      - styles.css
      - meta.json
    """

    REQUIRED_FILES = ["template.html.j2", "styles.css", "meta.json"]

    @staticmethod
    def list_ids() -> List[str]:
        # Restrict externally visible templates to only the compact executive bundle
        return ["executive_compact"]

    @staticmethod
    def resolve_id(template_id: str) -> str:
        """Resolve aliases and fallbacks for template IDs.

        - executive_compact -> executive (if exists) else modern
        - if requested template does not exist, fallback to modern when available
        """
        # Prefer an actual on-disk directory match
        if (TEMPLATES_ROOT / template_id).exists():
            return template_id
        # Alias for new compact executive bundle
        if template_id == "executive_compact":
            if (TEMPLATES_ROOT / "executive").exists():
                return "executive"
            if (TEMPLATES_ROOT / "modern").exists():
                return "modern"
        # Generic fallback
        if (TEMPLATES_ROOT / "modern").exists():
            return "modern"
        return template_id

    @staticmethod
    def get_dir(template_id: str) -> Path:
        resolved = TemplateRegistry.resolve_id(template_id)
        return TEMPLATES_ROOT / resolved

    @staticmethod
    def get_meta(template_id: str) -> Dict:
        import json
        meta_path = TemplateRegistry.get_dir(template_id) / "meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Template '{template_id}' missing meta.json")
        with meta_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def validate(template_id: str) -> None:
        bundle_dir = TemplateRegistry.get_dir(template_id)
        if not bundle_dir.exists() or not bundle_dir.is_dir():
            raise FileNotFoundError(f"Template '{template_id}' not found at {bundle_dir}")
        for req in TemplateRegistry.REQUIRED_FILES:
            path = bundle_dir / req
            if not path.exists():
                raise FileNotFoundError(f"Template '{template_id}' missing required file: {req}")




