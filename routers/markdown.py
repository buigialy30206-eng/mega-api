"""
Markdown to HTML API
Convert Markdown text to HTML. Pure Python.
"""

import re

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
async def root():
    return {"service": "Markdown to HTML API", "version": "1.0.0", "related": ["Text to Slug API", "URL Metadata Extractor API"]}

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

class MDResult(BaseModel):
    markdown: str
    html: str

def md_to_html(text: str) -> str:
    """Simple markdown to HTML converter."""
    lines = text.split("\n")
    html = []
    in_list = False

    for line in lines:
        # Headers
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            if in_list:
                html.append("</ul>")
                in_list = False
            level = len(m.group(1))
            html.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue

        # Unordered list
        m = re.match(r"^[-*+]\s+(.+)", line)
        if m:
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{m.group(1)}</li>")
            continue

        # Ordered list
        m = re.match(r"^\d+\.\s+(.+)", line)
        if m:
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<li>{m.group(1)}</li>")
            continue

        # Empty line
        if not line.strip():
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append("<br>")
            continue

        if in_list:
            html.append("</ul>")
            in_list = False

        # Code blocks
        if line.startswith("```"):
            html.append("<pre><code>" if "```" not in html[-1] else "</code></pre>")
            continue

        # Bold and italic
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)
        line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)
        # Links
        line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)

        if line.strip():
            html.append(f"<p>{line}</p>")

    if in_list:
        html.append("</ul>")

    return "\n".join(html)

