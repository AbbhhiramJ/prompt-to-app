"""Evidence-aware product blueprint synthesis.

The host agent may provide an AI synthesizer. The deterministic fallback keeps
the pipeline useful without adding another credential or model dependency.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping

@dataclass
class AppBlueprint:
    core_loop: list[str] = field(default_factory=list)
    onboarding: list[str] = field(default_factory=list)
    logging: list[str] = field(default_factory=list)
    schedules: list[str] = field(default_factory=list)
    progress: list[str] = field(default_factory=list)
    streaks: list[str] = field(default_factory=list)
    reminders: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)
    gamification: list[str] = field(default_factory=list)
    privacy: list[str] = field(default_factory=list)
    mobile_ux: list[str] = field(default_factory=list)
    mvp_scope: list[str] = field(default_factory=list)
    evidence: list[dict[str,str]] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str,object]:
        return self.__dict__.copy()

Synthesizer = Callable[[str, Mapping[str,object]], Mapping[str,object]]

def synthesize(prompt: str, research: Mapping[str,object], synthesizer: Synthesizer|None=None) -> AppBlueprint:
    if synthesizer is not None:
        data=dict(synthesizer(prompt,research))
        return AppBlueprint(**{k:data[k] for k in AppBlueprint.__dataclass_fields__ if k in data})

    sources=research.get("sources",[])
    titles=" ".join(str(s.get("title","")) for s in sources).lower()
    blueprint=AppBlueprint(
        core_loop=["Open quickly","See today's relevant habits","Complete in one tap","Give immediate feedback","Return to progress view"],
        onboarding=["Keep setup short","Offer sensible starter habits","Ask only for information needed to begin"],
        logging=["One-tap completion","Support quick daily logging","Avoid forcing long forms"],
        schedules=["Support daily, weekly, and custom schedules"],
        progress=["Show useful progress at a glance","Reserve deeper analytics for an insights view"],
        streaks=["Avoid making a broken streak feel like failure","Consider momentum or recovery-friendly metrics"],
        reminders=["Make reminders user-controlled","Prefer contextual/personalized nudges over generic spam"],
        integrations=["Keep integrations out of the MVP unless explicitly requested","Design data boundaries so integrations can be added later"],
        gamification=["Treat gamification as optional rather than the core loop"],
        privacy=["Minimize collected data","Do not add tracking or third-party services by default"],
        mobile_ux=["Design mobile-first","Use large touch targets","Reduce navigation required for daily logging"],
        mvp_scope=["Today dashboard","Create/edit/delete habit","One-tap completion","Flexible schedule","Progress/insights","Theme support","Local persistence"],
        decisions=[],
        caveats=[],
    )
    if "114" in titles or any("114" in str(s) for s in sources):
        blueprint.decisions.append("Basic logging and flexible schedules are category expectations; differentiation should come from packaging and experience.")
    if "widget" in titles:
        blueprint.decisions.append("Consider a quick-action/widget surface when the target platform supports it; do not make it a web MVP dependency.")
    if "streak" in titles or "forgiv" in titles:
        blueprint.decisions.append("Make consistency visible without relying exclusively on rigid consecutive-day streaks.")
    blueprint.evidence=[
        {"title":str(s.get("title","")), "url":str(s.get("url","")), "role":str(s.get("category","research"))}
        for s in sources if s.get("url")
    ]
    blueprint.caveats.append("Individual product blogs describe their own experiments and should not be treated as universal market evidence.")
    return blueprint
