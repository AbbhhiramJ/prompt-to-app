import argparse
from .orchestrator import build

def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt → App")
    parser.add_argument("prompt", help="Describe the application to build")
    parser.add_argument("--output", default="./generated-app")
    args = parser.parse_args()

    plan, project_dir, errors = build(args.prompt, args.output)
    print(f"project: {project_dir}")
    print(f"stack: {', '.join(plan.stack)}")
    if errors:
        print("verification: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("verification: passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
