import argparse
from .orchestrator import build

def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt → App")
    parser.add_argument("prompt", help="Describe the application to build")
    parser.add_argument("--output", default="./generated-app")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--serve", action="store_true", help="Start the generated app and verify HTTP reachability")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-repairs", type=int, default=2)
    args = parser.parse_args()

    plan, project_dir, errors, url, repairs = build(
        args.prompt,
        args.output,
        model=args.model,
        base_url=args.ollama_url,
        serve=args.serve,
        port=args.port,
        max_repairs=args.max_repairs,
    )
    print(f"project: {project_dir}")
    print(f"name: {plan.name}")
    print(f"stack: {', '.join(plan.stack)}")
    print(f"files: {', '.join(plan.files)}")
    print(f"repairs: {repairs}")
    if url:
        print(f"url: {url}")
    if errors:
        print("verification: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("verification: passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
