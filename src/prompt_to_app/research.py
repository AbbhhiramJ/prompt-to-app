"""Bounded, structured research for Prompt -> App."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

@dataclass
class ResearchSource:
    title: str
    url: str
    summary: str = ""
    relevance: str = ""

@dataclass
class ResearchReport:
    prompt: str
    user_requirements: list[str] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    sources: list[ResearchSource] = field(default_factory=list)
    product_findings: list[str] = field(default_factory=list)
    ux_findings: list[str] = field(default_factory=list)
    visual_findings: list[str] = field(default_factory=list)
    technical_findings: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    rounds: int = 0
    def as_dict(self) -> dict[str, object]:
        return {"prompt":self.prompt,"user_requirements":self.user_requirements,"research_questions":self.research_questions,"sources":[s.__dict__ for s in self.sources],"product_findings":self.product_findings,"ux_findings":self.ux_findings,"visual_findings":self.visual_findings,"technical_findings":self.technical_findings,"open_questions":self.open_questions,"assumptions":self.assumptions,"rounds":self.rounds}

def initial_research_questions(prompt: str) -> list[str]:
    text=prompt.strip()
    return [f"Current products and apps similar to: {text}",f"Common features and user expectations for: {text}",f"Current UX and interaction patterns for: {text}",f"Current visual and responsive UI patterns for: {text}",f"Practical technical implementation patterns for: {text}"]

@dataclass
class ResearchEngine:
    search: Callable[[str], Sequence[Mapping[str, object]]]
    max_rounds: int = 4
    max_sources: int = 15
    def run(self, prompt: str) -> ResearchReport:
        if not prompt.strip(): raise ValueError("prompt cannot be empty")
        if self.max_rounds<1 or self.max_sources<1: raise ValueError("research limits must be positive")
        report=ResearchReport(prompt=prompt.strip())
        questions=initial_research_questions(prompt); report.research_questions.extend(questions)
        for round_number in range(1,self.max_rounds+1):
            if len(report.sources)>=self.max_sources: break
            report.rounds=round_number
            for question in questions:
                for item in self.search(question):
                    if len(report.sources)>=self.max_sources: break
                    url=str(item.get("url","")).strip()
                    if not url or any(s.url==url for s in report.sources): continue
                    report.sources.append(ResearchSource(str(item.get("title",url)).strip(),url,str(item.get("summary","")).strip(),str(item.get("relevance","")).strip()))
            if round_number<self.max_rounds:
                questions=[f"Specific UX gaps and friction points in {prompt}",f"Accessibility and responsive design considerations for {prompt}",f"Implementation pitfalls and edge cases for {prompt}"]
        combined=" ".join(s.title+" "+s.summary for s in report.sources).lower()
        if report.sources: report.product_findings.append(f"Reviewed {len(report.sources)} public sources related to the requested product.")
        if "mobile" in combined or "responsive" in combined: report.ux_findings.append("Mobile/responsive behavior should be treated as a first-class requirement.")
        if "accessib" in combined: report.ux_findings.append("Accessibility considerations should be included in the implementation.")
        if "dark" in combined or "theme" in combined: report.visual_findings.append("Theme and appearance preferences are relevant to the researched category.")
        report.assumptions.append("Explicit user requirements take priority over research recommendations.")
        return report
