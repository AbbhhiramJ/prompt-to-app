"""Source quality scoring for research evidence."""
from __future__ import annotations
from urllib.parse import urlparse
from dataclasses import dataclass

@dataclass(frozen=True)
class EvidenceScore:
    score: float
    tier: str
    reasons: tuple[str,...]

AUTHORITATIVE_DOMAINS={"apple.com","developer.apple.com","google.com","developer.android.com","microsoft.com","github.com","vercel.com","w3.org","owasp.org","nist.gov"}
QUALITY_TERMS={"official","documentation","research","study","report","guideline","benchmark","survey"}

def score_source(title:str,url:str,summary:str="")->EvidenceScore:
    host=urlparse(url).netloc.lower().removeprefix("www.")
    score=0.45; reasons=[]
    if any(host==d or host.endswith("."+d) for d in AUTHORITATIVE_DOMAINS):
        score+=0.35; reasons.append("authoritative domain")
    if any(t in (title+" "+summary).lower() for t in QUALITY_TERMS):
        score+=0.10; reasons.append("evidence-oriented wording")
    if url.startswith("https://"):
        score+=0.05; reasons.append("HTTPS")
    if len(summary)>=180:
        score+=0.05; reasons.append("substantive summary")
    score=min(score,1.0)
    tier="high" if score>=0.75 else "medium" if score>=0.55 else "low"
    return EvidenceScore(round(score,2),tier,tuple(reasons))

def rank_sources(sources:list[dict])->list[dict]:
    ranked=[]
    for source in sources:
        s=score_source(str(source.get("title","")),str(source.get("url","")),str(source.get("summary","")))
        item=dict(source); item["evidence_score"]=s.score; item["evidence_tier"]=s.tier; item["evidence_reasons"]=list(s.reasons)
        ranked.append(item)
    return sorted(ranked,key=lambda x:x["evidence_score"],reverse=True)
