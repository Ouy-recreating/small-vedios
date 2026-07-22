from manim import *
import numpy as np

class Dwt(Scene):
    def construct(self):
        # -------------------- 光栅（与原始一致，左移1.5）--------------------
        num_bars = 40
        spacing = 0.075
        bar_width = 0.01
        bar_height = 0.04
        gray_color = GRAY
        total_span = (num_bars - 1) * spacing
        y_start = -total_span / 2

        bars = VGroup()
        for i in range(num_bars):
            y = y_start + i * spacing
            rect = Rectangle(
                width=bar_width,
                height=bar_height,
                fill_color=gray_color,
                fill_opacity=1.0,
                stroke_width=0,
            )
            rect.move_to(ORIGIN + UP * y)
            bars.add(rect)

        bars.shift(LEFT * 1.5)
        self.add(bars)
        self.wait(0.5)

        # -------------------- 入射光束（左端固定，右端向右生长）--------------------
        left_x = -7.0
        right_x = bars.get_center()[0]  # -1.5
        beam_height = total_span * 0.3  # 入射光高度，与梯形短边一致

        # 动态矩形（右端由ValueTracker控制）
        right_tracker_beam = ValueTracker(left_x)

        def get_beam():
            x_right = right_tracker_beam.get_value()
            rect = Polygon(
                [left_x, -beam_height/2, 0],
                [x_right, -beam_height/2, 0],
                [x_right, beam_height/2, 0],
                [left_x, beam_height/2, 0],
                color=WHITE,
                fill_opacity=0.6,
                stroke_width=0,
            )
            return rect

        beam = always_redraw(get_beam)
        self.add(beam)

        # 光束从左向右生长到光栅
        self.play(right_tracker_beam.animate.set_value(right_x), run_time=1.5)
        self.wait(0.3)

        # 将动态矩形转为静态，以便后续整体平移
        beam_static = beam.copy()
        self.remove(beam)
        self.add(beam_static)

        # -------------------- 衍射梯形（独立生长，从左向右出现）--------------------
        # 定义光屏位置（与后续一致）
        screen_x = 3.0  # 绝对坐标，因为光屏位于 RIGHT*4.5 + LEFT*1.5 = 3.0
        new_right_x = screen_x   # 梯形右端停在光屏处
        short_height = beam_height
        long_height = beam_height * 2.8   # 增加扩展幅度

        right_tracker_trap = ValueTracker(right_x)

        def get_trapezoid():
            x_end = right_tracker_trap.get_value()
            if x_end <= right_x:
                return VGroup()
            num_strips = 30
            strip_width = (new_right_x - right_x) / num_strips
            strips = VGroup()
            for i in range(num_strips):
                x1 = right_x + i * strip_width
                if x1 >= x_end:
                    break
                x2 = min(x1 + strip_width, x_end)
                if x2 <= x1:
                    continue
                t1 = (x1 - right_x) / (new_right_x - right_x)
                h1 = short_height + (long_height - short_height) * t1
                t2 = (x2 - right_x) / (new_right_x - right_x)
                h2 = short_height + (long_height - short_height) * t2
                # 透明度从左到右线性递减，右端为0
                alpha = 0.6 * (1 - i / num_strips)
                strip = Polygon(
                    [x1, -h1/2, 0],
                    [x2, -h2/2, 0],
                    [x2, h2/2, 0],
                    [x1, h1/2, 0],
                    color=WHITE,
                    fill_opacity=alpha,
                    stroke_width=0,
                )
                strips.add(strip)
            return strips

        trapezoid = always_redraw(get_trapezoid)
        self.add(trapezoid)

        # 梯形从左向右生长到光屏位置（new_right_x）
        self.play(right_tracker_trap.animate.set_value(new_right_x), run_time=1.5)
        self.wait(0.5)

        # 将动态梯形转为静态
        trapezoid_static = trapezoid.copy()
        self.remove(trapezoid)
        self.add(trapezoid_static)

        # -------------------- 凸透镜（箭头）与光屏 --------------------
        lens_half_height = 3.5
        up_arrow = Arrow(
            start=DOWN*0.25,
            end=UP*lens_half_height,
            color=GRAY,
            stroke_width=3,
            tip_length=0.2,
        )
        down_arrow = Arrow(
            start=UP*0.25,
            end=DOWN*lens_half_height,
            color=GRAY,
            stroke_width=3,
            tip_length=0.2,
        )
        lens_group = VGroup(up_arrow, down_arrow)
        lens_group.move_to(RIGHT * 2 + LEFT * 1.5)    # x = 0.5

        screen_height = 5
        screen = Rectangle(
            width=0.01,
            height=screen_height,
            fill_color=WHITE,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=1,
        )
        screen.move_to(RIGHT * 4.5 + LEFT * 1.5)      # x = 3.0 (与new_right_x一致)

        self.play(Create(up_arrow), Create(down_arrow), Create(screen))
        self.wait(0.5)

        # -------------------- 所有物体（含光束）整体向左平移2.5，停留，再移回--------------------
        all_objects = VGroup(bars, lens_group, screen, beam_static, trapezoid_static)
        self.play(all_objects.animate.shift(LEFT * 2.5), run_time=1)
        self.wait(2)
        self.play(all_objects.animate.shift(RIGHT * 2.5), run_time=1)
        self.wait(1)
        # ----- 过渡到第三段（对齐第三段初始完成状态）-----
        # 第三段完成初始创建后的状态：
        # bars: 缩放1.7，位置 LEFT*4
        # 透镜（箭头）：在原点（x=0）
        # 屏幕：在 RIGHT*4
        # 我们需要将第二段现有的 bars、透镜、屏幕变换到这些位置和缩放

        # 1. 先淡出光束和梯形（它们只在第二段出现）
        self.play(
            FadeOut(beam_static),
            FadeOut(trapezoid_static),
            run_time=1.5
        )

        # 2. 将 bars 缩放并左移，透镜移到原点，屏幕移到 RIGHT*4
        # 注意：第二段中 bars 当前位置是 LEFT*1.5（因为两次平移抵消）
        # 透镜位置是 x=0.5，屏幕位置是 x=3.0
        # 目标：bars 放大1.7并移到 LEFT*4，透镜到原点，屏幕到 RIGHT*4
        self.play(
            bars.animate.scale(1.7).shift(LEFT * 4 - bars.get_center()),  # 因为 bars 中心在 LEFT*1.5，需要额外左移2.5
            lens_group.animate.move_to(ORIGIN),
            screen.animate.move_to(RIGHT * 4),
            run_time=2
        )
        self.wait(0.5)
        # 此时场景中只有 bars（放大左移）、透镜（原点）、屏幕（x=4），与第三段完成初始创建后的状态完全一致