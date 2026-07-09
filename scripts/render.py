import argparse
import shutil
import subprocess
import time
from pathlib import Path

ROOT_FOLDER = "اثبات-های-ریاضی"
VENV_PYTHON = Path(".venv/bin/python")
MEDIA_ROOT = Path("media/videos")
OUTPUT_ROOT = Path("outputs")


def find_latest_rendered_video(scene_name: str, started_at: float) -> Path:
    candidates = list(MEDIA_ROOT.rglob(f"{scene_name}.mp4"))

    fresh_candidates = [
        path for path in candidates
        if path.stat().st_mtime >= started_at
    ]

    if not fresh_candidates:
        raise FileNotFoundError(
            f"No freshly rendered video found for scene: {scene_name}"
        )

    return max(fresh_candidates, key=lambda path: path.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(
        description="Render a Manim proof video and copy it to a clean output folder."
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

    proof_folder = Path(ROOT_FOLDER) / args.proof
    scene_file = proof_folder / "scene.py"

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

    started_at = time.time()
    subprocess.run(command, check=True)

    rendered_video = find_latest_rendered_video(args.scene, started_at)

    output_folder = OUTPUT_ROOT / args.proof
    output_folder.mkdir(parents=True, exist_ok=True)

    final_video = output_folder / f"{args.proof}_{args.quality}.mp4"
    shutil.copy2(rendered_video, final_video)

    print(f"Video copied to: {final_video}")

    subtitle_source = proof_folder / "subtitles.en.srt"
    if subtitle_source.exists():
        final_subtitle = output_folder / f"{args.proof}_en.srt"
        shutil.copy2(subtitle_source, final_subtitle)
        print(f"Subtitle copied to: {final_subtitle}")
    else:
        print("No subtitle file found yet. Expected: subtitles.en.srt")


if __name__ == "__main__":
    main()