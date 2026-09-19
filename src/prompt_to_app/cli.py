import argparse
from .orchestrator import build
from .vercel import VercelError,deploy
from .llm import CloudLLMError,GeminiLLM

def main()->int:
    parser=argparse.ArgumentParser(description="Prompt → App")
    parser.add_argument("prompt",help="Describe the application to build")
    parser.add_argument("--output",default="./generated-app")
    parser.add_argument("--model",default="qwen2.5-coder:7b")
    parser.add_argument("--ollama-url",default="http://127.0.0.1:11434")
    parser.add_argument("--serve",action="store_true")
    parser.add_argument("--browser",action="store_true")
    parser.add_argument("--cloud",action="store_true",help="Use Gemini for generation and deploy to Vercel")
    parser.add_argument("--cloud-model",default="gemini-2.5-flash")
    parser.add_argument("--cloud-name",default="prompt-to-app")
    parser.add_argument("--port",type=int,default=8000)
    parser.add_argument("--max-repairs",type=int,default=2)
    args=parser.parse_args()
    try:
        llm=GeminiLLM(model=args.cloud_model) if args.cloud else None
    except CloudLLMError as exc:
        print(f"cloud generation failed: {exc}"); return 1
    plan,project_dir,errors,url,repairs=build(args.prompt,args.output,model=args.model,base_url=args.ollama_url,
        serve=args.serve and not args.cloud,port=args.port,max_repairs=args.max_repairs,
        browser=args.browser and not args.cloud,llm=llm)
    print(f"project: {project_dir}\nname: {plan.name}\nstack: {', '.join(plan.stack)}\nfiles: {', '.join(plan.files)}\nrepairs: {repairs}")
    if args.cloud:
        try:
            cloud_url=deploy({str(p.relative_to(project_dir)):p.read_text(encoding="utf-8") for p in project_dir.rglob("*") if p.is_file() and ".git" not in p.parts},name=args.cloud_name)
        except VercelError as exc:
            print(f"cloud deployment failed: {exc}");return 1
        print(f"url: {cloud_url}");return 0
    if url: print(f"url: {url}")
    if errors:
        print("verification: failed")
        for error in errors: print(f"- {error}")
        return 1
    print("verification: passed");return 0

if __name__=="__main__": raise SystemExit(main())
