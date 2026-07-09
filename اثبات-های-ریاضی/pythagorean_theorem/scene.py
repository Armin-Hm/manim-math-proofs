from manim import *


class MainScene(Scene):
    def construct(self):
        title = Text("اثبات قضیه فیثاغورس", font_size=44)
        self.play(Write(title))
        self.wait(1)

        note = Text("اینجا مراحل اثبات را اضافه کن", font_size=30)
        note.next_to(title, DOWN, buff=1)

        self.play(Write(note))
        self.wait(2)
