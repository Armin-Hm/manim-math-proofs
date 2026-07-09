import argparse
from pathlib import Path
from string import Template

ROOT_FOLDER = "اثبات-های-ریاضی"


SCENE_TEMPLATE = Template(r'''from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


SUBTITLE_FILE = Path(__file__).parent / "subtitles.en.srt"


def format_srt_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


class MainScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="en"))

        subtitles = []
        subtitle_index = 1

        def add_subtitle(text, start_time, end_time):
            nonlocal subtitle_index

            subtitles.append(
                f"{subtitle_index}\n"
                f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
                f"{text}\n"
            )

            subtitle_index += 1

        title = Text("$title", font_size=44)
        subtitle_text = Text("", font_size=28)
        subtitle_text.to_edge(DOWN)

        self.add(subtitle_text)

        narration_1 = "In this video, we will explore the main idea behind $title."
        start = self.time
        with self.voiceover(text=narration_1) as tracker:
            self.play(Write(title))
            self.play(
                Transform(
                    subtitle_text,
                    Text(narration_1, font_size=24).to_edge(DOWN)
                )
            )
            self.wait(max(0, tracker.duration - 2))
        add_subtitle(narration_1, start, self.time)

        main_idea = Text("Add the main mathematical idea here", font_size=34)
        main_idea.next_to(title, DOWN, buff=1)

        narration_2 = "We will build the proof step by step, so that each part feels natural and connected."
        start = self.time
        with self.voiceover(text=narration_2) as tracker:
            self.play(Write(main_idea))
            self.play(
                Transform(
                    subtitle_text,
                    Text(narration_2, font_size=24).to_edge(DOWN)
                )
            )
            self.wait(max(0, tracker.duration - 2))
        add_subtitle(narration_2, start, self.time)

        conclusion = Text("Now replace this with the final insight.", font_size=32)
        conclusion.next_to(main_idea, DOWN, buff=0.8)

        narration_3 = "By the end, the result should not look like a memorized formula, but like something we can actually see."
        start = self.time
        with self.voiceover(text=narration_3) as tracker:
            self.play(FadeIn(conclusion))
            self.play(
                Transform(
                    subtitle_text,
                    Text(narration_3, font_size=22).to_edge(DOWN)
                )
            )
            self.wait(max(0, tracker.duration - 2))
        add_subtitle(narration_3, start, self.time)

        SUBTITLE_FILE.write_text("\n".join(subtitles), encoding="utf-8")
''')


def main():
    parser = argparse.ArgumentParser(
        description="Create a new math proof folder with English voiceover and subtitle support."
    )

    parser.add_argument(
        "folder_name",
        help="English folder name, example: quadratic_formula"
    )

    parser.add_argument(
        "title",
        help="English title of the proof, example: The Quadratic Formula"
    )

    args = parser.parse_args()

    base = Path(ROOT_FOLDER) / args.folder_name
    assets = base / "assets"

    base.mkdir(parents=True, exist_ok=True)
    assets.mkdir(exist_ok=True)

    files = {
        base / "scene.py": SCENE_TEMPLATE.substitute(title=args.title),
        base / "script.en.md": f"# Script: {args.title}\n\nWrite the English narration here.\n",
        base / "README.md": f"# {args.title}\n\nThis folder contains the Manim scene, narration script, assets, and generated subtitle workflow for this proof.\n",
        assets / ".gitkeep": "",
    }

    for path, content in files.items():
        if path.exists():
            print(f"Skipped existing file: {path}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Created: {path}")

    print(f"\nProof folder is ready: {base}")
    print("Render it with:")
    print(f"python scripts/render.py {args.folder_name} --quality low")

if __name__ == "__main__":
    main()
