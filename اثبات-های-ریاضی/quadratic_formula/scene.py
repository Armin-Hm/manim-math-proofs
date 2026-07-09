from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

config.background_color = "#0B1020"
config.frame_rate = 30


class QuadraticFormulaVideo(VoiceoverScene):
    def setup(self):
        super().setup()
        self.set_speech_service(GTTSService(lang="en", tld="com"))

        self.BLUE = "#58C4DD"
        self.GREEN = "#83C167"
        self.YELLOW = "#FFFF66"
        self.ORANGE = "#FFB86C"
        self.RED = "#FF6B6B"
        self.PURPLE = "#9B5DE5"

        self.caption = None
        self.keep = []

    def txt(self, text, size=30, color=WHITE, weight=NORMAL):
        t = Text(text, font_size=size, color=color, weight=weight)
        t.set_z_index(50)
        return t

    def tex(self, text, size=42, color=WHITE):
        m = MathTex(text, font_size=size, color=color)
        m.set_z_index(50)
        return m

    def box(self, mob, color=None, buff=0.22):
        color = color or self.YELLOW
        r = SurroundingRectangle(mob, buff=buff, color=color)
        r.set_fill(BLACK, opacity=0.25)
        r.set_stroke(color, width=2)
        r.set_z_index(40)
        return VGroup(r, mob)

    def formula(self, text, size=42, color=WHITE, stroke=None):
        m = self.tex(text, size=size, color=color)
        if m.width > 11.5:
            m.scale(11.5 / m.width)
        return self.box(m, color=stroke or self.YELLOW)

    def caption_box(self, text):
        band = Rectangle(width=14.5, height=0.75)
        band.to_edge(DOWN, buff=0)
        band.set_fill(BLACK, opacity=0.65)
        band.set_stroke(width=0)
        band.set_z_index(90)

        cap = self.txt(text, size=22, color=WHITE)
        cap.move_to(band.get_center())
        cap.set_z_index(100)

        return VGroup(band, cap)

    def speak(self, narration, *animations, caption=None, min_time=8):
        caption_anims = []

        if caption is not None:
            new_caption = self.caption_box(caption)

            if self.caption is not None:
                caption_anims.append(FadeOut(self.caption, run_time=0.2))

            caption_anims.append(FadeIn(new_caption, run_time=0.3))
        else:
            new_caption = None

        with self.voiceover(text=narration) as tracker:
            total = max(float(tracker.duration), float(min_time))
            all_anims = [*caption_anims, *animations]

            if all_anims:
                play_time = min(max(1.0, total * 0.55), total - 0.2)
                self.play(*all_anims, run_time=play_time)
                rest = total - play_time

                if rest > 0.1:
                    self.wait(rest)
            else:
                if total > 0.1:
                    self.wait(total)

        if new_caption is not None:
            self.caption = new_caption

    def clear(self):
        protected = list(self.keep)

        if self.caption is not None:
            protected.append(self.caption)

        removable = [m for m in self.mobjects if m not in protected]

        if removable:
            self.play(*[FadeOut(m) for m in removable], run_time=0.6)

    def construct(self):
        bg = NumberPlane(
            x_range=[-8, 8, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_width": 1,
                "stroke_opacity": 0.11,
            },
            faded_line_ratio=1,
        )
        bg.set_z_index(-100)

        title = self.txt("Quadratic Formula", size=42, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.22)

        subtitle = self.txt("A visual proof by completing the square", size=24, color=GREY_A)
        subtitle.next_to(title, DOWN, buff=0.08)

        self.add(bg)
        self.play(Write(title), FadeIn(subtitle), run_time=1.5)

        self.keep = [bg, title, subtitle]

        self.intro()
        self.normalize()
        self.split_middle_term()
        self.area_model()
        self.complete_square()
        self.balance()
        self.solve()
        self.graph_meaning()
        self.recap()
        self.outro()

    def intro(self):
        start = self.formula(r"ax^2+bx+c=0", size=52, stroke=self.YELLOW)
        start.move_to(UP * 1.0)

        final = self.formula(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=48,
            stroke=self.GREEN,
        )
        final.next_to(start, DOWN, buff=0.85)

        self.speak(
            "The quadratic formula is often memorized as a mysterious object. "
            "But it is not mysterious. It is what happens when we force a quadratic expression to become a square.",
            FadeIn(start, shift=UP * 0.15),
            caption="We start with the general quadratic equation.",
            min_time=16,
        )

        self.speak(
            "This is the destination. By the end, every part of the formula will have a visual reason: "
            "the negative b, the plus or minus sign, the square root, and the denominator two a.",
            FadeIn(final, shift=UP * 0.15),
            caption="Goal: explain every piece of the formula.",
            min_time=18,
        )

        pieces = VGroup(
            self.tex(r"-b", size=42, color=self.ORANGE),
            self.tex(r"\pm", size=42, color=self.YELLOW),
            self.tex(r"\sqrt{b^2-4ac}", size=42, color=self.GREEN),
            self.tex(r"2a", size=42, color=self.BLUE),
        )
        pieces.arrange(RIGHT, buff=0.75)
        pieces.move_to(DOWN * 2.15)

        labels = VGroup(
            self.txt("shift", size=22, color=self.ORANGE),
            self.txt("two directions", size=22, color=self.YELLOW),
            self.txt("remaining area", size=22, color=self.GREEN),
            self.txt("half-width", size=22, color=self.BLUE),
        )

        for label, piece in zip(labels, pieces):
            label.next_to(piece, DOWN, buff=0.15)

        self.speak(
            "The proof will not jump straight to symbols. First, we will build the geometry. "
            "Then the algebra will simply describe what the picture is doing.",
            FadeIn(pieces),
            FadeIn(labels),
            caption="Geometry first. Formula second.",
            min_time=18,
        )

    def normalize(self):
        self.clear()

        eq1 = self.formula(r"ax^2+bx+c=0", size=46, stroke=self.YELLOW)
        eq2 = self.formula(r"x^2+\frac{b}{a}x+\frac{c}{a}=0", size=44, stroke=self.BLUE)
        eq3 = self.formula(r"x^2+\frac{b}{a}x=-\frac{c}{a}", size=44, stroke=self.ORANGE)

        eq1.move_to(UP * 1.7)
        eq2.move_to(UP * 0.25)
        eq3.move_to(DOWN * 1.2)

        arrow1 = Arrow(eq1.get_bottom(), eq2.get_top(), buff=0.15, color=self.YELLOW)
        arrow2 = Arrow(eq2.get_bottom(), eq3.get_top(), buff=0.15, color=self.YELLOW)

        note1 = self.txt("divide by a", size=24, color=GREY_A)
        note1.next_to(arrow1, RIGHT, buff=0.25)

        note2 = self.txt("move the constant", size=24, color=GREY_A)
        note2.next_to(arrow2, RIGHT, buff=0.25)

        self.speak(
            "First divide every term by a. This makes the x squared coefficient equal to one. "
            "That matters because a square with side x has area x squared.",
            FadeIn(eq1),
            GrowArrow(arrow1),
            FadeIn(note1),
            FadeIn(eq2),
            caption="Step 1: make the x² coefficient equal to 1.",
            min_time=17,
        )

        self.speak(
            "Next move the constant term to the right. Now the left side contains the pieces we want to draw: "
            "one square term and one linear term.",
            GrowArrow(arrow2),
            FadeIn(note2),
            FadeIn(eq3),
            caption="Step 2: leave the x-pieces on the left.",
            min_time=17,
        )

        focus = SurroundingRectangle(eq3, color=self.YELLOW, buff=0.18)
        focus.set_stroke(self.YELLOW, width=4)

        self.speak(
            "From now on, keep your attention on the left side. "
            "The whole trick is to reshape this expression into one perfect square.",
            Create(focus),
            caption="The left side is the object we will reshape.",
            min_time=14,
        )

    def split_middle_term(self):
        self.clear()

        main = self.formula(r"x^2+\frac{b}{a}x", size=50, stroke=self.YELLOW)
        main.move_to(UP * 1.4)

        split = self.formula(
            r"x^2+\frac{b}{2a}x+\frac{b}{2a}x",
            size=44,
            stroke=self.GREEN,
        )
        split.move_to(DOWN * 0.15)

        self.speak(
            "The middle term is the important piece. Instead of keeping b over a times x as one rectangle, "
            "we split it into two equal rectangles.",
            FadeIn(main),
            caption="Split the middle term into two equal halves.",
            min_time=16,
        )

        self.speak(
            "Each half has area b over two a times x. "
            "That number b over two a will become the thickness of the side strips.",
            FadeIn(split, shift=DOWN * 0.15),
            caption="Each half-strip has area (b / 2a)x.",
            min_time=16,
        )

        long_rect = Rectangle(width=5.2, height=0.8)
        long_rect.set_fill(self.GREEN, opacity=0.72)
        long_rect.set_stroke(WHITE, width=2.5)
        long_rect.move_to(DOWN * 2.0)

        cut = DashedLine(long_rect.get_top(), long_rect.get_bottom(), color=self.YELLOW)
        cut.move_to(long_rect.get_center())

        left = long_rect.copy().scale([0.5, 1, 1])
        right = long_rect.copy().scale([0.5, 1, 1])
        left.move_to(long_rect.get_center() + LEFT * 1.3)
        right.move_to(long_rect.get_center() + RIGHT * 1.3)

        l_label = self.tex(r"\frac{b}{2a}x", size=30)
        r_label = self.tex(r"\frac{b}{2a}x", size=30)
        l_label.move_to(left)
        r_label.move_to(right)

        self.speak(
            "Visually, imagine one long green rectangle being cut into two equal green rectangles. "
            "Those two pieces are about to wrap around the blue x squared square.",
            FadeIn(long_rect),
            Create(cut),
            caption="One long rectangle becomes two side strips.",
            min_time=18,
        )

        self.play(FadeOut(cut), Transform(long_rect, VGroup(left, right)), run_time=1.5)
        self.play(FadeIn(l_label), FadeIn(r_label), run_time=0.8)
        self.wait(1)

    def area_model(self):
        self.clear()

        x_side = 2.55
        p_side = 0.85

        x_square = Rectangle(width=x_side, height=x_side)
        x_square.set_fill(self.BLUE, opacity=0.72)
        x_square.set_stroke(WHITE, width=2.5)
        x_square.move_to(LEFT * 2.25 + DOWN * 0.25)

        x_label = self.tex(r"x^2", size=48)
        x_label.move_to(x_square)

        bx1 = Rectangle(width=p_side, height=x_side)
        bx1.set_fill(self.GREEN, opacity=0.75)
        bx1.set_stroke(WHITE, width=2.5)
        bx1.next_to(x_square, RIGHT, buff=0)

        bx2 = Rectangle(width=x_side, height=p_side)
        bx2.set_fill(self.GREEN, opacity=0.75)
        bx2.set_stroke(WHITE, width=2.5)
        bx2.next_to(x_square, UP, buff=0)

        bx1_start = bx1.copy().shift(RIGHT * 1.5)
        bx2_start = bx2.copy().shift(UP * 1.1)

        label1 = self.tex(r"\frac{b}{2a}x", size=30)
        label1.rotate(PI / 2)
        label1.move_to(bx1_start)

        label2 = self.tex(r"\frac{b}{2a}x", size=30)
        label2.move_to(bx2_start)

        brace_x1 = Brace(x_square, DOWN, color=WHITE)
        brace_x1_label = self.tex(r"x", size=32)
        brace_x1_label.next_to(brace_x1, DOWN, buff=0.1)

        brace_x2 = Brace(x_square, LEFT, color=WHITE)
        brace_x2_label = self.tex(r"x", size=32)
        brace_x2_label.next_to(brace_x2, LEFT, buff=0.1)

        self.speak(
            "Now draw x squared as a blue square. Its side length is x, so its area is x squared.",
            FadeIn(x_square, scale=0.9),
            FadeIn(x_label),
            FadeIn(brace_x1),
            FadeIn(brace_x1_label),
            FadeIn(brace_x2),
            FadeIn(brace_x2_label),
            caption="x² is a square with side x.",
            min_time=15,
        )

        self.speak(
            "Bring in the two green half-strips. One attaches to the right side of the square. "
            "The other attaches to the top.",
            FadeIn(bx1_start),
            FadeIn(bx2_start),
            FadeIn(label1),
            FadeIn(label2),
            caption="The two half-strips wrap around the x² square.",
            min_time=17,
        )

        self.speak(
            "Slide them into place. The shape is now almost a bigger square, but notice the missing upper-right corner.",
            Transform(bx1_start, bx1),
            Transform(bx2_start, bx2),
            label1.animate.move_to(bx1),
            label2.animate.move_to(bx2),
            caption="Almost a square — one corner is missing.",
            min_time=16,
        )

        side = VGroup(x_square, bx2)
        side_label = self.tex(r"x+\frac{b}{2a}", size=36, color=self.YELLOW)
        side_label.next_to(side, UP, buff=0.3)

        thickness_brace = Brace(bx1, RIGHT, color=self.YELLOW)
        thickness_label = self.tex(r"\frac{b}{2a}", size=30, color=self.YELLOW)
        thickness_label.next_to(thickness_brace, RIGHT, buff=0.12)

        self.speak(
            "The thickness of each strip is b over two a. "
            "Therefore, the side length of the completed square would be x plus b over two a.",
            FadeIn(side_label),
            FadeIn(thickness_brace),
            FadeIn(thickness_label),
            caption="The completed side length is x + b / 2a.",
            min_time=18,
        )

        self.x_square = x_square
        self.bx1 = bx1_start
        self.bx2 = bx2_start
        self.x_side = x_side
        self.p_side = p_side

    def complete_square(self):
        x_square = self.x_square
        p_side = self.p_side
        x_side = self.x_side

        corner = Rectangle(width=p_side, height=p_side)
        corner.set_fill(self.YELLOW, opacity=0.9)
        corner.set_stroke(WHITE, width=2.5)
        corner.move_to(x_square.get_corner(UR) + RIGHT * p_side / 2 + UP * p_side / 2)

        corner_label = self.tex(r"\left(\frac{b}{2a}\right)^2", size=24, color=BLACK)
        corner_label.move_to(corner)

        ghost = VGroup(corner.copy(), corner_label.copy())
        ghost.set_opacity(0.35)

        self.speak(
            "The missing corner has side length b over two a in both directions. "
            "So its area is b over two a squared.",
            FadeIn(ghost),
            caption="The missing corner is (b / 2a)².",
            min_time=17,
        )

        self.play(FadeOut(ghost), run_time=0.4)

        formula_corner = self.formula(
            r"\text{missing corner}=\left(\frac{b}{2a}\right)^2",
            size=32,
            stroke=self.YELLOW,
        )
        formula_corner.move_to(RIGHT * 2.4 + DOWN * 0.1)

        self.speak(
            "This is the exact term we must add. It is not chosen randomly. "
            "It is the physical missing tile that completes the square.",
            FadeIn(corner, scale=0.9),
            FadeIn(corner_label),
            FadeIn(formula_corner),
            caption="Completing the square means adding the missing tile.",
            min_time=18,
        )

        outline = Square(side_length=x_side + p_side)
        outline.set_fill(BLACK, opacity=0)
        outline.set_stroke(self.YELLOW, width=5)
        outline.move_to(x_square.get_corner(DL) + RIGHT * (x_side + p_side) / 2 + UP * (x_side + p_side) / 2)

        completed = self.formula(
            r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
            r"=\left(x+\frac{b}{2a}\right)^2",
            size=31,
            stroke=self.GREEN,
        )
        completed.move_to(RIGHT * 2.4 + DOWN * 1.55)

        self.speak(
            "Now the entire shape is one square. Its area is the side length squared: "
            "x plus b over two a, all squared.",
            Create(outline),
            FadeIn(completed),
            caption="The left side has become one perfect square.",
            min_time=19,
        )

    def balance(self):
        self.clear()

        original = self.formula(
            r"x^2+\frac{b}{a}x=-\frac{c}{a}",
            size=44,
            stroke=self.YELLOW,
        )
        original.move_to(UP * 1.6)

        balance = Line(LEFT * 4, RIGHT * 4, color=GREY_B)
        balance.move_to(DOWN * 0.4)

        pivot = Triangle()
        pivot.scale(0.45)
        pivot.rotate(PI)
        pivot.set_fill(GREY_D, opacity=0.75)
        pivot.set_stroke(WHITE, width=2)
        pivot.next_to(balance, DOWN, buff=0)

        left_pan = Circle(radius=0.75, color=self.BLUE)
        left_pan.set_fill(self.BLUE, opacity=0.25)
        left_pan.move_to(LEFT * 2.5 + UP * 0.15)

        right_pan = Circle(radius=0.75, color=self.ORANGE)
        right_pan.set_fill(self.ORANGE, opacity=0.25)
        right_pan.move_to(RIGHT * 2.5 + UP * 0.15)

        left_label = self.tex(r"L", size=40)
        right_label = self.tex(r"R", size=40)
        left_label.move_to(left_pan)
        right_label.move_to(right_pan)

        self.speak(
            "But an equation is a balance. If we add the missing square tile to the left side, "
            "we must add exactly the same tile to the right side.",
            FadeIn(original),
            FadeIn(balance),
            FadeIn(pivot),
            FadeIn(left_pan),
            FadeIn(right_pan),
            FadeIn(left_label),
            FadeIn(right_label),
            caption="Whatever we add to one side, we add to the other.",
            min_time=18,
        )

        add_left = self.formula(r"+\left(\frac{b}{2a}\right)^2", size=34, stroke=self.YELLOW)
        add_right = add_left.copy()

        add_left.next_to(left_pan, UP, buff=0.25)
        add_right.next_to(right_pan, UP, buff=0.25)

        self.speak(
            "So we add b over two a squared to both sides. "
            "This is the algebraic version of adding the yellow missing tile.",
            FadeIn(add_left),
            FadeIn(add_right),
            caption="Add the missing corner to both sides.",
            min_time=16,
        )

        new_eq = self.formula(
            r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
            r"=-\frac{c}{a}+\left(\frac{b}{2a}\right)^2",
            size=31,
            stroke=self.GREEN,
        )
        new_eq.move_to(DOWN * 2.25)

        self.speak(
            "Now the left side is ready to be written as a perfect square, "
            "and the equality is still true.",
            FadeIn(new_eq),
            caption="The equation remains balanced.",
            min_time=15,
        )

    def solve(self):
        self.clear()

        eq1 = self.formula(
            r"\left(x+\frac{b}{2a}\right)^2"
            r"=-\frac{c}{a}+\frac{b^2}{4a^2}",
            size=38,
            stroke=self.GREEN,
        )
        eq1.move_to(UP * 1.7)

        eq2 = self.formula(
            r"\left(x+\frac{b}{2a}\right)^2"
            r"=\frac{b^2-4ac}{4a^2}",
            size=40,
            stroke=self.YELLOW,
        )
        eq2.move_to(UP * 0.25)

        self.speak(
            "Now we translate the picture back into algebra. "
            "The left side is one square. The right side must be simplified.",
            FadeIn(eq1),
            caption="The completed square becomes algebra.",
            min_time=16,
        )

        self.speak(
            "Using a common denominator, the right side becomes b squared minus four a c over four a squared. "
            "This is where the expression under the radical is born.",
            FadeIn(eq2),
            caption="The discriminant b² - 4ac appears.",
            min_time=18,
        )

        eq3 = self.formula(
            r"x+\frac{b}{2a}"
            r"=\pm\frac{\sqrt{b^2-4ac}}{2a}",
            size=40,
            stroke=self.ORANGE,
        )
        eq3.move_to(DOWN * 1.15)

        self.speak(
            "Now take the square root of both sides. "
            "The plus or minus sign appears because two opposite numbers can have the same square.",
            FadeIn(eq3),
            caption="Taking a square root creates ±.",
            min_time=18,
        )

        eq4 = self.formula(
            r"x=-\frac{b}{2a}\pm\frac{\sqrt{b^2-4ac}}{2a}",
            size=40,
            stroke=self.BLUE,
        )
        eq4.move_to(DOWN * 2.45)

        self.speak(
            "Finally subtract b over two a from both sides. "
            "This is where the negative b part comes from.",
            FadeIn(eq4),
            caption="Subtract b / 2a to isolate x.",
            min_time=16,
        )

        self.clear()

        final = self.formula(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=52,
            stroke=self.YELLOW,
        )
        final.move_to(UP * 0.2)

        note = self.txt(
            "The formula is not magic.\nIt is the record of completing a square.",
            size=34,
            color=WHITE,
            weight=BOLD,
        )
        note.next_to(final, DOWN, buff=0.6)

        self.speak(
            "Combine the two fractions over the common denominator two a, and the quadratic formula appears. "
            "The formula is not magic. It is the record of completing a square.",
            FadeIn(final),
            FadeIn(note),
            caption="The quadratic formula appears.",
            min_time=20,
        )

    def graph_meaning(self):
        self.clear()

        axes = Axes(
            x_range=[-4.5, 4.5, 1],
            y_range=[-2.5, 5.5, 1],
            x_length=7.2,
            y_length=4.7,
            axis_config={"include_tip": True, "color": GREY_B},
        )
        axes.move_to(DOWN * 0.25)

        graph = axes.plot(
            lambda x: 0.45 * (x + 2.2) * (x - 1.4),
            color=self.BLUE,
            stroke_width=5,
        )

        label = self.formula(r"y=ax^2+bx+c", size=38, stroke=self.BLUE)
        label.to_edge(UP, buff=1.05)

        root1 = Dot(axes.c2p(-2.2, 0), color=self.YELLOW, radius=0.09)
        root2 = Dot(axes.c2p(1.4, 0), color=self.YELLOW, radius=0.09)

        self.speak(
            "There is also a graph meaning. Solving the quadratic equation means finding where the parabola crosses the x-axis.",
            FadeIn(label),
            FadeIn(axes),
            Create(graph),
            caption="Roots are x-axis crossings.",
            min_time=16,
        )

        self.speak(
            "When the expression under the square root is positive, the formula gives two real roots. "
            "On the graph, that means two x-axis crossings.",
            FadeIn(root1, scale=1.4),
            FadeIn(root2, scale=1.4),
            caption="Positive discriminant: two real roots.",
            min_time=17,
        )

        disc = self.formula(r"D=b^2-4ac", size=48, stroke=self.YELLOW)
        disc.move_to(UP * 1.85)

        cases = VGroup(
            self.formula(r"D>0:\ \text{two real roots}", size=30, stroke=self.GREEN),
            self.formula(r"D=0:\ \text{one repeated root}", size=30, stroke=self.YELLOW),
            self.formula(r"D<0:\ \text{no real roots}", size=30, stroke=self.RED),
        )
        cases.arrange(DOWN, buff=0.25)
        cases.to_edge(RIGHT, buff=0.35)
        cases.shift(DOWN * 0.35)

        self.speak(
            "This expression is called the discriminant. It decides whether the square root produces two real roots, "
            "one repeated real root, or no real roots.",
            FadeIn(disc),
            FadeIn(cases),
            caption="The discriminant controls the real roots.",
            min_time=20,
        )

    def recap(self):
        self.clear()

        heading = self.txt("The whole proof in one chain", size=36, color=self.YELLOW, weight=BOLD)
        heading.to_edge(UP, buff=1.05)

        self.speak(
            "Now compress the whole proof into one chain. "
            "This is the part to remember.",
            FadeIn(heading),
            caption="The proof, compressed.",
            min_time=12,
        )

        chain = [
            (
                r"ax^2+bx+c=0",
                "Start from the general quadratic.",
                "Start.",
            ),
            (
                r"x^2+\frac{b}{a}x=-\frac{c}{a}",
                "Divide by a and move the constant.",
                "Prepare the equation.",
            ),
            (
                r"x^2+\frac{b}{a}x+\left(\frac{b}{2a}\right)^2"
                r"=-\frac{c}{a}+\left(\frac{b}{2a}\right)^2",
                "Add the missing corner to both sides.",
                "Complete the square.",
            ),
            (
                r"\left(x+\frac{b}{2a}\right)^2=\frac{b^2-4ac}{4a^2}",
                "Write the left side as one square and simplify the right side.",
                "One square appears.",
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

        for formula_text, narration, cap in chain:
            new_formula = self.formula(formula_text, size=36, stroke=self.YELLOW)
            new_formula.move_to(UP * 0.05)

            if current is None:
                self.speak(
                    narration,
                    FadeIn(new_formula),
                    caption=cap,
                    min_time=11,
                )
            else:
                self.speak(
                    narration,
                    FadeOut(current),
                    FadeIn(new_formula),
                    caption=cap,
                    min_time=11,
                )

            current = new_formula

        final_note = self.txt(
            "Visual idea: add the missing corner.\nAlgebraic result: the quadratic formula.",
            size=34,
            color=WHITE,
            weight=BOLD,
        )
        final_note.move_to(DOWN * 1.85)

        self.speak(
            "The visual idea is simple: add the missing corner. "
            "The algebraic result is the quadratic formula.",
            FadeIn(final_note),
            caption="One visual move creates the whole formula.",
            min_time=17,
        )

    def outro(self):
        self.clear()

        if self.caption is not None:
            self.play(FadeOut(self.caption), run_time=0.3)
            self.caption = None

        final = self.formula(
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            size=54,
            stroke=self.YELLOW,
        )
        final.move_to(UP * 0.4)

        message = self.txt(
            "A quadratic became a square.\nThe square gave the formula.",
            size=36,
            color=WHITE,
            weight=BOLD,
        )
        message.next_to(final, DOWN, buff=0.65)

        self.speak(
            "A quadratic became a square. "
            "The square gave the formula.",
            FadeIn(final),
            FadeIn(message),
            min_time=12,
        )

        self.wait(2)
