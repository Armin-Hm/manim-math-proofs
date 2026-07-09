import argparse
import subprocess
from pathlib import Path

ROOT_FOLDER = "اثبات-های-ریاضی"
VENV_PYTHON = Path(".venv/bin/python")


def main():
    parser = argparse.ArgumentParser(
        description="Render a Manim proof video from the proofs folder."
    )

    parser.add_argument(
        "proof",
        help="Proof folder name, example: pythagorean_theorem"
    )

    parser.add_argument(
        "--scene",
        default="MainScene",
        help="Scene class name inside scene.py. Default: MainScene"
    )

    parser.add_argument(
        "--quality",
        default="low",
        choices=["low", "medium", "high"],
        help="Render quality: low, medium, or high"
    )

    args = parser.parse_args()

    if not VENV_PYTHON.exists():
        raise FileNotFoundError(
            "Virtual environment not found. Please run: bash install.sh"
        )

    scene_file = Path(ROOT_FOLDER) / args.proof / "scene.py"

    if not scene_file.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_file}")

    quality_flags = {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
    }

    command = [
        str(VENV_PYTHON),
        "-m",
        "manim",
        quality_flags[args.quality],
        str(scene_file),
        args.scene,
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()