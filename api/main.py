"""de-ai MVP: evidence-based, deterministic content inspection API."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="de-ai Inspector", version="0.1.0", description="Rule-based Text and UI checks; no AI provenance claims.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class InspectRequest(BaseModel):
    modality: Literal["text", "ui"]
    content: str = Field(min_length=1, max_length=200_000)

class Issue(BaseModel):
    code: str
    severity: Literal["info", "minor", "major"]
    message: str
    evidence: str
    start: int | None = None
    end: int | None = None
    suggestion: str

class InspectResponse(BaseModel):
    modality: str
    issues: list[Issue]
    disclaimer: str = "Heuristic inspection, not AI-origin detection or a substitute for human review."

PHRASES = {
    "不仅": ("不仅", "Check whether this contrast adds useful information."),
    "更是": ("更是", "Consider replacing rhetorical escalation with a specific claim."),
    "赋能": ("赋能", "Name the concrete capability or outcome instead."),
    "颠覆性": ("颠覆性", "Provide evidence for the strength of this claim."),
    "未来已来": ("未来已来", "Replace a slogan with a verifiable observation."),
    "revolutionize": ("revolutionize", "Describe the measurable change instead."),
    "game-changing": ("game-changing", "Give a concrete example or evidence."),
    "in today's fast-paced world": ("in today's fast-paced world", "Remove generic scene-setting."),
}
def text_inspect(content: str) -> list[Issue]:
    issues: list[Issue] = []
    lower = content.lower()
    for phrase, (label, suggestion) in PHRASES.items():
        start = 0
        while (pos := lower.find(phrase.lower(), start)) >= 0:
            issues.append(Issue(code="text.cliche", severity="minor", message="Potentially formulaic wording", evidence=content[pos:pos+len(phrase)], start=pos, end=pos+len(phrase), suggestion=suggestion))
            start = pos + len(phrase)
    for match in re.finditer(r"(?<![\w])(?:100%|绝对|永远|完全保证|always|never)(?![\w])", content, flags=re.I):
        issues.append(Issue(code="text.absolute_claim", severity="major", message="Absolute claim may need qualification or evidence", evidence=match.group(), start=match.start(), end=match.end(), suggestion="Verify the claim, cite evidence, or qualify its scope."))
    return sorted(issues, key=lambda issue: issue.start if issue.start is not None else 0)

class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues: list[Issue] = []
        self.buttons = 0
        self.main_count = 0
        self.html_lang = False
        self.input_labels: set[str] = set()
        self.inputs: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = bool(a.get("lang", "").strip())
        if tag == "main":
            self.main_count += 1
        if tag == "img" and not a.get("alt", "").strip() and "alt" not in a:
            self.issues.append(Issue(code="ui.image.alt", severity="major", message="Image missing alt attribute", evidence=self.get_starttag_text() or "<img>", suggestion="Add meaningful alt text or alt=\"\" for decorative images."))
        if tag == "button":
            self.buttons += 1
        if tag == "label" and a.get("for"):
            self.input_labels.add(a["for"])
        if tag == "input" and a.get("type", "text").lower() not in {"hidden", "submit", "button", "reset", "image"}:
            self.inputs.append(a)

    def finish(self) -> list[Issue]:
        if not self.html_lang:
            self.issues.append(Issue(code="ui.document.lang", severity="minor", message="Document language is missing", evidence="<html>", suggestion="Set the html lang attribute to the page language."))
        if self.main_count == 0:
            self.issues.append(Issue(code="ui.landmark.main", severity="minor", message="No main landmark found", evidence="<main>", suggestion="Add one main landmark for primary page content."))
        for a in self.inputs:
            if not (a.get("aria-label") or a.get("aria-labelledby") or (a.get("id") and a["id"] in self.input_labels)):
                self.issues.append(Issue(code="ui.form.label", severity="major", message="Input may lack an accessible name", evidence=f'<input id="{a.get("id", "")}">', suggestion="Associate a label or provide a valid accessible name."))
        return self.issues

def ui_inspect(content: str) -> list[Issue]:
    inspector = HTMLAudit()
    inspector.feed(content)
    inspector.close()
    return inspector.finish()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}

@app.post("/v1/inspect", response_model=InspectResponse)
def inspect(request: InspectRequest) -> InspectResponse:
    return InspectResponse(modality=request.modality, issues=text_inspect(request.content) if request.modality == "text" else ui_inspect(request.content))
