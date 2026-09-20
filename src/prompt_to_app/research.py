"""Adaptive, bounded research for Prompt -> App."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence
from .evidence import rank_sources

@dataclass
class ResearchSource:
    title:str; url:str; summary:str=""; relevance:str=""; category:str=""; evidence_score:float=0.0; evidence_tier:str="low"

@dataclass
class ResearchReport:
    prompt:str; depth:str="standard"; user_requirements:list[str]=field(default_factory=list)
    research_questions:list[str]=field(default_factory=list); sources:list[ResearchSource]=field(default_factory=list)
    product_findings:list[str]=field(default_factory=list); ux_findings:list[str]=field(default_factory=list)
    visual_findings:list[str]=field(default_factory=list); technical_findings:list[str]=field(default_factory=list)
    open_questions:list[str]=field(default_factory=list); assumptions:list[str]=field(default_factory=list); rounds:int=0
    def as_dict(self):
        return {"prompt":self.prompt,"depth":self.depth,"user_requirements":self.user_requirements,"research_questions":self.research_questions,
                "sources":[s.__dict__ for s in self.sources],"product_findings":self.product_findings,"ux_findings":self.ux_findings,
                "visual_findings":self.visual_findings,"technical_findings":self.technical_findings,"open_questions":self.open_questions,
                "assumptions":self.assumptions,"rounds":self.rounds}

def research_depth(prompt):
    text=prompt.lower(); signals=sum(x in text for x in ("platform","marketplace","social","dashboard","saas","ecommerce","ai","health","finance","analytics","current","trend","modern"))
    if signals>=2 or len(prompt.split())>=30:return "deep",5,25
    if signals==1 or len(prompt.split())>=12:return "standard",3,15
    return "quick",2,8

def initial_research_questions(prompt,depth="standard"):
    base=[f"Current products and apps similar to: {prompt}",f"Common features and user expectations for: {prompt}",
          f"Current UX and interaction patterns for: {prompt}",f"Current visual and responsive UI patterns for: {prompt}",
          f"Practical technical implementation patterns for: {prompt}"]
    if depth=="quick":return base[:3]
    if depth=="deep":return base+[f"Competitor strengths and weaknesses for: {prompt}",f"Recent 2026 trends and launches related to: {prompt}",
      f"Accessibility, privacy, security and edge cases for: {prompt}",f"Retention, onboarding and engagement patterns for: {prompt}"]
    return base

@dataclass
class ResearchEngine:
    search:Callable[[str],Sequence[Mapping[str,object]]]; max_rounds:int|None=None; max_sources:int|None=None
    def run(self,prompt):
        if not prompt.strip():raise ValueError("prompt cannot be empty")
        depth,default_rounds,limit=research_depth(prompt); rounds=self.max_rounds or default_rounds; limit=self.max_sources or limit
        report=ResearchReport(prompt.strip(),depth); questions=initial_research_questions(prompt,depth); report.research_questions.extend(questions)
        seen=set()
        for n in range(1,rounds+1):
            report.rounds=n
            if len(report.sources)>=limit:break
            batch=[]
            for q in questions:
                for item in self.search(q):
                    url=str(item.get("url","")).strip()
                    if not url or url in seen:continue
                    seen.add(url); batch.append(dict(item))
            ranked=rank_sources(batch)
            for item in ranked[:max(0,limit-len(report.sources))]:
                report.sources.append(ResearchSource(str(item.get("title",item["url"])),item["url"],str(item.get("summary") or item.get("snippet") or ""),
                  str(item.get("relevance","")),str(item.get("category") or "research"),float(item["evidence_score"]),str(item["evidence_tier"])))
            if n<rounds: questions=self._followups(prompt,report)
        report.product_findings.append(f"Reviewed {len(report.sources)} unique public sources at {depth} research depth.")
        report.assumptions.append("Explicit user requirements take priority over research recommendations.")
        if not report.sources:report.open_questions.append("No usable public sources were returned.")
        return report
    @staticmethod
    def _followups(prompt,report):
        return [f"Specific UX gaps and friction points in {prompt}",f"Accessibility and responsive design considerations for {prompt}",
                f"Implementation pitfalls and edge cases for {prompt}"]
