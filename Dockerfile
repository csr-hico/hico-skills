FROM python:3.12-slim

WORKDIR /app

# Install the package first (its own layer) so dependency installs are cached across
# skill/frontend edits.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# Runtime data baked into the image. A skill change is a merge to main -> a rebuild.
COPY frontend ./frontend
COPY skills ./skills
COPY agents ./agents

ENV SKILLS_DIR=/app/skills \
    AGENTS_DIR=/app/agents \
    FRONTEND_DIR=/app/frontend \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)" || exit 1

CMD ["python", "-m", "hico_skills"]
