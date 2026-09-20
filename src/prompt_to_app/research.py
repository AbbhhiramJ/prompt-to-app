"""Adaptive, bounded research for Prompt -> App."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

@dataclass
class ResearchSource:
    title: str
    url: str
    summary: str = ""
    relevance: str = ""
    category: str = ""

@dataclass
class ResearchReport:
    prompt: str
    depth: str = "standard"
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
        return {"prompt":self.prompt,"depth":self.depth,"user_requirements":self.user_requirements,
                "research_questions":self.research_questions,"sources":[s.__dict__ for s in self.sources],
                "product_findings":self.product_findings,"ux_findings":self.ux_findings,
                "visual_findings":self.visual_findings,"technical_findings":self.technical_findings,
                "open_questions":self.open_questions,"assumptions":self.assumptions,"rounds":self.rounds}

def research_depth(prompt: str) -> tuple[str,int,int]:
    text=prompt.lower()
    signals=sum(x in text for x in ("platform","marketplace","social","dashboard","saas","ecommerce","ai","health","finance","analytics","current","trend","modern"))
    complexity=len(prompt.split())
    if signals>=2 or complexity>=30: return "deep",5,25
    if signals==1 or complexity>=12: return "standard",3,15
    return "quick",2,8

def initial_research_questions(prompt: str, depth: str = "standard") -> list[str]:
    text=prompt.strip()
    base=[f"Current products and apps similar to: {text}",
          f"Common features and user expectations for: {text}",
          f"Current UX and interaction patterns for: {text}",
          f"Current visual and responsive UI patterns for: {text}",
          f"Practical technical implementation patterns for: {text}"]
    if depth=="quick": return base[:3]
    if depth=="deep":
        return base+[
            f"Competitor strengths and weaknesses for: {text}",
            f"Recent 2026 trends and launches related to: {text}",
            f"Accessibility, privacy, security and edge cases for: {text}",
            f"Retention, onboarding and engagement patterns for: {text}",
        ]
    return base

@dataclass
class ResearchEngine:
    search: Callable[[str], Sequence[Mapping[str, object]]]
    max_rounds: int | None = None
    max_sources: int | None = None

    def run(self, prompt: str) -> ResearchReport:
        if not prompt.strip(): raise ValueError("prompt cannot be empty")
        depth,default_rounds,default_sources=research_depth(prompt)
        rounds=self.max_rounds or default_rounds
        sources_limit=self.max_sources or default_sources
        if rounds<1 or sources_limit<1: raise ValueError("research limits must be positive")
        report=ResearchReport(prompt=prompt.strip(),depth=depth)
        questions=initial_research_questions(prompt,depth)
        report.research_questions.extend(questions)
        for round_number in range(1,rounds+1):
            if len(report.sources)>=sources_limit: break
            report.rounds=round_number
            for question in questions:
                if len(report.sources)>=sources_limit: break
                for item in self.search(question):
                    if len(report.sources)>=sources_limit: break
                    url=str(item.get("url","")).strip()
                    if not url or any(s.url==url for s in report.sources): continue
                    category=str(item.get("category") or self._category(question))
                    report.sources.append(ResearchSource(
                        str(item.get("title",url)).strip(),url,
                        str(item.get("summary") or item.get("snippet") or "").strip(),
                        str(item.get("relevance","")).strip(),category))
            if round_number<rounds:
                questions=self._followups(prompt,report)
        self._synthesize(report)
        return report

    @staticmethod
    def _category(question: str) -> str:
        q=question.lower()
        if "competitor" in q or "product" in q: return "product"
        if "ux" in q or "onboarding" in q or "retention" in q: return "ux"
        if "visual" in q or "trend" in q or "responsive" in q: return "visual"
        return "technical"

    @staticmethod
    def _followups(prompt: str, report: ResearchReport) -> list[str]:
        combined=" ".join(s.summary+" "+s.title for s in report.sources).lower()
        qs=[f"Specific UX gaps and friction points in {prompt}",
            f"Accessibility and responsive design considerations for {prompt}",
            f"Implementation pitfalls and edge cases for {prompt}"]
        if "ai" in prompt.lower(): qs.append(f"AI interaction patterns and trust considerations for {prompt}")
        if "mobile" in combined or "responsive" in combined: qs.append(f"Mobile interaction details and navigation patterns for {prompt}")
        if "competitor" in combined or "product" in combined: qs.append(f"Differentiating features users expect from {prompt}")
        return qs

    @staticmethod
    def _synthesize(report: ResearchReport) -> None:
        combined=" ".join(s.title+" "+s.summary+" "+s.category for s in report.sources).lower()
        if report.sources: report.product_findings.append(f"Reviewed {len(report.sources)} public sources at {report.depth} research depth.")
        if "mobile" in combined or "responsive" in combined: report.ux_findings.append("Mobile/responsive behavior should be first-class.")
        if "accessib" in combined: report.ux_findings.append("Accessibility should be included in implementation.")
        if "dark" in combined or "theme" in combined: report.visual_findings.append("Theme/appearance preferences are relevant.")
        if "privacy" in combined or "security" in combined: report.technical_findings.append("Privacy/security constraints surfaced in research should be respected.")
        report.assumptions.append("Explicit user requirements take priority over research recommendations.")
        if not report.sources: report.open_questions.append("No usable public sources were returned; generation should avoid unsupported trend claims.")
