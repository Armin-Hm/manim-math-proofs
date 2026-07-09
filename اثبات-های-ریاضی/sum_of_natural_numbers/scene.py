import textwrap
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


config.background_color = "#08111F"
config.frame_rate = 30

SUBTITLE_FILE = Path(__file__).parent / "subtitles.en.srt"


def format_srt_time(seconds):
    total_milliseconds = int(round(seconds * 1000))

    hours = total_milliseconds // 3_600_000
    total_milliseconds %= 3_600_000

    minutes = total_milliseconds // 60_000
    total_milliseconds %= 60_000

    secs = total_milliseconds // 1000
    milliseconds = total_milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


class MainScene(VoiceoverScene):
    def setup(self):
        super().setup()

        self.set_speech_service(GTTSService(lang="en", tld="com"))

        self.BLUE = "#58C4DD"
        self.GREEN = "#83C167"
        self.YELLOW = "#FFFF66"
        self.ORANGE = "#FFB86C"
        self.RED = "#FF6B6B"
        self.PURPLE = "#9B5DE5"
        self.WHITE = "#F7F7F2"

        self.current_caption = None
        self.keep = []
        self.title_group = None
        self.title_mode = "hero"

        self.subtitle_entries = []
        self.subtitle_index = 1

    # ------------------------------------------------------------
    # General helpers
    # ------------------------------------------------------------

    def T(self, text, size=28, color=None, weight="NORMAL", line_spacing=0.9):
        mob = Text(
            str(text),
            font_size=size,
            color=color or self.WHITE,
            weight=weight,
            line_spacing=line_spacing,
        )
        mob.set_z_index(70)
        return mob

    def M(self, tex, size=42, color=None):
        mob = MathTex(tex, font_size=size, color=color or self.WHITE)
        mob.set_z_index(70)
        return mob

    def subtle_background(self):
        plane = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-4.5, 4.5, 1],
            axis_config={
                "stroke_color": "#C9D6E8",
                "stroke_width": 1.2,
                "stroke_opacity": 0.22,
                "include_ticks": False,
            },
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1.0,
                "stroke_opacity": 0.09,
            },
            faded_line_ratio=2,
        )
        plane.set_z_index(-100)
        return plane

    def formula_box(self, tex, size=40, stroke=None, color=None, max_width=10.8):
        stroke = stroke or self.YELLOW
        formula = self.M(tex, size=size, color=color or self.WHITE)

        if formula.width > max_width:
            formula.scale(max_width / formula.width)

        bg = BackgroundRectangle(
            formula,
            color=BLACK,
            fill_opacity=0.24,
            buff=0.20,
        )

        frame = SurroundingRectangle(
            bg,
            buff=0.035,
            color=stroke,
            corner_radius=0.10,
        )
        frame.set_stroke(stroke, width=2.2)

        group = VGroup(bg, frame, formula)
        group.set_z_index(55)
        return group

    def label_box(self, text, size=24, stroke=None, color=None, max_width=8.5):
        stroke = stroke or self.YELLOW
        label = self.T(text, size=size, color=color or self.WHITE)

        if label.width > max_width:
            label.scale(max_width / label.width)

        bg = BackgroundRectangle(
            label,
            color=BLACK,
            fill_opacity=0.28,
            buff=0.18,
        )

        frame = SurroundingRectangle(
            bg,
            buff=0.03,
            color=stroke,
            corner_radius=0.10,
        )
        frame.set_stroke(stroke, width=2.0)

        group = VGroup(bg, frame, label)
        group.set_z_index(60)
        return group

    def glow(self, mob, color=None, buff=0.12):
        color = color or self.YELLOW
        g = SurroundingRectangle(
            mob,
            color=color,
            buff=buff,
            corner_radius=0.10,
        )
        g.set_stroke(color, width=4)
        g.set_z_index(90)
        return g

    def tile_square(self, side, color, opacity=0.92):
        sq = Square(side_length=side)
        sq.set_fill(color, opacity=opacity)
        sq.set_stroke(self.WHITE, width=2.4)
        sq.set_z_index(30)
        return sq

    # ------------------------------------------------------------
    # Captions, voiceover, and SRT subtitles
    # ------------------------------------------------------------

    def add_subtitle(self, text, start_time, end_time):
        self.subtitle_entries.append(
            f"{self.subtitle_index}\n"
            f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
            f"{text}\n"
        )
        self.subtitle_index += 1

    def write_subtitles(self):
        SUBTITLE_FILE.write_text("\n".join(self.subtitle_entries), encoding="utf-8")

    def make_caption(self, text):
        wrapped = "\n".join(
            textwrap.wrap(
                str(text),
                width=52,
                break_long_words=False,
                replace_whitespace=False,
            )[:2]
        )

        band = Rectangle(width=12.2, height=0.82)
        band.to_edge(DOWN, buff=0)
        band.set_fill(BLACK, opacity=0.76)
        band.set_stroke(width=0)
        band.set_z_index(95)

        label = self.T(
            wrapped,
            size=24,
            color=self.WHITE,
            line_spacing=0.88,
        )
        label.move_to(band.get_center() + UP * 0.01)
        label.set_z_index(100)

        return VGroup(band, label)

    def transition_caption(self, text):
        new_caption = self.make_caption(text)

        if self.current_caption is None:
            self.add(new_caption)
        else:
            old = self.current_caption
            self.play(
                FadeOut(old, shift=DOWN * 0.03),
                FadeIn(new_caption, shift=UP * 0.03),
                run_time=0.18,
                rate_func=linear,
            )

        self.current_caption = new_caption

    def hide_caption(self):
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption), run_time=0.18)
            self.current_caption = None

    def speak(self, narration, *animations, caption=None, min_time=0.0, motion_ratio=0.70):
        if caption is not None:
            self.transition_caption(caption)

        start_time = self.time

        with self.voiceover(text=narration) as tracker:
            total = max(float(tracker.duration), float(min_time))

            if animations:
                motion_time = min(
                    max(0.9, total * motion_ratio),
                    max(0.9, total - 0.12),
                )

                self.play(
                    *animations,
                    run_time=motion_time,
                    rate_func=smooth,
                )

                remaining = total - motion_time
                if remaining > 1 / config.frame_rate:
                    self.wait(remaining)
            else:
                if total > 1 / config.frame_rate:
                    self.wait(total)

        self.add_subtitle(narration, start_time, self.time)

    def clear_stage(self):
        protected = list(self.keep)

        if self.title_group is not None:
            protected.append(self.title_group)

        if self.current_caption is not None:
            protected.append(self.current_caption)

        removable = [m for m in self.mobjects if m not in protected]

        if removable:
            self.play(*[FadeOut(m) for m in removable], run_time=0.55)

    # ------------------------------------------------------------
    # Title
    # ------------------------------------------------------------

    def build_title(self):
        title = self.T(
            "Sum of Natural Numbers",
            size=58,
            color=self.WHITE,
            weight="BOLD",
        )

        subtitle = self.T(
            "staircase proof",
            size=23,
            color=GREY_A,
        )

        group = VGroup(title, subtitle).arrange(DOWN, buff=0.04)
        group.to_edge(UP, buff=0.18)
        group.set_z_index(80)

        self.title_group = group
        self.title_mode = "hero"

        return group

    def compact_title(self):
        if self.title_mode == "compact":
            return

        compact = VGroup(
            self.T("Sum of Natural Numbers", size=26, color=self.WHITE, weight="BOLD"),
            self.T("staircase proof", size=15, color=GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.01)

        compact.to_corner(UL, buff=0.42)
        compact.set_z_index(80)

        self.play(
            Transform(self.title_group, compact),
            run_time=0.65,
            rate_func=smooth,
        )

        self.title_mode = "compact"

    # ------------------------------------------------------------
    # Coordinate grid and tiled staircase
    # ------------------------------------------------------------

    def example_plane(self, n=6, unit=0.72):
        plane = NumberPlane(
            x_range=[0, n + 1, 1],
            y_range=[0, n, 1],
            x_length=(n + 1) * unit,
            y_length=n * unit,
            axis_config={
                "stroke_color": "#D8E2F0",
                "stroke_width": 1.6,
                "stroke_opacity": 0.42,
                "include_ticks": False,
            },
            background_line_style={
                "stroke_color": "#D8E2F0",
                "stroke_width": 1.6,
                "stroke_opacity": 0.42,
            },
            faded_line_ratio=1,
        )

        plane.move_to(LEFT * 2.85 + DOWN * 0.18)
        plane.set_z_index(10)

        frame = Rectangle(
            width=(n + 1) * unit,
            height=n * unit,
        )
        frame.move_to(plane.c2p((n + 1) / 2, n / 2))
        frame.set_fill(opacity=0)
        frame.set_stroke(self.YELLOW, width=4)
        frame.set_z_index(45)

        return plane, frame

    def staircase_data(self, plane, n=6, color=None):
        color = color or self.BLUE

        tiles = VGroup()
        rows = []
        end_labels = VGroup()

        cell_w = abs(plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0])

        for r in range(n):
            row = VGroup()
            for c in range(r + 1):
                sq = self.tile_square(cell_w, color)
                sq.move_to(plane.c2p(c + 0.5, r + 0.5))
                row.add(sq)
                tiles.add(sq)
            rows.append(row)

            lab = self.M(str(r + 1), size=24, color=self.YELLOW)
            lab.move_to(plane.c2p(r + 0.5, r + 0.5))
            end_labels.add(lab)

        return {
            "tiles": tiles,
            "rows": rows,
            "end_labels": end_labels,
            "n": n,
            "cell_w": cell_w,
        }

    def complement_tiles(self, plane, n=6, color=None):
        color = color or self.GREEN

        cell_w = abs(plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0])

        tiles = VGroup()
        for r in range(n):
            for c in range(r + 1, n + 1):
                sq = self.tile_square(cell_w, color)
                sq.move_to(plane.c2p(c + 0.5, r + 0.5))
                tiles.add(sq)

        return tiles

    def full_rectangle_rows(self, plane, n=6):
        rows = []
        left = plane.c2p(0, 0)[0]
        right = plane.c2p(n + 1, 0)[0]
        for r in range(n):
            y_bottom = plane.c2p(0, r)[1]
            y_top = plane.c2p(0, r + 1)[1]
            rect = Rectangle(width=right - left, height=y_top - y_bottom)
            rect.move_to(plane.c2p((n + 1) / 2, r + 0.5))
            rect.set_fill(opacity=0)
            rect.set_stroke(self.YELLOW, width=3)
            rect.set_z_index(85)
            rows.append(rect)
        return rows

    # ------------------------------------------------------------
    # Main
    # ------------------------------------------------------------

    def construct(self):
        bg = self.subtle_background()
        self.add(bg)
        self.keep = [bg]

        title = self.build_title()

        self.play(
            Write(title[0]),
            FadeIn(title[1], shift=UP * 0.06),
            run_time=1.25,
        )

        self.intro_scene()
        self.build_staircase_scene()
        self.complete_rectangle_scene()
        self.numeric_formula_scene()
        self.general_picture_scene()
        self.general_formula_scene()
        self.recap_scene()
        self.outro_scene()

        self.write_subtitles()

    # ------------------------------------------------------------
    # Scenes
    # ------------------------------------------------------------

    def intro_scene(self):
        theorem = self.formula_box(
            r"1+2+3+\cdots+n=\frac{n(n+1)}{2}",
            size=50,
            stroke=self.YELLOW,
        )
        theorem.move_to(UP * 0.75)

        idea1 = self.label_box("build a staircase", size=22, stroke=self.BLUE, max_width=2.8)
        idea2 = self.label_box("make a second copy", size=22, stroke=self.GREEN, max_width=3.3)
        idea3 = self.label_box("form a rectangle", size=22, stroke=self.ORANGE, max_width=3.1)
        idea4 = self.label_box("take half", size=22, stroke=self.PURPLE, max_width=2.4)

        ideas = VGroup(idea1, idea2, idea3, idea4).arrange(RIGHT, buff=0.28)
        ideas.move_to(DOWN * 1.22)

        self.speak(
            "We want to understand the formula for the sum of the first n natural numbers. "
            "Not just memorize it, but really see why it is true.",
            FadeIn(theorem, shift=UP * 0.10),
            caption="Goal: understand the formula visually.",
            min_time=15,
        )

        self.speak(
            "The proof has one central idea. "
            "We build the sum as a staircase, take a second copy, fit both copies into a rectangle, and then take half of the rectangle.",
            FadeIn(ideas, shift=UP * 0.08),
            caption="Plan: staircase → copy → rectangle → half.",
            min_time=18,
        )

        self.speak(
            "That picture will explain where n comes from, where n plus one comes from, and why division by two appears.",
            caption="Every part of the formula will come from the picture.",
            min_time=13,
        )

        self.compact_title()

    def build_staircase_scene(self):
        self.clear_stage()

        plane, frame = self.example_plane(n=6, unit=0.72)
        stair = self.staircase_data(plane, n=6, color=self.BLUE)

        self.plane = plane
        self.frame = frame
        self.stair = stair

        sum_box = self.formula_box(
            r"S=1+2+3+4+5+6",
            size=42,
            stroke=self.BLUE,
            max_width=5.4,
        )
        sum_box.move_to(RIGHT * 3.35 + UP * 1.55)

        note = self.label_box(
            "Each row is one term of the sum",
            size=23,
            stroke=self.YELLOW,
            max_width=4.5,
        )
        note.move_to(RIGHT * 3.30 + UP * 0.55)

        self.speak(
            "Let us start with a concrete example. "
            "Suppose S is one plus two plus three plus four plus five plus six.",
            FadeIn(sum_box, shift=UP * 0.08),
            caption="Example: S = 1 + 2 + 3 + 4 + 5 + 6.",
            min_time=13,
        )

        self.speak(
            "Now place the sum on a grid. "
            "One becomes one square. Two becomes a row of two squares. Three becomes a row of three squares, and so on.",
            FadeIn(plane),
            FadeIn(frame),
            FadeIn(note, shift=UP * 0.06),
            caption="Represent each term as a row of unit squares.",
            min_time=17,
        )

        for i, row in enumerate(stair["rows"]):
            label = stair["end_labels"][i]
            row_box = self.label_box(
                f"row {i + 1} has {i + 1} square{'s' if i + 1 > 1 else ''}",
                size=22,
                stroke=self.YELLOW,
                max_width=4.2,
            )
            row_box.move_to(RIGHT * 3.25 + DOWN * 1.30)

            self.speak(
                f"Row {i + 1} has {i + 1} square{'s' if i + 1 > 1 else ''}.",
                AnimationGroup(
                    *[FadeIn(tile, shift=UP * 0.02) for tile in row],
                    lag_ratio=0.06,
                ),
                FadeIn(label, scale=0.8),
                FadeIn(row_box, shift=UP * 0.04),
                caption=f"Row {i + 1} contributes {i + 1}.",
                min_time=5.0,
                motion_ratio=0.80,
            )
            self.play(FadeOut(row_box), run_time=0.18)

        self.play(FadeOut(note), run_time=0.30)

        area_box = self.formula_box(
            r"\text{area of staircase}=S",
            size=32,
            stroke=self.GREEN,
            max_width=4.8,
        )
        area_box.move_to(RIGHT * 3.35 + DOWN * 1.10)

        self.speak(
            "Together, these rows form a staircase. "
            "The total number of squares in the staircase is exactly the sum S.",
            LaggedStart(
                *[Indicate(row, color=self.YELLOW, scale_factor=1.02) for row in stair["rows"]],
                lag_ratio=0.10,
            ),
            FadeIn(area_box, shift=UP * 0.05),
            caption="The whole staircase represents the sum S.",
            min_time=15,
        )

        self.sum_box = sum_box
        self.area_box = area_box

    def complete_rectangle_scene(self):
        plane = self.plane
        frame = self.frame
        stair = self.stair
        n = stair["n"]

        copy_source = stair["tiles"].copy()
        copy_source.set_fill(self.GREEN, opacity=0.90)
        copy_source.set_stroke(self.WHITE, width=2.4)
        copy_source.shift(RIGHT * 4.05 + UP * 0.95)

        copy_label = self.label_box(
            "A second identical staircase",
            size=22,
            stroke=self.GREEN,
            max_width=4.4,
        )
        copy_label.move_to(RIGHT * 3.35 + UP * 0.55)

        target = self.complement_tiles(plane, n=n, color=self.GREEN)

        self.speak(
            "Now take a second copy of the same staircase. "
            "It has exactly the same area as the blue one.",
            FadeIn(copy_source, shift=LEFT * 0.10),
            FadeIn(copy_label, shift=UP * 0.04),
            caption="Create a second identical copy.",
            min_time=13,
        )

        self.play(FadeOut(copy_label), run_time=0.25)

        fit_label = self.label_box(
            "Fit the copy into the empty spaces",
            size=22,
            stroke=self.ORANGE,
            max_width=4.7,
        )
        fit_label.move_to(RIGHT * 3.35 + UP * 0.55)

        self.speak(
            "Move the second staircase into the missing spaces. "
            "When the pieces fit together, the staircase becomes a rectangle.",
            Transform(copy_source, target),
            FadeIn(fit_label, shift=UP * 0.04),
            caption="Two staircases fit together to make a rectangle.",
            min_time=16,
        )

        self.play(FadeOut(fit_label), run_time=0.25)

        left_brace = Brace(frame, LEFT, color=self.WHITE)
        left_label = self.M(r"6", size=31, color=self.YELLOW)
        left_label.next_to(left_brace, LEFT, buff=0.10)

        bottom_brace = Brace(frame, DOWN, color=self.WHITE)
        bottom_label = self.M(r"7", size=31, color=self.YELLOW)
        bottom_label.next_to(bottom_brace, DOWN, buff=0.10)

        self.speak(
            "Now read the dimensions of the completed rectangle. "
            "Its height is six, because there are six rows. "
            "Its width is seven, because each completed row has seven squares.",
            FadeIn(left_brace),
            FadeIn(left_label),
            FadeIn(bottom_brace),
            FadeIn(bottom_label),
            caption="For this example, the rectangle is 6 by 7.",
            min_time=20,
        )

        row_highlights = self.full_rectangle_rows(plane, n=n)

        row_note = self.label_box(
            "Every row now has width 7",
            size=22,
            stroke=self.YELLOW,
            max_width=4.0,
        )
        row_note.move_to(RIGHT * 3.30 + DOWN * 1.05)

        self.speak(
            "And this is why the width is seven. "
            "Each row is completed to the same full length.",
            FadeIn(row_note, shift=UP * 0.05),
            LaggedStart(*[Create(r) for r in row_highlights], lag_ratio=0.10),
            caption="Each completed row has the same width.",
            min_time=14,
        )

        self.play(
            FadeOut(row_note),
            *[FadeOut(r) for r in row_highlights],
            run_time=0.35,
        )

        self.copy_source = copy_source
        self.left_brace = left_brace
        self.left_label = left_label
        self.bottom_brace = bottom_brace
        self.bottom_label = bottom_label

    def numeric_formula_scene(self):
        self.clear_stage()

        heading = self.T(
            "Turn the picture into arithmetic",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.00)

        f1 = self.formula_box(
            r"S=1+2+3+4+5+6",
            size=42,
            stroke=self.BLUE,
            max_width=6.4,
        )
        f1.move_to(UP * 0.95)

        f2 = self.formula_box(
            r"2S=6\times 7",
            size=42,
            stroke=self.ORANGE,
            max_width=4.8,
        )
        f2.move_to(UP * 0.05)

        f3 = self.formula_box(
            r"S=\frac{6\times 7}{2}",
            size=40,
            stroke=self.GREEN,
            max_width=5.8,
        )
        f3.move_to(DOWN * 0.95)

        f4 = self.formula_box(
            r"S=21",
            size=42,
            stroke=self.YELLOW,
            max_width=3.0,
        )
        f4.move_to(DOWN * 1.95)

        self.speak(
            "Now let the geometry step aside for a moment, and convert the picture into arithmetic.",
            FadeIn(heading, shift=UP * 0.08),
            caption="Now translate the picture into arithmetic.",
            min_time=10,
        )

        self.speak(
            "One staircase is the sum S.",
            FadeIn(f1, shift=UP * 0.06),
            caption="One staircase equals S.",
            min_time=8,
        )

        self.speak(
            "Two identical staircases make one rectangle, so two S equals six times seven.",
            FadeIn(f2, shift=UP * 0.06),
            caption="Two staircases make a 6 by 7 rectangle.",
            min_time=13,
        )

        self.speak(
            "Therefore one staircase is half of six times seven.",
            FadeIn(f3, shift=UP * 0.06),
            caption="One staircase is half of the rectangle.",
            min_time=11,
        )

        self.speak(
            "And that gives S equals twenty one.",
            FadeIn(f4, shift=UP * 0.06),
            caption="So the sum is 21.",
            min_time=9,
        )

    def general_picture_scene(self):
        self.clear_stage()

        plane, frame = self.example_plane(n=6, unit=0.72)

        blue = self.staircase_data(plane, n=6, color=self.BLUE)["tiles"]
        green = self.complement_tiles(plane, n=6, color=self.GREEN)

        left_brace = Brace(frame, LEFT, color=self.WHITE)
        left_label = self.M(r"n", size=31, color=self.YELLOW)
        left_label.next_to(left_brace, LEFT, buff=0.10)

        bottom_brace = Brace(frame, DOWN, color=self.WHITE)
        bottom_label = self.M(r"n+1", size=31, color=self.YELLOW)
        bottom_label.next_to(bottom_brace, DOWN, buff=0.10)

        general_tag = self.label_box(
            "Same picture, but now for any n",
            size=23,
            stroke=self.YELLOW,
            max_width=4.8,
        )
        general_tag.move_to(RIGHT * 3.25 + UP * 1.25)

        self.speak(
            "Now keep the picture, but replace the specific number six with a general number n.",
            FadeIn(plane),
            FadeIn(frame),
            FadeIn(blue),
            FadeIn(green),
            FadeIn(general_tag, shift=UP * 0.05),
            caption="Now generalize the picture.",
            min_time=14,
        )

        self.speak(
            "The height becomes n, because there are n rows.",
            FadeIn(left_brace),
            FadeIn(left_label),
            caption="Height = n.",
            min_time=10,
        )

        self.speak(
            "And the width becomes n plus one, because the completed row is one unit longer than the largest step.",
            FadeIn(bottom_brace),
            FadeIn(bottom_label),
            caption="Width = n + 1.",
            min_time=14,
        )

        self.play(FadeOut(general_tag), run_time=0.25)

        why1 = self.label_box("n = height", size=22, stroke=self.BLUE, max_width=2.6)
        why2 = self.label_box("n+1 = width", size=22, stroke=self.GREEN, max_width=3.0)

        why_group = VGroup(why1, why2).arrange(DOWN, buff=0.22)
        why_group.move_to(RIGHT * 3.25 + UP * 0.25)

        self.speak(
            "So even in the general case, the picture already contains the ingredients of the formula.",
            FadeIn(why_group, shift=LEFT * 0.03),
            caption="The picture already contains n and n+1.",
            min_time=12,
        )

    def general_formula_scene(self):
        self.clear_stage()

        heading = self.T(
            "Now write the general formula",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.0)

        g1 = self.formula_box(
            r"2S=n(n+1)",
            size=44,
            stroke=self.ORANGE,
            max_width=5.4,
        )
        g1.move_to(UP * 0.70)

        g2 = self.formula_box(
            r"S=\frac{n(n+1)}{2}",
            size=46,
            stroke=self.YELLOW,
            max_width=6.2,
        )
        g2.move_to(DOWN * 0.65)

        cards = VGroup(
            self.label_box("n = the height", size=22, stroke=self.BLUE, max_width=3.0),
            self.label_box("n+1 = the width", size=22, stroke=self.GREEN, max_width=3.3),
            self.label_box("divide by 2 = one staircase", size=22, stroke=self.PURPLE, max_width=4.5),
        ).arrange(DOWN, buff=0.24)
        cards.move_to(DOWN * 2.05)

        self.speak(
            "Two staircases together fill the rectangle. "
            "So the area of the full rectangle is two S, and it is also n times n plus one.",
            FadeIn(heading, shift=UP * 0.06),
            FadeIn(g1, shift=UP * 0.08),
            caption="Two staircases give 2S = n(n+1).",
            min_time=16,
        )

        self.speak(
            "Now divide by two, because we only want one staircase, not both of them.",
            FadeIn(g2, shift=UP * 0.08),
            caption="One staircase gives S = n(n+1)/2.",
            min_time=12,
        )

        self.speak(
            "And now every piece has a meaning. "
            "n comes from the height, n plus one comes from the width, and division by two comes from taking one of the two equal copies.",
            FadeIn(cards, shift=UP * 0.06),
            caption="Every part of the formula now has a clear reason.",
            min_time=19,
        )

    def recap_scene(self):
        self.clear_stage()

        heading = self.T(
            "Recap",
            size=35,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.05)

        self.speak(
            "Let us summarize the proof in one clean chain.",
            FadeIn(heading, shift=UP * 0.06),
            caption="Recap of the whole proof.",
            min_time=8,
        )

        chain = [
            (
                r"S=1+2+3+\cdots+n",
                "Start with the sum.",
                "Start with the sum.",
            ),
            (
                r"\text{Draw it as a staircase}",
                "Draw the numbers as a staircase made of unit squares.",
                "Draw a staircase.",
            ),
            (
                r"\text{Make a second identical staircase}",
                "Make one more identical copy.",
                "Duplicate the staircase.",
            ),
            (
                r"\text{The two copies form an } n\times(n+1)\text{ rectangle}",
                "The two copies fit together to form a rectangle of height n and width n plus one.",
                "Two copies form a rectangle.",
            ),
            (
                r"2S=n(n+1)",
                "So two S equals the rectangle area.",
                "Two staircases give 2S.",
            ),
            (
                r"S=\frac{n(n+1)}{2}",
                "And one S is half of that rectangle.",
                "One staircase gives the final formula.",
            ),
        ]

        current = None

        for tex, narration, cap in chain:
            box = self.formula_box(
                tex,
                size=33,
                stroke=self.YELLOW,
                max_width=10.2,
            )
            box.move_to(DOWN * 0.10)

            if current is None:
                self.speak(
                    narration,
                    FadeIn(box, shift=UP * 0.06),
                    caption=cap,
                    min_time=9,
                )
            else:
                self.speak(
                    narration,
                    FadeOut(current),
                    FadeIn(box, shift=UP * 0.06),
                    caption=cap,
                    min_time=10,
                )
            current = box

        final_note = self.label_box(
            "A formula becomes easy to remember when it has a picture.",
            size=24,
            stroke=self.GREEN,
            max_width=6.8,
        )
        final_note.move_to(DOWN * 1.85)

        self.speak(
            "This is why the formula is memorable. "
            "It is not just a string of symbols. It comes from a simple picture.",
            FadeIn(final_note, shift=UP * 0.06),
            caption="The formula is remembered through the picture.",
            min_time=14,
        )

    def outro_scene(self):
        self.clear_stage()
        self.hide_caption()

        final = self.formula_box(
            r"1+2+3+\cdots+n=\frac{n(n+1)}{2}",
            size=52,
            stroke=self.YELLOW,
        )
        final.move_to(UP * 0.45)

        message = self.T(
            "A staircase became a rectangle.\nThe rectangle gave the formula.",
            size=34,
            color=self.WHITE,
            weight="BOLD",
            line_spacing=0.92,
        )
        message.next_to(final, DOWN, buff=0.65)

        self.speak(
            "A staircase became a rectangle. The rectangle gave the formula.",
            FadeIn(final, scale=0.96),
            FadeIn(message, shift=UP * 0.08),
            min_time=12,
        )

        self.wait(2)
