from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prompt_to_app.llm import CloudLLMError, GeminiLLM
from prompt_to_app.orchestrator import build
from prompt_to_app.vercel import VercelError, deploy

app = FastAPI(title="Prompt → App API")


class BuildRequest(BaseModel):
    prompt: str
    name: str | None = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/build")
def build_app(request: BuildRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt cannot be empty")
    try:
        llm = GeminiLLM()
        with TemporaryDirectory() as temp_dir:
            plan, project_dir, errors, _, repairs = build(
                request.prompt,
                output_dir=Path(temp_dir) / "app",
                max_repairs=2,
                llm=llm,
            )
            if errors:
                raise HTTPException(status_code=422, detail={"errors": errors})
            files = {
                str(path.relative_to(project_dir)): path.read_text(encoding="utf-8")
                for path in project_dir.rglob("*")
                if path.is_file()
            }
            url = deploy(files, name=request.name or plan.name)
        return {"name": plan.name, "status": "ready", "url": url, "repairs": repairs}
    except HTTPException:
        raise
    except CloudLLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except VercelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="build failed") from exc
