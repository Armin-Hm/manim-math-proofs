from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

config.background_color = "#0B1020"


class TestVoiceover(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="en", tld="com"))

        title = Text("Manim is working!", font_size=52, color=YELLOW)

        formula = MathTex(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            font_size=54,
        )

        formula.next_to(title, DOWN, buff=0.6)

        with self.voiceover(
            text="Manim is working. The voiceover system is also working."
        ) as tracker:
            self.play(Write(title), run_time=1.5)
            self.play(Write(formula), run_time=2.0)

            remaining_time = tracker.duration - 3.5

            if remaining_time > 0.1:
                self.wait(remaining_time)
            else:
                self.wait(0.5)

        self.wait(1)
