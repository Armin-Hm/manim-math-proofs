import textwrap
import numpy as np

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


config.background_color = "#08111F"
config.frame_rate = 30


class QuadraticFormulaWorldClass(VoiceoverScene):
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

    # ------------------------------------------------------------------
    # Core visual helpers
    # ------------------------------------------------------------------

    def T(self, text, size=28, color=None, weight=NORMAL, line_spacing=0.9):
        mob = Text(
            str(text),
            font_size=size,
            color=color or self.WHITE,
            weight=weight,
            line_spacing=line_spacing,
        )
        mob.set_z_index(50)
        return mob

    def M(self, tex, size=42, color=None):
        mob = MathTex(tex, font_size=size, color=color or self.WHITE)
        mob.set_z_index(50)
        return mob

    def subtle_grid(self):
        """
        Professional 3B1B-style coordinate background:
        - Cartesian axes are kept.
        - They are visible but not dominant.
        - Grid stays behind all mathematical objects.
        """
        plane = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-5, 5, 1],
            axis_config={
                "stroke_color": "#D8E2F0",
                "stroke_width": 1.25,
                "stroke_opacity": 0.26,
            },
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.105,
            },
            faded_line_ratio=2,
        )

        plane.set_z_index(-100)
        return plane

    def formula_box(self, tex, size=42, stroke=None, color=None, max_width=10.8):
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
        group.set_z_index(40)
        return group

    def formula_card(self, tex, label, color):
        formula = self.M(tex, size=34, color=color)
        label_mob = self.T(label, size=20, color=self.WHITE, weight=MEDIUM)

        content = VGroup(formula, label_mob).arrange(DOWN, buff=0.10)

        bg = BackgroundRectangle(
            content,
            color=BLACK,
            fill_opacity=0.22,
            buff=0.20,
        )

        frame = SurroundingRectangle(
            bg,
            buff=0.035,
            color=color,
            corner_radius=0.10,
        )
        frame.set_stroke(color, width=2.0)

        card = VGroup(bg, frame, content)
        card.set_z_index(45)
        return card

    def rect_area(self, width, height, color, opacity=0.72):
        r = Rectangle(width=width, height=height)
        r.set_fill(color, opacity=opacity)
        r.set_stroke(self.WHITE, width=2.4)
        r.set_z_index(35)
        return r

    def glow(self, mob, color=None, buff=0.14):
        color = color or self.YELLOW
        g = SurroundingRectangle(
            mob,
            color=color,
            buff=buff,
            corner_radius=0.12,
        )
        g.set_stroke(color, width=4)
        g.set_z_index(80)
        return g

    # ------------------------------------------------------------------
    # Stage layout helpers
    # ------------------------------------------------------------------

    def stage_center(self):
        if self.title_mode == "hero":
            return DOWN * 0.22
        return DOWN * 0.12

    def fit_width(self, mob, max_width=11.0):
        if mob.width > max_width:
            mob.scale(max_width / mob.width)
        return mob

    def fit_height(self, mob, max_height=5.55):
        if mob.height > max_height:
            mob.scale(max_height / mob.height)
        return mob

    def fit_stage(self, mob, max_width=11.0, max_height=5.55):
        self.fit_width(mob, max_width=max_width)
        self.fit_height(mob, max_height=max_height)
        return mob

    def place_stage_center(self, mob, max_width=11.0, max_height=5.55, shift=ORIGIN):
        self.fit_stage(mob, max_width=max_width, max_height=max_height)
        mob.move_to(self.stage_center() + shift)
        return mob

    # ------------------------------------------------------------------
    # Title and caption system
    # ------------------------------------------------------------------

    def build_title(self):
        title = self.T("Quadratic Formula", size=66, color=self.WHITE, weight=BOLD)
        subtitle = self.T(
            "A visual proof by completing the square",
            size=25,
            color=GREY_A,
        )

        group = VGroup(title, subtitle).arrange(DOWN, buff=0.04)
        group.to_edge(UP, buff=0.18)
        group.set_z_index(70)

        self.title_group = group
        self.title_mode = "hero"
        return group

    def compact_title(self):
        if self.title_mode == "compact":
            return

        compact = VGroup(
            self.T("Quadratic Formula", size=28, color=self.WHITE, weight=BOLD),
            self.T("completing the square", size=15, color=GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.01)

        # Keep it inside the frame. Do not let it clip at the top.
        compact.to_corner(UL, buff=0.42)
        compact.set_z_index(70)

        self.play(
            Transform(self.title_group, compact),
            run_time=0.65,
            rate_func=smooth,
        )

        self.title_mode = "compact"

    def make_caption(self, text):
        wrapped = "\n".join(
            textwrap.wrap(
                str(text),
                width=48,
                break_long_words=False,
                replace_whitespace=False,
            )[:2]
        )

        band = Rectangle(width=12.2, height=0.82)
        band.to_edge(DOWN, buff=0)
        band.set_fill(BLACK, opacity=0.74)
        band.set_stroke(width=0)
        band.set_z_index(95)

        label = self.T(
            wrapped,
            size=24,
            color=self.WHITE,
            weight=NORMAL,
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
            old_caption = self.current_caption
            self.play(
                FadeOut(old_caption, shift=DOWN * 0.03),
                FadeIn(new_caption, shift=UP * 0.03),
                run_time=0.18,
                rate_func=linear,
            )

        self.current_caption = new_caption

    def hide_caption(self):
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption), run_time=0.18)
            self.current_caption = None

    def speak(self, narration, *animations, caption=None, min_time=0.0, motion_ratio=0.68):
        if caption is not None:
            self.transition_caption(caption)

        with self.voiceover(text=narration) as tracker:
            total = max(float(tracker.duration), float(min_time))

            if animations:
                motion_time = min(
                    max(0.75, total * motion_ratio),
                    max(0.75, total - 0.12),
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

    def clear_stage(self):
        protected = list(self.keep)

        if self.title_group is not None:
            protected.append(self.title_group)

        if self.current_caption is not None:
            protected.append(self.current_caption)

        removable = [m for m in self.mobjects if m not in protected]

        if removable:
            self.play(*[FadeOut(m) for m in removable], run_time=0.55)

    # ------------------------------------------------------------------
    # Main construction
    # ------------------------------------------------------------------

    def construct(self):
        bg = self.subtle_grid()
        title = self.build_title()

        self.add(bg)
        self.keep = [bg]

        self.play(
            Write(title[0]),
            FadeIn(title[1], shift=UP * 0.06),
            run_time=1.25,
        )

        self.intro()
        self.normalize_equation()
        self.split_middle_term()
        self.area_model()
        self.complete_the_square()
        self.balance_scene()
        self.algebra_translation()
        self.solve_for_x()
        self.discriminant_scene()
        self.recap_scene()
        self.outro()

    # ------------------------------------------------------------------
    # Scenes
    # ------------------------------------------------------------------

    def intro(self):
        start = self.formula_box(
            r"ax^2+bx+c=0",
            size=52,
            stroke=self.YELLOW,
        )
        start.move_to(UP * 1.12)

        final = self.formula_box(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=48,
            stroke=self.GREEN,
        )
        final.next_to(start, DOWN, buff=0.82)

        group = VGroup(start, final)
        self.fit_stage(group, max_width=10.8, max_height=3.4)

        self.speak(
            "The quadratic formula is often memorized as a mysterious object. "
            "But it is not mysterious. It is the shape of a completed square written in symbols.",
            FadeIn(start, shift=UP * 0.12),
            caption="Start with the general quadratic equation.",
            min_time=15,
        )

        self.speak(
            "This is the destination. The goal is to explain why every piece appears: "
            "negative b, plus or minus, the square root, and the denominator two a.",
            FadeIn(final, shift=UP * 0.12),
            caption="Goal: explain every piece of the formula.",
            min_time=17,
        )

        cards = VGroup(
            self.formula_card(r"-b", "shift of x", self.ORANGE),
            self.formula_card(r"\pm", "two roots", self.YELLOW),
            self.formula_card(r"\sqrt{b^2-4ac}", "remaining area", self.GREEN),
            self.formula_card(r"2a", "half-width", self.BLUE),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.38, 0.32))

        cards.scale(0.88)
        cards.move_to(DOWN * 2.02)

        self.speak(
            "Instead of showing these pieces in a crowded row, think of them as four design clues. "
            "Each clue will come from one visual move.",
            FadeIn(cards, shift=UP * 0.10),
            caption="Four pieces, four reasons.",
            min_time=17,
        )

        self.compact_title()

    def normalize_equation(self):
        self.clear_stage()

        eq1 = self.formula_box(r"ax^2+bx+c=0", size=45, stroke=self.YELLOW)
        eq2 = self.formula_box(
            r"x^2+\frac{b}{a}x+\frac{c}{a}=0",
            size=41,
            stroke=self.BLUE,
        )
        eq3 = self.formula_box(
            r"x^2+\frac{b}{a}x=-\frac{c}{a}",
            size=41,
            stroke=self.ORANGE,
        )

        eqs = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.52)
        eqs.move_to(DOWN * 0.12)

        tag1 = self.T("divide by a", size=22, color=self.YELLOW, weight=MEDIUM)
        tag2 = self.T("move constant", size=22, color=self.ORANGE, weight=MEDIUM)

        tag1.next_to(eq2, RIGHT, buff=0.35)
        tag2.next_to(eq3, RIGHT, buff=0.35)

        arrows = VGroup(
            Arrow(eq1.get_bottom(), eq2.get_top(), buff=0.14, color=self.YELLOW),
            Arrow(eq2.get_bottom(), eq3.get_top(), buff=0.14, color=self.YELLOW),
        )

        self.speak(
            "First divide every term by a. This makes the x squared coefficient equal to one, "
            "which is exactly what we need for a clean square picture.",
            FadeIn(eq1),
            GrowArrow(arrows[0]),
            FadeIn(eq2),
            FadeIn(tag1),
            caption="Step 1: make the x² coefficient equal to 1.",
            min_time=17,
        )

        self.speak(
            "Next move the constant term to the right. "
            "Now the left side contains only the pieces we want to draw.",
            GrowArrow(arrows[1]),
            FadeIn(eq3),
            FadeIn(tag2),
            caption="Step 2: isolate the x-pieces on the left.",
            min_time=16,
        )

        focus = self.glow(eq3, color=self.YELLOW)

        self.speak(
            "From this point on, the whole proof is about reshaping this left side into one perfect square.",
            Create(focus),
            caption="The left side is the object we reshape.",
            min_time=13,
        )

    def split_middle_term(self):
        self.clear_stage()

        eq = self.formula_box(
            r"x^2+\frac{b}{a}x",
            size=50,
            stroke=self.YELLOW,
        )
        eq.move_to(UP * 1.35)

        split = self.formula_box(
            r"x^2+\frac{b}{2a}x+\frac{b}{2a}x",
            size=43,
            stroke=self.GREEN,
        )
        split.move_to(UP * 0.02)

        strip = self.rect_area(5.1, 0.78, self.GREEN, opacity=0.72)
        strip.move_to(DOWN * 1.75)

        cut = DashedLine(
            strip.get_top(),
            strip.get_bottom(),
            color=self.YELLOW,
            dash_length=0.08,
        )
        cut.move_to(strip.get_center())
        cut.set_z_index(60)

        left = self.rect_area(2.55, 0.78, self.GREEN, opacity=0.72)
        right = self.rect_area(2.55, 0.78, self.GREEN, opacity=0.72)

        left.move_to(strip.get_center() + LEFT * 1.275)
        right.move_to(strip.get_center() + RIGHT * 1.275)

        l_label = self.M(r"\frac{b}{2a}x", size=30)
        r_label = self.M(r"\frac{b}{2a}x", size=30)

        l_label.move_to(left)
        r_label.move_to(right)

        self.speak(
            "The middle term is the key. Instead of treating b over a times x as one block, "
            "we cut it into two equal pieces.",
            FadeIn(eq, shift=UP * 0.08),
            FadeIn(split, shift=UP * 0.08),
            caption="Split the middle term into two equal halves.",
            min_time=17,
        )

        self.speak(
            "Visually, that means one long green rectangle becomes two equal green rectangles.",
            FadeIn(strip),
            Create(cut),
            caption="One rectangle becomes two side strips.",
            min_time=13,
        )

        self.play(FadeOut(cut), Transform(strip, VGroup(left, right)), run_time=1.2)
        self.play(FadeIn(l_label), FadeIn(r_label), run_time=0.65)
        self.wait(0.4)

    def area_model(self):
        self.clear_stage()

        # Geometry construction.
        # Important: everything is positioned from ONE anchor.
        # We do not move the blue square after placing the green strips.
        x_side = 2.42
        p_side = 0.74

        # Put the construction slightly left of center so the y-axis remains visible
        # without cutting through the main diagram.
        anchor = LEFT * 1.55 + DOWN * 0.35

        x_square = self.rect_area(x_side, x_side, self.BLUE, opacity=0.76)
        x_square.move_to(anchor)

        x_label = self.M(r"x^2", size=44)
        x_label.move_to(x_square)

        right_strip = self.rect_area(p_side, x_side, self.GREEN, opacity=0.76)
        right_strip.next_to(x_square, RIGHT, buff=0)

        top_strip = self.rect_area(x_side, p_side, self.GREEN, opacity=0.76)
        top_strip.next_to(x_square, UP, buff=0)

        # Starting positions for the strips.
        right_start = right_strip.copy().shift(RIGHT * 1.25)
        top_start = top_strip.copy().shift(UP * 0.95)

        r_label_start = self.M(r"\frac{b}{2a}x", size=26)
        r_label_start.rotate(PI / 2)
        r_label_start.move_to(right_start)

        t_label_start = self.M(r"\frac{b}{2a}x", size=26)
        t_label_start.move_to(top_start)

        # Final labels.
        r_label_final = r_label_start.copy()
        r_label_final.move_to(right_strip)

        t_label_final = t_label_start.copy()
        t_label_final.move_to(top_strip)

        # x braces
        bx = Brace(x_square, DOWN, color=self.WHITE)
        bx_lab = self.M(r"x", size=28)
        bx_lab.next_to(bx, DOWN, buff=0.09)

        by = Brace(x_square, LEFT, color=self.WHITE)
        by_lab = self.M(r"x", size=28)
        by_lab.next_to(by, LEFT, buff=0.09)

        self.speak(
            "Now draw x squared as a blue square. Its side length is x, so its area is x squared.",
            FadeIn(x_square, scale=0.92),
            FadeIn(x_label),
            FadeIn(bx),
            FadeIn(bx_lab),
            FadeIn(by),
            FadeIn(by_lab),
            caption="x² is a square with side x.",
            min_time=15,
        )

        self.speak(
            "Bring in the two green half-strips. One attaches to the right side, and the other attaches to the top.",
            FadeIn(right_start),
            FadeIn(top_start),
            FadeIn(r_label_start),
            FadeIn(t_label_start),
            caption="The two half-strips wrap around x².",
            min_time=16,
        )

        self.speak(
            "Slide them into place. The shape is almost a bigger square, except for one missing corner.",
            Transform(right_start, right_strip),
            Transform(top_start, top_strip),
            Transform(r_label_start, r_label_final),
            Transform(t_label_start, t_label_final),
            caption="Almost a square — one corner is missing.",
            min_time=16,
        )

        # Full completed side label.
        side_label = self.M(
            r"x+\frac{b}{2a}",
            size=32,
            color=self.YELLOW,
        )
        side_label.next_to(VGroup(x_square, top_strip), UP, buff=0.28)

        # Thickness brace on right strip.
        thick_brace = Brace(right_strip, RIGHT, color=self.YELLOW)
        thick_label = self.M(r"\frac{b}{2a}", size=27, color=self.YELLOW)
        thick_label.next_to(thick_brace, RIGHT, buff=0.11)

        self.speak(
            "The thickness of each strip is b over two a. So the completed side length would be x plus b over two a.",
            FadeIn(side_label),
            FadeIn(thick_brace),
            FadeIn(thick_label),
            caption="The completed side length is x + b / 2a.",
            min_time=17,
        )

        # Save references for the next scene.
        self.x_square = x_square
        self.right_strip = right_start
        self.top_strip = top_start
        self.x_side = x_side
        self.p_side = p_side

    def complete_the_square(self):
        x_square = self.x_square
        x_side = self.x_side
        p_side = self.p_side

        # The missing corner is computed from the actual x_square position.
        corner = self.rect_area(p_side, p_side, self.YELLOW, opacity=0.90)
        corner.move_to(
            x_square.get_corner(UR)
            + RIGHT * p_side / 2
            + UP * p_side / 2
        )

        corner_label = self.M(
            r"\left(\frac{b}{2a}\right)^2",
            size=21,
            color=BLACK,
        )
        corner_label.move_to(corner)

        ghost = VGroup(corner.copy(), corner_label.copy())
        ghost.set_opacity(0.32)

        self.speak(
            "The missing corner has side b over two a in both directions. Therefore its area is b over two a squared.",
            FadeIn(ghost),
            caption="The missing corner is (b / 2a)².",
            min_time=16,
        )

        self.play(FadeOut(ghost), run_time=0.35)

        # Put the explanation formula on the open right side of the frame.
        corner_formula = self.formula_box(
            r"\left(\frac{b}{2a}\right)^2",
            size=35,
            stroke=self.YELLOW,
        )
        corner_formula.move_to(RIGHT * 2.65 + DOWN * 0.05)

        self.speak(
            "That is the exact term we add. It is not a trick; it is the missing tile.",
            FadeIn(corner, scale=0.92),
            FadeIn(corner_label),
            FadeIn(corner_formula),
            caption="Completing the square means adding the missing tile.",
            min_time=15,
        )

        outline = Square(side_length=x_side + p_side)
        outline.set_fill(BLACK, opacity=0)
        outline.set_stroke(self.YELLOW, width=4.5)
        outline.move_to(
            x_square.get_corner(DL)
            + RIGHT * (x_side + p_side) / 2
            + UP * (x_side + p_side) / 2
        )
        outline.set_z_index(70)

        identity = self.formula_box(
            r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
            r"=\left(x+\frac{b}{2a}\right)^2",
            size=29,
            stroke=self.GREEN,
            max_width=5.9,
        )
        identity.move_to(RIGHT * 2.65 + DOWN * 1.42)

        self.speak(
            "Once the corner is added, the entire figure is one square. Its side length is x plus b over two a.",
            Create(outline),
            FadeIn(identity, shift=UP * 0.08),
            caption="The left side has become one perfect square.",
            min_time=18,
        )

    def balance_scene(self):
        self.clear_stage()

        equation = self.formula_box(
            r"x^2+\frac{b}{a}x=-\frac{c}{a}",
            size=43,
            stroke=self.YELLOW,
        )
        equation.move_to(UP * 1.55)

        beam = Line(LEFT * 3.3, RIGHT * 3.3, color=GREY_B)
        beam.set_stroke(GREY_B, width=3)
        beam.move_to(DOWN * 0.20)

        pivot = Triangle()
        pivot.scale(0.32)
        pivot.rotate(PI)
        pivot.set_fill(GREY_D, opacity=0.75)
        pivot.set_stroke(self.WHITE, width=2)
        pivot.next_to(beam, DOWN, buff=0)

        left_label = self.T("left side", size=22, color=self.BLUE, weight=MEDIUM)
        right_label = self.T("right side", size=22, color=self.ORANGE, weight=MEDIUM)

        left_label.next_to(beam, LEFT, buff=0.55).shift(UP * 0.55)
        right_label.next_to(beam, RIGHT, buff=0.55).shift(UP * 0.55)

        self.speak(
            "But an equation is a balance. Whatever we add to one side, "
            "we must add to the other side as well.",
            FadeIn(equation),
            FadeIn(beam),
            FadeIn(pivot),
            FadeIn(left_label),
            FadeIn(right_label),
            caption="Whatever we add to one side, we add to the other.",
            min_time=17,
        )

        add_left = self.formula_box(
            r"+\left(\frac{b}{2a}\right)^2",
            size=33,
            stroke=self.YELLOW,
        )
        add_right = self.formula_box(
            r"+\left(\frac{b}{2a}\right)^2",
            size=33,
            stroke=self.YELLOW,
        )

        add_left.move_to(LEFT * 2.55 + UP * 0.85)
        add_right.move_to(RIGHT * 2.55 + UP * 0.85)

        self.speak(
            "So the missing corner is added to both sides. "
            "This keeps the equation balanced while completing the square.",
            FadeIn(add_left, shift=UP * 0.10),
            FadeIn(add_right, shift=UP * 0.10),
            caption="Add the missing corner to both sides.",
            min_time=16,
        )

        balanced = self.formula_box(
            r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
            r"=-\frac{c}{a}+\left(\frac{b}{2a}\right)^2",
            size=31,
            stroke=self.GREEN,
            max_width=10.2,
        )
        balanced.move_to(DOWN * 2.05)

        self.speak(
            "Now the left side is ready to become a perfect square, "
            "and the equality is still true.",
            FadeIn(balanced, shift=UP * 0.08),
            caption="The equation remains balanced.",
            min_time=15,
        )

    def algebra_translation(self):
        self.clear_stage()

        eq1 = self.formula_box(
            r"\left(x+\frac{b}{2a}\right)^2"
            r"=-\frac{c}{a}+\frac{b^2}{4a^2}",
            size=39,
            stroke=self.GREEN,
            max_width=10.6,
        )
        eq1.move_to(UP * 1.25)

        common = self.formula_box(
            r"-\frac{c}{a}=-\frac{4ac}{4a^2}",
            size=37,
            stroke=self.ORANGE,
        )
        common.move_to(DOWN * 0.20)

        eq2 = self.formula_box(
            r"\left(x+\frac{b}{2a}\right)^2"
            r"=\frac{b^2-4ac}{4a^2}",
            size=40,
            stroke=self.YELLOW,
            max_width=10.6,
        )
        eq2.move_to(DOWN * 1.60)

        self.speak(
            "Now we translate the completed square back into algebra. "
            "The left side is one square.",
            FadeIn(eq1),
            caption="The completed square becomes algebra.",
            min_time=15,
        )

        self.speak(
            "To combine the right side, rewrite negative c over a with denominator four a squared.",
            FadeIn(common, shift=UP * 0.08),
            caption="Use a common denominator.",
            min_time=15,
        )

        self.speak(
            "After combining, the expression b squared minus four a c appears. "
            "This is the discriminant.",
            FadeIn(eq2, shift=UP * 0.08),
            caption="The expression b² - 4ac appears.",
            min_time=17,
        )

    def solve_for_x(self):
        self.clear_stage()

        eq1 = self.formula_box(
            r"\left(x+\frac{b}{2a}\right)^2"
            r"=\frac{b^2-4ac}{4a^2}",
            size=39,
            stroke=self.YELLOW,
            max_width=10.6,
        )
        eq1.move_to(UP * 1.45)

        eq2 = self.formula_box(
            r"x+\frac{b}{2a}"
            r"=\pm\frac{\sqrt{b^2-4ac}}{2a}",
            size=39,
            stroke=self.ORANGE,
            max_width=10.6,
        )
        eq2.move_to(UP * 0.05)

        eq3 = self.formula_box(
            r"x=-\frac{b}{2a}\pm\frac{\sqrt{b^2-4ac}}{2a}",
            size=39,
            stroke=self.BLUE,
            max_width=10.6,
        )
        eq3.move_to(DOWN * 1.35)

        self.speak(
            "Now take the square root of both sides.",
            FadeIn(eq1),
            caption="Take the square root of both sides.",
            min_time=11,
        )

        self.speak(
            "The plus or minus sign appears because two opposite numbers can have the same square.",
            FadeIn(eq2, shift=UP * 0.08),
            caption="Taking a square root creates ±.",
            min_time=17,
        )

        self.speak(
            "Then subtract b over two a from both sides. "
            "That is where the negative b comes from.",
            FadeIn(eq3, shift=UP * 0.08),
            caption="Subtract b / 2a to isolate x.",
            min_time=16,
        )

        self.clear_stage()

        final = self.formula_box(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=53,
            stroke=self.YELLOW,
            max_width=10.8,
        )
        final.move_to(UP * 0.35)

        note = self.T(
            "The formula is not magic.\nIt is a completed square, solved for x.",
            size=32,
            color=self.WHITE,
            weight=BOLD,
            line_spacing=0.90,
        )
        note.next_to(final, DOWN, buff=0.60)

        self.speak(
            "Combine the two fractions over the common denominator two a, "
            "and the quadratic formula appears.",
            FadeIn(final, scale=0.96),
            FadeIn(note, shift=UP * 0.08),
            caption="The quadratic formula appears.",
            min_time=18,
        )

    def discriminant_scene(self):
        self.clear_stage()

        axes = Axes(
            x_range=[-4.5, 4.5, 1],
            y_range=[-2.4, 5.2, 1],
            x_length=7.0,
            y_length=4.35,
            axis_config={
                "include_tip": True,
                "color": GREY_B,
                "stroke_width": 2,
            },
        )
        axes.move_to(DOWN * 0.25 + LEFT * 1.15)

        graph = axes.plot(
            lambda x: 0.45 * (x + 2.15) * (x - 1.35),
            color=self.BLUE,
            stroke_width=5,
        )

        label = self.formula_box(
            r"y=ax^2+bx+c",
            size=36,
            stroke=self.BLUE,
        )
        label.move_to(UP * 1.85 + LEFT * 1.15)

        root1 = Dot(axes.c2p(-2.15, 0), color=self.YELLOW, radius=0.09)
        root2 = Dot(axes.c2p(1.35, 0), color=self.YELLOW, radius=0.09)

        self.speak(
            "There is also a graph meaning. Solving the quadratic equation means finding where the parabola crosses the x-axis.",
            FadeIn(label),
            FadeIn(axes),
            Create(graph),
            caption="Roots are x-axis crossings.",
            min_time=16,
        )

        self.speak(
            "When the discriminant is positive, the formula gives two real roots. "
            "On the graph, that means two crossings.",
            FadeIn(root1, scale=1.4),
            FadeIn(root2, scale=1.4),
            caption="Positive discriminant: two real roots.",
            min_time=16,
        )

        disc = self.formula_box(
            r"D=b^2-4ac",
            size=45,
            stroke=self.YELLOW,
        )
        disc.move_to(RIGHT * 3.35 + UP * 1.55)

        cases = VGroup(
            self.formula_box(r"D>0:\ \text{two roots}", size=28, stroke=self.GREEN),
            self.formula_box(r"D=0:\ \text{one root}", size=28, stroke=self.YELLOW),
            self.formula_box(r"D<0:\ \text{no real roots}", size=28, stroke=self.RED),
        ).arrange(DOWN, buff=0.25)

        cases.next_to(disc, DOWN, buff=0.35)

        self.speak(
            "The discriminant controls how many real roots the equation has.",
            FadeIn(disc, shift=UP * 0.08),
            FadeIn(cases, shift=RIGHT * 0.08),
            caption="The discriminant controls the real roots.",
            min_time=16,
        )

    def recap_scene(self):
        self.clear_stage()

        heading = self.T(
            "The proof, compressed",
            size=35,
            color=self.YELLOW,
            weight=BOLD,
        )
        heading.move_to(UP * 2.05)

        self.speak(
            "Now compress the proof into one clean chain.",
            FadeIn(heading, shift=UP * 0.08),
            caption="The proof in one chain.",
            min_time=10,
        )

        chain = [
            (
                r"ax^2+bx+c=0",
                "Start from the general quadratic equation.",
                "Start.",
            ),
            (
                r"x^2+\frac{b}{a}x=-\frac{c}{a}",
                "Divide by a, then move the constant to the right.",
                "Prepare the equation.",
            ),
            (
                r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
                r"=-\frac{c}{a}+\left(\frac{b}{2a}\right)^2",
                "Add the missing corner to both sides.",
                "Add the missing corner.",
            ),
            (
                r"\left(x+\frac{b}{2a}\right)^2=\frac{b^2-4ac}{4a^2}",
                "The left side becomes one square.",
                "A square appears.",
            ),
            (
                r"x+\frac{b}{2a}=\pm\frac{\sqrt{b^2-4ac}}{2a}",
                "Take the square root.",
                "The ± appears.",
            ),
            (
                r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
                "Isolate x.",
                "The formula is born.",
            ),
        ]

        current = None

        for tex, narration, cap in chain:
            nxt = self.formula_box(
                tex,
                size=35,
                stroke=self.YELLOW,
                max_width=10.6,
            )
            nxt.move_to(DOWN * 0.10)

            if current is None:
                self.speak(
                    narration,
                    FadeIn(nxt, shift=UP * 0.08),
                    caption=cap,
                    min_time=11,
                )
            else:
                self.speak(
                    narration,
                    FadeOut(current),
                    FadeIn(nxt, shift=UP * 0.08),
                    caption=cap,
                    min_time=11,
                )

            current = nxt

        final_note = self.T(
            "Visual move: add the missing corner.\nAlgebraic result: the quadratic formula.",
            size=31,
            color=self.WHITE,
            weight=BOLD,
            line_spacing=0.90,
        )
        final_note.move_to(DOWN * 1.95)

        self.speak(
            "The visual move is simple: add the missing corner. "
            "The algebraic result is the quadratic formula.",
            FadeIn(final_note, shift=UP * 0.08),
            caption="One visual move creates the whole formula.",
            min_time=16,
        )

    def outro(self):
        self.clear_stage()
        self.hide_caption()

        final = self.formula_box(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=54,
            stroke=self.YELLOW,
            max_width=10.8,
        )
        final.move_to(UP * 0.40)

        message = self.T(
            "A quadratic became a square.\nThe square gave the formula.",
            size=35,
            color=self.WHITE,
            weight=BOLD,
            line_spacing=0.90,
        )
        message.next_to(final, DOWN, buff=0.65)

        self.speak(
            "A quadratic became a square. The square gave the formula.",
            FadeIn(final, scale=0.96),
            FadeIn(message, shift=UP * 0.08),
            min_time=12,
        )

        self.wait(2)
