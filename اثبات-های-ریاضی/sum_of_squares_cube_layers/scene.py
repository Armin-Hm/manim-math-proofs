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
        self.YELLOW = "#FFF176"
        self.ORANGE = "#FFB86C"
        self.RED = "#FF6B6B"
        self.PURPLE = "#9B5DE5"
        self.CYAN = "#7DD3FC"
        self.WHITE = "#F7F7F2"
        self.MUTED = "#AAB6C5"

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

        bg = BackgroundRectangle(formula, color=BLACK, fill_opacity=0.24, buff=0.20)
        frame = SurroundingRectangle(bg, buff=0.035, color=stroke, corner_radius=0.10)
        frame.set_stroke(stroke, width=2.2)
        group = VGroup(bg, frame, formula)
        group.set_z_index(55)
        return group

    def label_box(self, text, size=24, stroke=None, color=None, max_width=8.5):
        stroke = stroke or self.YELLOW
        label = self.T(text, size=size, color=color or self.WHITE)
        if label.width > max_width:
            label.scale(max_width / label.width)

        bg = BackgroundRectangle(label, color=BLACK, fill_opacity=0.28, buff=0.18)
        frame = SurroundingRectangle(bg, buff=0.03, color=stroke, corner_radius=0.10)
        frame.set_stroke(stroke, width=2.0)
        group = VGroup(bg, frame, label)
        group.set_z_index(60)
        return group

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

        label = self.T(wrapped, size=24, color=self.WHITE, line_spacing=0.88)
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
                motion_time = min(max(0.9, total * motion_ratio), max(0.9, total - 0.12))
                self.play(*animations, run_time=motion_time, rate_func=smooth)
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
        title = self.T("Sum of Squares", size=58, color=self.WHITE, weight="BOLD")
        subtitle = self.T("cube-layer proof", size=23, color=GREY_A)
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
        self.play(Transform(self.title_group, compact), run_time=0.65, rate_func=smooth)
        self.title_mode = "compact"

    # ------------------------------------------------------------
    # 2D square-layer helpers
    # ------------------------------------------------------------

    def tile_square(self, side, color, opacity=0.92):
        sq = Square(side_length=side)
        sq.set_fill(color, opacity=opacity)
        sq.set_stroke(self.WHITE, width=1.4)
        sq.set_z_index(30)
        return sq

    def square_layer_grid(self, k, unit=0.24, color=None):
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
        formula = self.M(f"{k}^2", size=30, color=self.YELLOW)
        formula.next_to(grid, DOWN, buff=0.16)
        return VGroup(grid, formula)

    # ------------------------------------------------------------
    # Isometric cube helpers
    # ------------------------------------------------------------

    def iso_point(self, x, y, z, origin=ORIGIN, scale=1.0):
        return np.array(origin) + RIGHT * ((x - y) * 0.62 * scale) + UP * ((x + y) * 0.32 * scale + z * 0.78 * scale)

    def iso_unit_cube(self, i, j, k, origin=ORIGIN, scale=0.36, colors=None, opacity=0.96, stroke_width=1.2):
        colors = colors or {
            "top": self.YELLOW,
            "left": self.BLUE,
            "right": self.GREEN,
        }

        p000 = self.iso_point(i, j, k, origin, scale)
        p100 = self.iso_point(i + 1, j, k, origin, scale)
        p010 = self.iso_point(i, j + 1, k, origin, scale)
        p001 = self.iso_point(i, j, k + 1, origin, scale)
        p101 = self.iso_point(i + 1, j, k + 1, origin, scale)
        p011 = self.iso_point(i, j + 1, k + 1, origin, scale)
        p111 = self.iso_point(i + 1, j + 1, k + 1, origin, scale)

        left_face = Polygon(p000, p010, p011, p001)
        right_face = Polygon(p000, p100, p101, p001)
        top_face = Polygon(p001, p101, p111, p011)

        left_face.set_fill(colors["left"], opacity=opacity * 0.78)
        right_face.set_fill(colors["right"], opacity=opacity * 0.85)
        top_face.set_fill(colors["top"], opacity=opacity)

        z = 25 + i + j + k
        for face in (left_face, right_face, top_face):
            face.set_stroke(self.WHITE, width=stroke_width, opacity=0.9)
            face.set_z_index(z)

        return VGroup(left_face, right_face, top_face)

    def cube_group(self, positions, origin=ORIGIN, scale=0.36, colors=None):
        cubes = VGroup()
        positions = sorted(list(positions), key=lambda t: (t[0] + t[1] + t[2], t[2], t[1], t[0]))
        for i, j, k in positions:
            cubes.add(self.iso_unit_cube(i, j, k, origin=origin, scale=scale, colors=colors))
        return cubes

    def palette(self, base):
        if base == "blue":
            return {"top": self.CYAN, "left": self.BLUE, "right": self.GREEN}
        if base == "orange":
            return {"top": self.ORANGE, "left": "#E67E22", "right": "#F39C12"}
        if base == "purple":
            return {"top": self.PURPLE, "left": "#7E57C2", "right": "#AB47BC"}
        if base == "red":
            return {"top": self.RED, "left": "#D35454", "right": "#E57373"}
        return {"top": self.YELLOW, "left": self.BLUE, "right": self.GREEN}

    def square_pyramid_positions(self, n):
        positions = []
        for z in range(n):
            side = n - z
            for x in range(side):
                for y in range(side):
                    positions.append((x, y, z))
        return positions

    def brace_label_pair(self, text, color, width=3.5):
        box = self.label_box(text, size=22, stroke=color, max_width=width)
        return box

    # ------------------------------------------------------------
    # Main
    # ------------------------------------------------------------

    def construct(self):
        bg = self.subtle_background()
        self.add(bg)
        self.keep = [bg]

        title = self.build_title()
        self.play(Write(title[0]), FadeIn(title[1], shift=UP * 0.06), run_time=1.25)

        self.intro_scene()
        self.layers_to_pyramid_scene()
        self.detailed_cube_growth_scene()
        self.general_identity_scene()
        self.telescoping_scene()
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
        theorem.move_to(UP * 0.78)

        ideas = VGroup(
            self.label_box("square layers", size=22, stroke=self.BLUE, max_width=2.8),
            self.label_box("grow a cube", size=22, stroke=self.GREEN, max_width=2.7),
            self.label_box("count the shell carefully", size=22, stroke=self.ORANGE, max_width=4.4),
            self.label_box("add and simplify", size=22, stroke=self.PURPLE, max_width=3.4),
        ).arrange(RIGHT, buff=0.22)
        ideas.move_to(DOWN * 1.24)

        self.speak(
            "This time we want the formula for the sum of squares. "
            "And this proof really deserves a strong visual explanation, because the expression looks more complicated than the sum of natural numbers.",
            FadeIn(theorem, shift=UP * 0.08),
            caption="Goal: prove the sum of squares formula visually.",
            min_time=18,
        )

        self.speak(
            "Our plan has four stages. "
            "First, think of each k squared as a square layer. Then grow a cube from side k to side k plus one. Then count every new piece in the outer shell. Finally, add those identities and solve.",
            FadeIn(ideas, shift=UP * 0.05),
            caption="Plan: layers → cube growth → shell count → formula.",
            min_time=23,
        )

        self.compact_title()

    def layers_to_pyramid_scene(self):
        self.clear_stage()

        heading = self.T("From square layers to a stack of cubes", size=34, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.02)

        cards = VGroup(
            self.layer_card(1, unit=0.33, color=self.BLUE),
            self.layer_card(2, unit=0.27, color=self.GREEN),
            self.layer_card(3, unit=0.23, color=self.ORANGE),
            self.layer_card(4, unit=0.20, color=self.PURPLE),
        ).arrange(RIGHT, buff=0.52)
        cards.move_to(LEFT * 2.75 + UP * 0.10)

        dots = self.M(r"\cdots", size=46, color=self.WHITE)
        dots.next_to(cards, RIGHT, buff=0.32)

        sum_box = self.formula_box(
            r"S=1^2+2^2+3^2+\cdots+n^2",
            size=37,
            stroke=self.BLUE,
            max_width=6.0,
        )
        sum_box.move_to(RIGHT * 3.25 + DOWN * 1.75)

        pyramid_origin = RIGHT * 2.8 + DOWN * 1.55
        pyramid = self.cube_group(self.square_pyramid_positions(4), origin=pyramid_origin, scale=0.28, colors=self.palette("blue"))
        pyramid_glow = SurroundingRectangle(pyramid, color=self.YELLOW, buff=0.16, corner_radius=0.10)
        pyramid_glow.set_stroke(width=2.0, opacity=0.8)
        pyramid_glow.set_fill(opacity=0)
        pyramid_glow.set_z_index(50)

        stack_arrow = Arrow(LEFT * 0.1 + DOWN * 0.05, RIGHT * 1.45 + DOWN * 0.05, buff=0.1)
        stack_arrow.set_color(self.WHITE)
        stack_arrow.set_z_index(50)

        note = self.label_box("Stack the layers: 1², 2², 3², 4², ...", size=22, stroke=self.YELLOW, max_width=4.6)
        note.move_to(RIGHT * 0.35 + DOWN * 0.78)

        self.speak(
            "Start with the individual square layers. One squared is a one by one layer. Two squared is a two by two layer. Three squared is a three by three layer. And so on.",
            FadeIn(heading, shift=UP * 0.06),
            LaggedStart(*[FadeIn(card, shift=UP * 0.05) for card in cards], lag_ratio=0.16),
            FadeIn(dots, shift=UP * 0.05),
            caption="Each k² is a square layer.",
            min_time=20,
        )

        self.speak(
            "If we stack those layers on top of one another, we get a stepped pile of cubes. "
            "The total number of little cubes inside that pile is exactly the sum S.",
            GrowArrow(stack_arrow),
            FadeIn(note, shift=UP * 0.05),
            LaggedStart(*[FadeIn(cube, shift=UP * 0.03) for cube in pyramid], lag_ratio=0.03),
            FadeIn(sum_box, shift=UP * 0.05),
            caption="The stacked layers represent the sum S.",
            min_time=18,
        )

        self.speak(
            "That stack is a nice mental picture of the sum. But the real trick for the proof is not the pile itself. "
            "The real trick is to study how a cube grows when its side length increases by one.",
            Create(pyramid_glow),
            caption="Now shift attention to cube growth.",
            min_time=15,
        )

    def detailed_cube_growth_scene(self):
        self.clear_stage()

        heading = self.T("Detailed shell growth: from 3³ to 4³", size=34, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.05)

        base_origin = LEFT * 2.55 + DOWN * 1.35
        scale = 0.36
        k = 3

        base_positions = [(x, y, z) for x in range(k) for y in range(k) for z in range(k)]
        base_cube = self.cube_group(base_positions, origin=base_origin, scale=scale, colors=self.palette("blue"))

        label_3 = self.formula_box(r"3^3=27", size=34, stroke=self.BLUE, max_width=3.4)
        label_3.move_to(LEFT * 4.55 + UP * 1.25)

        label_4 = self.formula_box(r"4^3=64", size=34, stroke=self.GREEN, max_width=3.4)
        label_4.move_to(RIGHT * 4.45 + UP * 1.25)

        arrow = Arrow(LEFT * 0.65 + DOWN * 0.25, RIGHT * 0.95 + DOWN * 0.25, buff=0.12)
        arrow.set_color(self.WHITE)
        arrow.set_z_index(50)

        shell_formula = self.formula_box(r"4^3-3^3=37", size=38, stroke=self.YELLOW, max_width=4.2)
        shell_formula.move_to(DOWN * 2.15)

        self.speak(
            "Let us not jump directly to the general symbol k. "
            "First watch one concrete example carefully. Start with a three by three by three cube. It contains twenty seven unit cubes.",
            FadeIn(heading, shift=UP * 0.06),
            LaggedStart(*[FadeIn(c, shift=UP * 0.03) for c in base_cube], lag_ratio=0.025),
            FadeIn(label_3, shift=UP * 0.04),
            caption="Concrete example: start with 3³ = 27.",
            min_time=22,
        )

        self.speak(
            "Now imagine the larger cube of side four. It contains sixty four unit cubes. So the new outer shell must contain sixty four minus twenty seven, which is thirty seven cubes.",
            GrowArrow(arrow),
            FadeIn(label_4, shift=UP * 0.04),
            FadeIn(shell_formula, shift=UP * 0.05),
            caption="The new shell has 64 − 27 = 37 cubes.",
            min_time=20,
        )

        top_positions = [(x, y, k) for x in range(k) for y in range(k)]
        face_y_positions = [(x, k, z) for x in range(k) for z in range(k)]
        face_x_positions = [(k, y, z) for y in range(k) for z in range(k)]
        edge_xy_positions = [(k, k, z) for z in range(k)]
        edge_xz_positions = [(k, y, k) for y in range(k)]
        edge_yz_positions = [(x, k, k) for x in range(k)]
        corner_positions = [(k, k, k)]

        top_target = self.cube_group(top_positions, origin=base_origin, scale=scale, colors=self.palette("orange"))
        face_y_target = self.cube_group(face_y_positions, origin=base_origin, scale=scale, colors=self.palette("purple"))
        face_x_target = self.cube_group(face_x_positions, origin=base_origin, scale=scale, colors=self.palette("red"))
        edge_xy_target = self.cube_group(edge_xy_positions, origin=base_origin, scale=scale, colors=self.palette("orange"))
        edge_xz_target = self.cube_group(edge_xz_positions, origin=base_origin, scale=scale, colors=self.palette("purple"))
        edge_yz_target = self.cube_group(edge_yz_positions, origin=base_origin, scale=scale, colors=self.palette("red"))
        corner_target = self.cube_group(corner_positions, origin=base_origin, scale=scale, colors=self.palette("blue"))

        top_piece = top_target.copy().shift(UP * 2.35 + RIGHT * 1.05)
        face_y_piece = face_y_target.copy().shift(LEFT * 2.15 + UP * 0.25)
        face_x_piece = face_x_target.copy().shift(RIGHT * 2.75 + DOWN * 0.10)
        edge_xy_piece = edge_xy_target.copy().shift(UP * 2.55 + RIGHT * 3.00)
        edge_xz_piece = edge_xz_target.copy().shift(RIGHT * 3.55 + DOWN * 1.25)
        edge_yz_piece = edge_yz_target.copy().shift(LEFT * 1.20 + UP * 2.70)
        corner_piece = corner_target.copy().shift(RIGHT * 4.15 + UP * 2.75)

        pieces = VGroup(top_piece, face_y_piece, face_x_piece, edge_xy_piece, edge_xz_piece, edge_yz_piece, corner_piece)

        face_note = self.label_box("First: three 3×3 square faces", size=22, stroke=self.ORANGE, max_width=4.4)
        face_note.move_to(RIGHT * 3.45 + UP * 0.35)
        face_formula = self.formula_box(r"3\cdot 3^2=27", size=34, stroke=self.ORANGE, max_width=3.8)
        face_formula.move_to(RIGHT * 3.45 + DOWN * 0.58)

        edge_note = self.label_box("Then: three edge rods of length 3", size=22, stroke=self.PURPLE, max_width=4.4)
        edge_note.move_to(RIGHT * 3.55 + UP * 0.18)
        edge_formula = self.formula_box(r"3\cdot 3=9", size=34, stroke=self.PURPLE, max_width=2.9)
        edge_formula.move_to(RIGHT * 3.55 + DOWN * 0.74)

        corner_note = self.label_box("Finally: one corner cube", size=22, stroke=self.GREEN, max_width=3.9)
        corner_note.move_to(RIGHT * 3.50 + UP * 0.20)
        corner_formula = self.formula_box(r"1", size=36, stroke=self.GREEN, max_width=1.3)
        corner_formula.move_to(RIGHT * 3.50 + DOWN * 0.72)

        total_note = self.formula_box(r"37=27+9+1", size=38, stroke=self.YELLOW, max_width=4.8)
        total_note.move_to(RIGHT * 3.55 + DOWN * 1.92)

        self.speak(
            "Now let us pull that shell apart so we can really see what it contains.",
            FadeIn(pieces),
            caption="Explode the shell into visible pieces.",
            min_time=11,
        )

        self.speak(
            "The biggest pieces are three square faces. One sits on top. One sits along one side. And one sits along the other side. Each face contains three squared cubes.",
            FadeIn(face_note, shift=UP * 0.05),
            FadeIn(face_formula, shift=UP * 0.05),
            Transform(top_piece, top_target),
            Transform(face_y_piece, face_y_target),
            Transform(face_x_piece, face_x_target),
            caption="Add the three 3×3 square faces.",
            min_time=23,
            motion_ratio=0.78,
        )

        self.play(FadeOut(face_note), FadeOut(face_formula), run_time=0.28)

        self.speak(
            "But the larger cube is not finished yet. Three exposed edges are still missing. Each one is a rod of length three.",
            FadeIn(edge_note, shift=UP * 0.05),
            FadeIn(edge_formula, shift=UP * 0.05),
            Transform(edge_xy_piece, edge_xy_target),
            Transform(edge_xz_piece, edge_xz_target),
            Transform(edge_yz_piece, edge_yz_target),
            caption="Add the three edge rods.",
            min_time=18,
            motion_ratio=0.78,
        )

        self.play(FadeOut(edge_note), FadeOut(edge_formula), run_time=0.28)

        self.speak(
            "After the faces and the edge rods, just one little cube is still missing at the far corner. Add that corner cube, and the four by four by four cube is complete.",
            FadeIn(corner_note, shift=UP * 0.05),
            FadeIn(corner_formula, shift=UP * 0.05),
            Transform(corner_piece, corner_target),
            caption="Add the final corner cube.",
            min_time=18,
            motion_ratio=0.75,
        )

        self.play(FadeOut(corner_note), FadeOut(corner_formula), run_time=0.28)

        self.speak(
            "So the shell contains twenty seven cubes from the three square faces, plus nine cubes from the three edge rods, plus one corner cube. In total, thirty seven.",
            FadeIn(total_note, shift=UP * 0.05),
            LaggedStart(
                Indicate(top_target, color=self.ORANGE, scale_factor=1.03),
                AnimationGroup(Indicate(face_y_target, color=self.ORANGE, scale_factor=1.03), Indicate(face_x_target, color=self.ORANGE, scale_factor=1.03)),
                AnimationGroup(Indicate(edge_xy_target, color=self.PURPLE, scale_factor=1.05), Indicate(edge_xz_target, color=self.PURPLE, scale_factor=1.05), Indicate(edge_yz_target, color=self.PURPLE, scale_factor=1.05)),
                Indicate(corner_target, color=self.GREEN, scale_factor=1.12),
                lag_ratio=0.18,
            ),
            caption="For k = 3, the shell is 3·3² + 3·3 + 1.",
            min_time=22,
        )

    def general_identity_scene(self):
        self.clear_stage()

        heading = self.T("Generalize the pattern", size=34, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.03)

        eq0 = self.formula_box(r"4^3-3^3=3\cdot 3^2+3\cdot 3+1", size=38, stroke=self.BLUE, max_width=8.2)
        eq0.move_to(UP * 0.95)

        arrow = Arrow(LEFT * 1.15 + DOWN * 0.05, RIGHT * 1.15 + DOWN * 0.05, buff=0.1)
        arrow.set_color(self.WHITE)
        arrow.set_z_index(50)

        eq1 = self.formula_box(r"(k+1)^3-k^3=3k^2+3k+1", size=44, stroke=self.YELLOW, max_width=8.5)
        eq1.move_to(DOWN * 0.28)

        cards = VGroup(
            self.label_box("3k² from the three square faces", size=22, stroke=self.ORANGE, max_width=4.6),
            self.label_box("3k from the three edge rods", size=22, stroke=self.PURPLE, max_width=4.4),
            self.label_box("1 from the corner cube", size=22, stroke=self.GREEN, max_width=4.0),
        ).arrange(DOWN, buff=0.22)
        cards.move_to(DOWN * 1.95)

        self.speak(
            "Now replace the specific number three with a general side length k. "
            "Nothing changes in the structure. A larger cube grows by three square faces, three edge rods, and one corner cube.",
            FadeIn(heading, shift=UP * 0.06),
            FadeIn(eq0, shift=UP * 0.05),
            GrowArrow(arrow),
            FadeIn(eq1, shift=UP * 0.05),
            caption="General shell identity: (k+1)³ − k³ = 3k² + 3k + 1.",
            min_time=23,
        )

        self.speak(
            "That is the crucial identity. It is the engine of the whole proof.",
            FadeIn(cards, shift=UP * 0.05),
            caption="Each term in the identity has a visual meaning.",
            min_time=13,
        )

    def telescoping_scene(self):
        self.clear_stage()

        heading = self.T("Add the identities from 1 to n", size=34, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.05)

        chain = VGroup(
            self.formula_box(r"2^3-1^3=3\cdot1^2+3\cdot1+1", size=30, stroke=self.BLUE, max_width=8.7),
            self.formula_box(r"3^3-2^3=3\cdot2^2+3\cdot2+1", size=30, stroke=self.GREEN, max_width=8.7),
            self.formula_box(r"4^3-3^3=3\cdot3^2+3\cdot3+1", size=30, stroke=self.ORANGE, max_width=8.7),
            self.formula_box(r"\vdots", size=34, stroke=self.WHITE, max_width=2.0),
            self.formula_box(r"(n+1)^3-n^3=3n^2+3n+1", size=30, stroke=self.PURPLE, max_width=8.7),
        ).arrange(DOWN, buff=0.18)
        chain.move_to(DOWN * 0.15)

        self.speak(
            "Write the shell identity for k equals one, then for k equals two, then for k equals three, and continue all the way to n.",
            FadeIn(heading, shift=UP * 0.06),
            LaggedStart(*[FadeIn(row, shift=UP * 0.04) for row in chain], lag_ratio=0.11),
            caption="Write the shell identity for k = 1, 2, 3, ..., n.",
            min_time=18,
        )

        self.clear_stage()

        heading2 = self.T("The left side telescopes", size=34, color=self.YELLOW, weight="BOLD")
        heading2.move_to(UP * 2.05)

        left = self.formula_box(
            r"(2^3-1^3)+(3^3-2^3)+\cdots+((n+1)^3-n^3)",
            size=31,
            stroke=self.BLUE,
            max_width=10.3,
        )
        left.move_to(UP * 1.02)

        cancel1 = self.formula_box(r"=(n+1)^3-1", size=41, stroke=self.GREEN, max_width=4.5)
        cancel1.move_to(UP * 0.02)

        right = self.formula_box(
            r"=3(1^2+2^2+\cdots+n^2)+3(1+2+\cdots+n)+n",
            size=30,
            stroke=self.ORANGE,
            max_width=10.5,
        )
        right.move_to(DOWN * 1.10)

        self.speak(
            "Now add all those equations. On the left side, the negative two cubed cancels the positive two cubed. The negative three cubed cancels the positive three cubed. And the same thing keeps happening. That is telescoping.",
            FadeIn(heading2, shift=UP * 0.06),
            FadeIn(left, shift=UP * 0.05),
            FadeIn(cancel1, shift=UP * 0.05),
            caption="The left side collapses to (n+1)³ − 1.",
            min_time=24,
        )

        self.speak(
            "On the right side, all the square terms collect together, all the linear terms collect together, and the constant ones add up to n.",
            FadeIn(right, shift=UP * 0.05),
            caption="The right side collects into three groups.",
            min_time=17,
        )

    def solve_scene(self):
        self.clear_stage()

        heading = self.T("Now isolate the sum of squares", size=34, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.05)

        eq1 = self.formula_box(
            r"(n+1)^3-1=3S+3(1+2+\cdots+n)+n",
            size=35,
            stroke=self.BLUE,
            max_width=9.8,
        )
        eq1.move_to(UP * 0.92)

        eq2 = self.formula_box(
            r"1+2+\cdots+n=\frac{n(n+1)}{2}",
            size=38,
            stroke=self.GREEN,
            max_width=6.3,
        )
        eq2.move_to(DOWN * 0.10)

        eq3 = self.formula_box(
            r"(n+1)^3-1=3S+\frac{3n(n+1)}{2}+n",
            size=34,
            stroke=self.ORANGE,
            max_width=9.9,
        )
        eq3.move_to(DOWN * 1.15)

        self.speak(
            "Let S denote the sum of squares. Then the collected identity becomes this equation. To handle the linear sum, use the formula from the previous staircase proof: one plus two plus up to n equals n times n plus one over two.",
            FadeIn(heading, shift=UP * 0.06),
            FadeIn(eq1, shift=UP * 0.05),
            FadeIn(eq2, shift=UP * 0.05),
            FadeIn(eq3, shift=UP * 0.05),
            caption="Substitute the known formula for 1 + 2 + ... + n.",
            min_time=24,
        )

        self.clear_stage()

        heading2 = self.T("Simplify step by step", size=34, color=self.YELLOW, weight="BOLD")
        heading2.move_to(UP * 2.05)

        s1 = self.formula_box(r"3S=(n+1)^3-1-\frac{3n(n+1)}{2}-n", size=34, stroke=self.BLUE, max_width=9.8)
        s1.move_to(UP * 0.98)

        s2 = self.formula_box(r"3S=\frac{n(n+1)(2n+1)}{2}", size=42, stroke=self.GREEN, max_width=7.7)
        s2.move_to(DOWN * 0.02)

        s3 = self.formula_box(r"S=\frac{n(n+1)(2n+1)}{6}", size=48, stroke=self.YELLOW, max_width=7.8)
        s3.move_to(DOWN * 1.23)

        final_note = self.label_box("This is the exact formula for 1² + 2² + ... + n².", size=24, stroke=self.PURPLE, max_width=7.0)
        final_note.move_to(DOWN * 2.18)

        self.speak(
            "Move the extra terms to the other side. Then simplify the algebra. After simplification, three S equals n times n plus one times two n plus one, all over two.",
            FadeIn(heading2, shift=UP * 0.06),
            FadeIn(s1, shift=UP * 0.05),
            FadeIn(s2, shift=UP * 0.05),
            caption="After simplification: 3S = n(n+1)(2n+1)/2.",
            min_time=21,
        )

        self.speak(
            "Now divide both sides by three. The denominator becomes six, and the sum of squares formula appears.",
            FadeIn(s3, shift=UP * 0.05),
            FadeIn(final_note, shift=UP * 0.05),
            caption="Therefore S = n(n+1)(2n+1)/6.",
            min_time=17,
        )

    def recap_scene(self):
        self.clear_stage()

        heading = self.T("Recap", size=35, color=self.YELLOW, weight="BOLD")
        heading.move_to(UP * 2.05)
        self.speak(
            "Let us summarize the logic one more time, but now in a compact chain.",
            FadeIn(heading, shift=UP * 0.06),
            caption="Recap of the full argument.",
            min_time=9,
        )

        chain = [
            (r"S=1^2+2^2+\cdots+n^2", "Start with square layers.", "Start with the sum of square layers."),
            (r"(k+1)^3-k^3=3k^2+3k+1", "Growing a cube creates three square faces, three edge rods, and one corner cube.", "Count the shell of the larger cube."),
            (r"(n+1)^3-1=3S+3(1+2+\cdots+n)+n", "Add the shell identities from one to n, and the left side telescopes.", "Add the identities and telescope."),
            (r"1+2+\cdots+n=\frac{n(n+1)}{2}", "Use the known natural-number sum.", "Use the previous staircase formula."),
            (r"S=\frac{n(n+1)(2n+1)}{6}", "Then solve for S.", "Obtain the final formula."),
        ]

        current = None
        for tex, narration, cap in chain:
            box = self.formula_box(tex, size=32, stroke=self.YELLOW, max_width=10.2)
            box.move_to(DOWN * 0.12)
            if current is None:
                self.speak(narration, FadeIn(box, shift=UP * 0.06), caption=cap, min_time=10)
            else:
                self.speak(narration, FadeOut(current), FadeIn(box, shift=UP * 0.06), caption=cap, min_time=12)
            current = box

        note = self.label_box("The visual heart of the proof is the cube shell.", size=24, stroke=self.GREEN, max_width=5.9)
        note.move_to(DOWN * 1.90)
        self.speak(
            "So the part to remember is this: the sum of squares is hiding inside the shell of a growing cube.",
            FadeIn(note, shift=UP * 0.05),
            caption="Remember the cube shell picture.",
            min_time=15,
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
            "Square layers built the sum.\nThe growing cube explained the formula.",
            size=33,
            color=self.WHITE,
            weight="BOLD",
            line_spacing=0.92,
        )
        message.next_to(final, DOWN, buff=0.62)

        self.speak(
            "Square layers built the sum. The growing cube explained the formula.",
            FadeIn(final, scale=0.96),
            FadeIn(message, shift=UP * 0.08),
            min_time=12,
        )
        self.wait(2)
