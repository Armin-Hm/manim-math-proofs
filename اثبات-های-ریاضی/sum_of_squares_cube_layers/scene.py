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

        # Same voiceover engine as the original file. Replace this service if you
        # use a higher-quality local or cloud voice.
        self.set_speech_service(GTTSService(lang="en", tld="com"))

        self.BLUE = "#58C4DD"
        self.GREEN = "#83C167"
        self.YELLOW = "#FFFF66"
        self.ORANGE = "#FFB86C"
        self.RED = "#FF6B6B"
        self.PURPLE = "#9B5DE5"
        self.CYAN = "#7DD3FC"
        self.WHITE = "#F7F7F2"
        self.MUTED = "#9CA3AF"

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

    def tile_square(self, side, color, opacity=0.92):
        sq = Square(side_length=side)
        sq.set_fill(color, opacity=opacity)
        sq.set_stroke(self.WHITE, width=1.5)
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
            "Sum of Squares",
            size=58,
            color=self.WHITE,
            weight="BOLD",
        )

        subtitle = self.T(
            "cube-layer proof",
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
            self.T("Sum of Squares", size=26, color=self.WHITE, weight="BOLD"),
            self.T("cube-layer proof", size=15, color=GREY_A),
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
    # Visual helpers for square layers and simple cube diagrams
    # ------------------------------------------------------------

    def square_layer_grid(self, k, unit=0.22, color=None):
        color = color or self.BLUE
        cells = VGroup()
        for r in range(k):
            for c in range(k):
                sq = self.tile_square(unit, color, opacity=0.88)
                sq.move_to(RIGHT * (c * unit) + DOWN * (r * unit))
                cells.add(sq)
        cells.move_to(ORIGIN)
        return cells

    def layer_card(self, k, unit=0.22, color=None):
        grid = self.square_layer_grid(k, unit=unit, color=color or self.BLUE)
        formula = self.M(f"{k}^2", size=31, color=self.YELLOW)
        formula.next_to(grid, DOWN, buff=0.18)
        card = VGroup(grid, formula)
        card.set_z_index(30)
        return card

    def iso_point(self, x, y, z, origin=ORIGIN, scale=1.0):
        return np.array(origin) + RIGHT * ((x - y) * 0.70 * scale) + UP * ((x + y) * 0.36 * scale + z * 0.78 * scale)

    def iso_cube(self, origin=ORIGIN, scale=1.0, colors=None, opacity=0.90, stroke_width=2.0):
        colors = colors or {
            "top": self.YELLOW,
            "left": self.BLUE,
            "right": self.GREEN,
        }

        p000 = self.iso_point(0, 0, 0, origin, scale)
        p100 = self.iso_point(1, 0, 0, origin, scale)
        p010 = self.iso_point(0, 1, 0, origin, scale)
        p110 = self.iso_point(1, 1, 0, origin, scale)
        p001 = self.iso_point(0, 0, 1, origin, scale)
        p101 = self.iso_point(1, 0, 1, origin, scale)
        p011 = self.iso_point(0, 1, 1, origin, scale)
        p111 = self.iso_point(1, 1, 1, origin, scale)

        left_face = Polygon(p000, p010, p011, p001)
        right_face = Polygon(p000, p100, p101, p001)
        top_face = Polygon(p001, p101, p111, p011)

        left_face.set_fill(colors["left"], opacity=opacity * 0.78)
        right_face.set_fill(colors["right"], opacity=opacity * 0.83)
        top_face.set_fill(colors["top"], opacity=opacity)

        for face in (left_face, right_face, top_face):
            face.set_stroke(self.WHITE, width=stroke_width, opacity=0.92)
            face.set_z_index(35)

        return VGroup(left_face, right_face, top_face)

    def simple_big_cube(self, side_label="k", center=ORIGIN, size=2.25):
        cube = self.iso_cube(origin=ORIGIN, scale=size)
        cube.move_to(center)

        label = self.M(side_label + "^3", size=42, color=self.WHITE)
        label.move_to(cube.get_center())
        label.set_z_index(80)

        return VGroup(cube, label)

    def layer_parts(self):
        # An exploded view of the new shell: 3 square faces, 3 edge strips, 1 corner cube.
        squares = VGroup()
        for label, col in [(r"k^2", self.BLUE), (r"k^2", self.GREEN), (r"k^2", self.ORANGE)]:
            sq = Square(side_length=0.96)
            sq.set_fill(col, opacity=0.86)
            sq.set_stroke(self.WHITE, width=1.8)
            tx = self.M(label, size=30, color=self.WHITE)
            tx.move_to(sq.get_center())
            squares.add(VGroup(sq, tx))
        squares.arrange(RIGHT, buff=0.22)

        strips = VGroup()
        for col in [self.PURPLE, self.RED, self.CYAN]:
            rect = RoundedRectangle(width=1.12, height=0.32, corner_radius=0.06)
            rect.set_fill(col, opacity=0.84)
            rect.set_stroke(self.WHITE, width=1.5)
            tx = self.M(r"k", size=25, color=self.WHITE)
            tx.move_to(rect.get_center())
            strips.add(VGroup(rect, tx))
        strips.arrange(RIGHT, buff=0.22)

        corner = self.iso_cube(scale=0.42, opacity=0.95)
        one = self.M(r"1", size=24, color=self.WHITE)
        one.move_to(corner.get_center() + DOWN * 0.03)
        corner_piece = VGroup(corner, one)

        top = VGroup(squares).arrange(RIGHT)
        bottom = VGroup(strips, corner_piece).arrange(RIGHT, buff=0.35)
        parts = VGroup(top, bottom).arrange(DOWN, buff=0.36)
        parts.set_z_index(40)
        return parts

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
        self.square_layers_scene()
        self.cube_growth_scene()
        self.telescope_scene()
        self.solve_scene()
        self.recap_scene()
        self.outro_scene()

        self.write_subtitles()

    # ------------------------------------------------------------
    # Scenes
    # ------------------------------------------------------------

    def intro_scene(self):
        theorem = self.formula_box(
            r"1^2+2^2+3^2+\cdots+n^2=\frac{n(n+1)(2n+1)}{6}",
            size=43,
            stroke=self.YELLOW,
            max_width=11.0,
        )
        theorem.move_to(UP * 0.72)

        idea1 = self.label_box("square layers", size=22, stroke=self.BLUE, max_width=2.8)
        idea2 = self.label_box("grow a cube", size=22, stroke=self.GREEN, max_width=2.7)
        idea3 = self.label_box("new shell = 3k² + 3k + 1", size=22, stroke=self.ORANGE, max_width=4.7)
        idea4 = self.label_box("add and solve", size=22, stroke=self.PURPLE, max_width=3.1)

        ideas = VGroup(idea1, idea2, idea3, idea4).arrange(RIGHT, buff=0.24)
        ideas.move_to(DOWN * 1.25)

        self.speak(
            "Now we want to prove the formula for the sum of the first n squares. "
            "The picture will be three dimensional: square layers made from little cubes.",
            FadeIn(theorem, shift=UP * 0.10),
            caption="Goal: prove the sum of squares formula visually.",
            min_time=16,
        )

        self.speak(
            "The key move is not to memorize the formula. "
            "We will grow a cube by one unit, count the new shell, add all those shells, and solve for the square terms.",
            FadeIn(ideas, shift=UP * 0.08),
            caption="Plan: layers → cube growth → telescoping → formula.",
            min_time=19,
        )

        self.compact_title()

    def square_layers_scene(self):
        self.clear_stage()

        heading = self.T(
            "Each term is a square layer",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.02)

        cards = VGroup(
            self.layer_card(1, unit=0.33, color=self.BLUE),
            self.layer_card(2, unit=0.27, color=self.GREEN),
            self.layer_card(3, unit=0.23, color=self.ORANGE),
            self.layer_card(4, unit=0.205, color=self.PURPLE),
        ).arrange(RIGHT, buff=0.52)
        cards.move_to(LEFT * 2.20 + DOWN * 0.15)

        dots = self.M(r"\cdots", size=46, color=self.WHITE)
        dots.next_to(cards, RIGHT, buff=0.38)

        stack_note = self.label_box(
            "Stacking these layers creates a square pyramid of cubes",
            size=23,
            stroke=self.YELLOW,
            max_width=4.8,
        )
        stack_note.move_to(RIGHT * 3.18 + UP * 0.58)

        sum_box = self.formula_box(
            r"S=1^2+2^2+3^2+\cdots+n^2",
            size=37,
            stroke=self.BLUE,
            max_width=5.8,
        )
        sum_box.move_to(RIGHT * 3.18 + DOWN * 1.02)

        self.speak(
            "A square number is an area. "
            "One squared is a one by one layer. Two squared is a two by two layer. Three squared is a three by three layer, and so on.",
            FadeIn(heading, shift=UP * 0.06),
            LaggedStart(*[FadeIn(card, shift=UP * 0.05) for card in cards], lag_ratio=0.18),
            FadeIn(dots, shift=UP * 0.05),
            caption="Each k² is a k by k square layer.",
            min_time=20,
        )

        self.speak(
            "If we stack all these square layers, the total number of little cubes is exactly S, the sum we want.",
            FadeIn(stack_note, shift=LEFT * 0.05),
            FadeIn(sum_box, shift=UP * 0.06),
            caption="The stacked layers represent S.",
            min_time=14,
        )

    def cube_growth_scene(self):
        self.clear_stage()

        heading = self.T(
            "Grow a cube by one unit",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.05)

        cube_k = self.simple_big_cube(side_label="k", center=LEFT * 3.35 + DOWN * 0.12, size=1.18)

        arrow = Arrow(LEFT * 1.55 + DOWN * 0.12, RIGHT * 0.15 + DOWN * 0.12, buff=0.10)
        arrow.set_color(self.WHITE)
        arrow.set_z_index(50)

        cube_next = self.simple_big_cube(side_label="k+1", center=RIGHT * 1.70 + DOWN * 0.12, size=1.36)

        growth_formula = self.formula_box(
            r"(k+1)^3-k^3=\text{new shell}",
            size=35,
            stroke=self.GREEN,
            max_width=7.0,
        )
        growth_formula.move_to(DOWN * 2.08)

        self.speak(
            "Look at a cube with side length k. "
            "Now grow it to a cube with side length k plus one. The difference between the two cubes is the new outer shell.",
            FadeIn(heading, shift=UP * 0.06),
            FadeIn(cube_k, shift=RIGHT * 0.05),
            GrowArrow(arrow),
            FadeIn(cube_next, shift=LEFT * 0.05),
            FadeIn(growth_formula, shift=UP * 0.05),
            caption="The added shell equals (k+1)³ − k³.",
            min_time=21,
        )

        self.clear_stage()

        heading2 = self.T(
            "Count the new shell",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading2.move_to(UP * 2.05)

        parts = self.layer_parts()
        parts.move_to(LEFT * 2.15 + DOWN * 0.12)

        part_labels = VGroup(
            self.label_box("3 square faces", size=22, stroke=self.BLUE, max_width=3.4),
            self.label_box("3 edge strips", size=22, stroke=self.PURPLE, max_width=3.2),
            self.label_box("1 corner cube", size=22, stroke=self.GREEN, max_width=3.2),
        ).arrange(DOWN, buff=0.23)
        part_labels.move_to(RIGHT * 3.25 + UP * 0.65)

        shell_formula = self.formula_box(
            r"\text{new shell}=3k^2+3k+1",
            size=38,
            stroke=self.ORANGE,
            max_width=6.8,
        )
        shell_formula.move_to(RIGHT * 3.25 + DOWN * 1.15)

        self.speak(
            "Now count that shell. "
            "It consists of three square faces of size k squared, three edge strips of length k, and one corner cube.",
            FadeIn(heading2, shift=UP * 0.06),
            FadeIn(parts, shift=UP * 0.08),
            FadeIn(part_labels, shift=LEFT * 0.05),
            caption="The new shell breaks into 3k², 3k, and 1.",
            min_time=20,
        )

        self.speak(
            "So the cube identity becomes: k plus one cubed minus k cubed equals three k squared, plus three k, plus one.",
            FadeIn(shell_formula, shift=UP * 0.06),
            caption="(k+1)³ − k³ = 3k² + 3k + 1.",
            min_time=16,
        )

    def telescope_scene(self):
        self.clear_stage()

        heading = self.T(
            "Add the identities",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.05)

        chain = VGroup(
            self.formula_box(r"2^3-1^3=3\cdot1^2+3\cdot1+1", size=30, stroke=self.BLUE, max_width=8.6),
            self.formula_box(r"3^3-2^3=3\cdot2^2+3\cdot2+1", size=30, stroke=self.GREEN, max_width=8.6),
            self.formula_box(r"4^3-3^3=3\cdot3^2+3\cdot3+1", size=30, stroke=self.ORANGE, max_width=8.6),
            self.formula_box(r"\vdots", size=34, stroke=self.WHITE, max_width=2.0),
            self.formula_box(r"(n+1)^3-n^3=3n^2+3n+1", size=30, stroke=self.PURPLE, max_width=8.6),
        ).arrange(DOWN, buff=0.17)
        chain.move_to(DOWN * 0.18)

        self.speak(
            "Now write the same cube-growth identity for k equals one, then k equals two, then k equals three, all the way to n.",
            FadeIn(heading, shift=UP * 0.06),
            LaggedStart(*[FadeIn(row, shift=UP * 0.04) for row in chain], lag_ratio=0.12),
            caption="Use the shell identity for k = 1, 2, 3, ..., n.",
            min_time=18,
        )

        self.clear_stage()

        heading2 = self.T(
            "The left side telescopes",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading2.move_to(UP * 2.05)

        left = self.formula_box(
            r"(2^3-1^3)+(3^3-2^3)+\cdots+((n+1)^3-n^3)",
            size=31,
            stroke=self.BLUE,
            max_width=10.2,
        )
        left.move_to(UP * 0.95)

        cancel = self.formula_box(
            r"=\ (n+1)^3-1",
            size=40,
            stroke=self.GREEN,
            max_width=5.0,
        )
        cancel.move_to(UP * 0.03)

        right = self.formula_box(
            r"=\ 3(1^2+2^2+\cdots+n^2)+3(1+2+\cdots+n)+n",
            size=30,
            stroke=self.ORANGE,
            max_width=10.4,
        )
        right.move_to(DOWN * 1.10)

        self.speak(
            "When we add the left sides, almost everything cancels. "
            "That is called telescoping. We are left with n plus one cubed minus one.",
            FadeIn(heading2, shift=UP * 0.06),
            FadeIn(left, shift=UP * 0.05),
            FadeIn(cancel, shift=UP * 0.05),
            caption="The left side collapses to (n+1)³ − 1.",
            min_time=18,
        )

        self.speak(
            "The right sides collect into three times the sum of squares, plus three times the sum of natural numbers, plus n ones.",
            FadeIn(right, shift=UP * 0.05),
            caption="The right side contains the sum of squares we want.",
            min_time=18,
        )

    def solve_scene(self):
        self.clear_stage()

        heading = self.T(
            "Solve for the square sum",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading.move_to(UP * 2.05)

        eq1 = self.formula_box(
            r"(n+1)^3-1=3S+3\frac{n(n+1)}{2}+n",
            size=36,
            stroke=self.BLUE,
            max_width=9.2,
        )
        eq1.move_to(UP * 0.85)

        note = self.label_box(
            "Use the previous result: 1+2+...+n = n(n+1)/2",
            size=22,
            stroke=self.GREEN,
            max_width=7.2,
        )
        note.move_to(DOWN * 0.03)

        eq2 = self.formula_box(
            r"3S=(n+1)^3-1-\frac{3n(n+1)}{2}-n",
            size=34,
            stroke=self.ORANGE,
            max_width=9.6,
        )
        eq2.move_to(DOWN * 0.95)

        self.speak(
            "Let S be the sum of squares. "
            "Now use the natural-number sum from the previous staircase proof: one plus two plus up to n equals n times n plus one over two.",
            FadeIn(heading, shift=UP * 0.06),
            FadeIn(eq1, shift=UP * 0.05),
            FadeIn(note, shift=UP * 0.05),
            caption="Substitute the known formula for 1 + 2 + ... + n.",
            min_time=20,
        )

        self.speak(
            "Then move the extra terms to the other side. "
            "What remains is three times S.",
            FadeIn(eq2, shift=UP * 0.05),
            caption="Isolate 3S.",
            min_time=13,
        )

        self.clear_stage()

        heading2 = self.T(
            "Simplify",
            size=34,
            color=self.YELLOW,
            weight="BOLD",
        )
        heading2.move_to(UP * 2.05)

        s1 = self.formula_box(
            r"3S=\frac{n(n+1)(2n+1)}{2}",
            size=42,
            stroke=self.GREEN,
            max_width=7.6,
        )
        s1.move_to(UP * 0.55)

        s2 = self.formula_box(
            r"S=\frac{n(n+1)(2n+1)}{6}",
            size=48,
            stroke=self.YELLOW,
            max_width=7.8,
        )
        s2.move_to(DOWN * 0.78)

        final_label = self.label_box(
            "This is the formula for 1² + 2² + ... + n²",
            size=24,
            stroke=self.PURPLE,
            max_width=6.6,
        )
        final_label.move_to(DOWN * 2.05)

        self.speak(
            "After simplification, three S equals n times n plus one times two n plus one, all over two.",
            FadeIn(heading2, shift=UP * 0.06),
            FadeIn(s1, shift=UP * 0.05),
            caption="After simplification: 3S = n(n+1)(2n+1)/2.",
            min_time=15,
        )

        self.speak(
            "Finally divide by three. "
            "The denominator becomes six, and we get the sum of squares formula.",
            FadeIn(s2, shift=UP * 0.06),
            FadeIn(final_label, shift=UP * 0.05),
            caption="Therefore S = n(n+1)(2n+1)/6.",
            min_time=16,
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
                r"S=1^2+2^2+\cdots+n^2",
                "Start with the sum of square layers.",
                "Start with the square-layer sum.",
            ),
            (
                r"(k+1)^3-k^3=3k^2+3k+1",
                "Growing a cube by one unit creates three square faces, three edge strips, and one corner cube.",
                "A cube shell gives 3k² + 3k + 1.",
            ),
            (
                r"(n+1)^3-1=3S+3(1+2+\cdots+n)+n",
                "Add the identities from k equals one to n. The left side telescopes.",
                "Adding all shells makes the left side telescope.",
            ),
            (
                r"1+2+\cdots+n=\frac{n(n+1)}{2}",
                "Use the already proven natural-number sum.",
                "Use the staircase formula from the previous video.",
            ),
            (
                r"S=\frac{n(n+1)(2n+1)}{6}",
                "Then solve for S.",
                "Solve for the final formula.",
            ),
        ]

        current = None

        for tex, narration, cap in chain:
            box = self.formula_box(
                tex,
                size=32,
                stroke=self.YELLOW,
                max_width=10.2,
            )
            box.move_to(DOWN * 0.12)

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
                    min_time=12,
                )
            current = box

        final_note = self.label_box(
            "The square formula comes from counting cube layers.",
            size=24,
            stroke=self.GREEN,
            max_width=6.2,
        )
        final_note.move_to(DOWN * 1.86)

        self.speak(
            "So the formula is not magic. "
            "It appears because every cube shell contains square layers, edge strips, and one corner cube.",
            FadeIn(final_note, shift=UP * 0.06),
            caption="Cube layers explain the sum of squares.",
            min_time=16,
        )

    def outro_scene(self):
        self.clear_stage()
        self.hide_caption()

        final = self.formula_box(
            r"1^2+2^2+\cdots+n^2=\frac{n(n+1)(2n+1)}{6}",
            size=48,
            stroke=self.YELLOW,
            max_width=11.0,
        )
        final.move_to(UP * 0.48)

        message = self.T(
            "Square layers grew into a cube.\nThe cube shell revealed the formula.",
            size=33,
            color=self.WHITE,
            weight="BOLD",
            line_spacing=0.92,
        )
        message.next_to(final, DOWN, buff=0.62)

        self.speak(
            "Square layers grew into a cube. The cube shell revealed the formula.",
            FadeIn(final, scale=0.96),
            FadeIn(message, shift=UP * 0.08),
            min_time=12,
        )

        self.wait(2)
