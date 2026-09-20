"""Evidence-aware product blueprint synthesis."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Mapping

from .llm import LLM


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
    evidence: list[dict[str, str]] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


Synthesizer = Callable[[str, Mapping[str, object]], Mapping[str, object]]

SYNTHESIS_SYSTEM = """You are the product-research synthesis engine for Prompt -> App.
Compare the supplied research evidence and produce ONLY valid JSON with these keys:
core_loop,onboarding,logging,schedules,progress,streaks,reminders,integrations,gamification,privacy,mobile_ux,mvp_scope,decisions,caveats.
Each value is an array of concise strings.
Separate broad evidence from individual product claims. Do not invent facts.
Explicit user requirements have priority over research. Keep MVP practical.
"""


def _from_data(
    data: Mapping[str, object],
    sources: list[Mapping[str, object]],
) -> AppBlueprint:
    fields = AppBlueprint.__dataclass_fields__
    clean = {
        k: data[k]
        for k in fields
        if k in data and k != "evidence"
    }
    bp = AppBlueprint(**clean)
    bp.evidence = [
        {
            "title": str(s.get("title", "")),
            "url": str(s.get("url", "")),
            "role": str(s.get("category", "research")),
        }
        for s in sources
        if s.get("url")
    ]
    return bp


def synthesize(
    prompt: str,
    research: Mapping[str, object],
    synthesizer: Synthesizer | None = None,
    llm: LLM | None = None,
    model: str = "qwen2.5-coder:7b",
) -> AppBlueprint:
    sources = list(research.get("sources", []))

    if synthesizer is not None:
        try:
            return _from_data(dict(synthesizer(prompt, research)), sources)
        except (TypeError, KeyError, ValueError):
            pass

    if llm is not None:
        try:
            payload = {
                "user_prompt": prompt,
                "research": research,
            }
            # Keep this explicit so downstream planners and compatibility
            # adapters can distinguish researched planning from raw prompting.
            user_prompt = (
                "Research blueprint:\n"
                + json.dumps(payload, ensure_ascii=False)
            )
            data = json.loads(
                llm.generate(
                    SYNTHESIS_SYSTEM,
                    user_prompt,
                )
            )
            return _from_data(data, sources)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
        ):
            pass

    titles = " ".join(str(s.get("title", "")) for s in sources).lower()
    bp = AppBlueprint(
        core_loop=[
            "Open quickly",
            "See today's relevant items",
            "Complete in one tap",
            "Give immediate feedback",
            "Return to progress",
        ],
        onboarding=[
            "Keep setup short",
            "Offer sensible starter items",
            "Ask only for information needed to begin",
        ],
        logging=["One-tap completion", "Quick daily logging", "Avoid long forms"],
        schedules=["Support daily, weekly, and custom schedules"],
        progress=["At-a-glance progress", "Deeper analytics in insights"],
        streaks=[
            "Avoid punitive broken-streak UX",
            "Consider momentum or recovery-friendly metrics",
        ],
        reminders=["User-controlled reminders", "Prefer contextual nudges"],
        integrations=["Keep integrations out of MVP unless requested"],
        gamification=["Optional, not core"],
        privacy=["Minimize collected data", "No third-party tracking by default"],
        mobile_ux=[
            "Mobile-first",
            "Large touch targets",
            "Minimal navigation for daily actions",
        ],
        mvp_scope=[
            "Today dashboard",
            "Create/edit/delete",
            "One-tap completion",
            "Flexible schedule",
            "Progress/insights",
            "Theme",
            "Local persistence",
        ],
        caveats=[
            "Individual product experiments are evidence, not universal market truth."
        ],
    )
    if "114" in titles:
        bp.decisions.append(
            "Logging and flexible schedules appear to be category expectations; differentiate through experience."
        )
    if "widget" in titles:
        bp.decisions.append(
            "Consider quick actions/widgets when the target platform supports them."
        )
    if "streak" in titles or "forgiv" in titles:
        bp.decisions.append(
            "Make consistency visible without relying exclusively on rigid consecutive-day streaks."
        )
    bp.evidence = [
        {
            "title": str(s.get("title", "")),
            "url": str(s.get("url", "")),
            "role": str(s.get("category", "research")),
        }
        for s in sources
        if s.get("url")
    ]
    return bp
