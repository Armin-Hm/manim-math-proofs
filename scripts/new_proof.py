import argparse
from pathlib import Path

ROOT_FOLDER = "اثبات-های-ریاضی"

SCENE_TEMPLATE = '''from manim import *


class MainScene(Scene):
    def construct(self):
        title = Text("{title}", font_size=44)
        self.play(Write(title))
        self.wait(1)

        note = Text("اینجا مراحل اثبات را اضافه کن", font_size=30)
        note.next_to(title, DOWN, buff=1)

        self.play(Write(note))
        self.wait(2)
'''


def main():
    parser = argparse.ArgumentParser(
        description="Create a new math proof folder with starter files."
    )
    parser.add_argument(
        "folder_name",
        help="English folder name, example: pythagorean_theorem"
    )
    parser.add_argument(
        "title",
        help="Persian or English title of the proof"
    )

    args = parser.parse_args()

    base = Path(ROOT_FOLDER) / args.folder_name
    assets = base / "assets"

    base.mkdir(parents=True, exist_ok=True)
    assets.mkdir(exist_ok=True)

    files = {
        base / "scene.py": SCENE_TEMPLATE.format(title=args.title),
        base / "script.fa.md": f"# سناریوی فارسی: {args.title}\n\nمتن روایت اینجا نوشته شود.\n",
        base / "README.md": f"# {args.title}\n\nاین فولدر شامل کد، سناریو و فایل‌های مربوط به این اثبات است.\n",
        assets / ".gitkeep": "",
    }

    for path, content in files.items():
        if path.exists():
            print(f"Skipped existing file: {path}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Created: {path}")

    print(f"\nProof folder is ready: {base}")


if __name__ == "__main__":
    main()
