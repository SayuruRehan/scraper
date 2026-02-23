from __future__ import annotations

from pathlib import Path

from src.orchestrator import run_pipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    path = run_pipeline(project_root)
    print(f"Export created: {path}")
