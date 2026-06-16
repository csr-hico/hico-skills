"""`python -m hico_skills` -> serve the MCP server + OnePager via uvicorn."""

from __future__ import annotations

from .config import load_settings
from .web import build_app


def main() -> None:
    settings = load_settings()
    app = build_app(settings)
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
