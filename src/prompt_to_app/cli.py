import argparse
from .orchestrator import build

def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt → App")
    parser.add_argument("prompt", help="Describe the application to build")
    parser.add_argument("--output", default="./generated-app")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    args = parser.parse_args()

    plan, project_dir, errors = build(
        args.prompt,
        args.output,
        model=args.model,
        base_url=args.ollama_url,
    )
    print(f"project: {project_dir}")
    print(f"name: {plan.name}")
    print(f"stack: {', '.join(plan.stack)}")
    print(f"files: {', '.join(plan.files)}")
    if errors:
        print("verification: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("verification: passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
