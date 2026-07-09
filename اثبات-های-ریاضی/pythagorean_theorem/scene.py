from pathlib import Path

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

        title = Text("The Pythagorean Theorem", font_size=44)
        subtitle_text = Text("", font_size=28)
        subtitle_text.to_edge(DOWN)

        self.add(subtitle_text)

        narration_1 = "In this video, we will look at the main idea behind the Pythagorean theorem."
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

        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=64)
        formula.next_to(title, DOWN, buff=1)

        narration_2 = "In a right triangle, the square of one short side plus the square of the other short side equals the square of the longest side."
        start = self.time
        with self.voiceover(text=narration_2) as tracker:
            self.play(Write(formula))
            self.play(
                Transform(
                    subtitle_text,
                    Text(narration_2, font_size=20).to_edge(DOWN)
                )
            )
            self.wait(max(0, tracker.duration - 2))
        add_subtitle(narration_2, start, self.time)

        narration_3 = "So this is not just a formula. It is a geometric relationship between the areas of squares."
        start = self.time
        with self.voiceover(text=narration_3) as tracker:
            self.play(formula.animate.scale(1.15))
            self.play(
                Transform(
                    subtitle_text,
                    Text(narration_3, font_size=24).to_edge(DOWN)
                )
            )
            self.wait(max(0, tracker.duration - 2))
        add_subtitle(narration_3, start, self.time)

        SUBTITLE_FILE.write_text("\n".join(subtitles), encoding="utf-8")