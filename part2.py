from manim import *
import numpy as np

def create_triangle(point, angle, side=0.15):
    """创建等边三角形，中心在 point，指向 angle（弧度），边长为 side"""
    r = side / np.sqrt(3)
    v1 = np.array([r, 0, 0])
    v2 = np.array([-r/2, side/2, 0])
    v3 = np.array([-r/2, -side/2, 0])
    tri = Polygon(v1, v2, v3, color=WHITE, fill_opacity=1, stroke_width=0)
    tri.rotate(angle, about_point=ORIGIN)
    tri.shift(point)
    return tri

class Irs(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # 光栅参数
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

        self.add(bars)
        self.play(bars.animate.scale(1.7).shift(LEFT * 4))
        self.wait(0.5)

        # -------------------- 凸透镜（箭头）--------------------
        lens_half_height = 3.5
        up_arrow = Arrow(
            start=DOWN * 0.25,
            end=UP * lens_half_height,
            color=GRAY,
            stroke_width=3,
            tip_length=0.2,
        )
        down_arrow = Arrow(
            start=UP * 0.25,
            end=DOWN * lens_half_height,
            color=GRAY,
            stroke_width=3,
            tip_length=0.2,
        )
        self.play(Create(up_arrow), Create(down_arrow))

        # -------------------- 光屏 --------------------
        screen_height = 5
        screen_width = 0.01
        screen = Rectangle(
            width=screen_width,
            height=screen_height,
            fill_color=WHITE,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=1,
        )
        screen.move_to(RIGHT * 4)
        self.play(Create(screen), run_time=1)
        self.wait(0.5)

        # -------------------- 光线系统（分段射入，三角形随光线到达中点时显现）--------------------
        heights = [0, 0.5, 1, 1.5, 2, -0.5, -1, -1.5, -2]

        x_left = -7.5
        x_g = -4
        x_l = 0
        x_s = 4
        f = x_s

        # 三个进度追踪器
        len_left = ValueTracker(0)
        len_mid = ValueTracker(0)
        len_right = ValueTracker(0)
        # 初始角度为水平（0°）
        theta_tracker = ValueTracker(0)

        def get_dynamic_rays():
            group = VGroup()
            theta = theta_tracker.get_value()
            tan_theta = np.tan(theta)
            l_l = len_left.get_value()
            l_m = len_mid.get_value()
            l_r = len_right.get_value()

            for y in heights:
                # ---- 左侧段 ----
                left_start = np.array([x_left, y, 0])
                left_end_full = np.array([x_g, y, 0])
                left_end = left_start + l_l * (left_end_full - left_start)
                left_line = Line(left_start, left_end, stroke_width=1, color=WHITE)
                group.add(left_line)

                # 左侧段固定中点
                left_mid = (left_start + left_end_full) / 2
                if l_l >= 0.5:
                    tri = create_triangle(left_mid, 0, 0.075)  # 始终水平向右
                    group.add(tri)

                # ---- 中间段 ----
                y_lens = y - x_g * tan_theta
                mid_start = np.array([x_g, y, 0])
                mid_end_full = np.array([x_l, y_lens, 0])
                mid_end = mid_start + l_m * (mid_end_full - mid_start)
                mid_line = Line(mid_start, mid_end, stroke_width=1, color=WHITE)
                group.add(mid_line)

                mid_mid = (mid_start + mid_end_full) / 2
                if l_m >= 0.5:
                    # 中间段方向角等于当前 theta
                    tri = create_triangle(mid_mid, theta, 0.075)
                    group.add(tri)

                # ---- 右侧段 ----
                y_focus = f * tan_theta
                r_start = np.array([x_l, y_lens, 0])
                r_end_full = np.array([x_s, y_focus, 0])
                r_end = r_start + l_r * (r_end_full - r_start)
                r_line = Line(r_start, r_end, stroke_width=1, color=WHITE)
                group.add(r_line)

                # 右侧段方向角（基于完整终点）
                dx_full = r_end_full[0] - r_start[0]
                dy_full = r_end_full[1] - r_start[1]
                r_angle = np.arctan2(dy_full, dx_full) if np.linalg.norm([dx_full, dy_full]) > 1e-6 else 0
                r_mid = (r_start + r_end_full) / 2
                if l_r >= 0.5:
                    tri = create_triangle(r_mid, r_angle, 0.075)
                    group.add(tri)

            return group

        dynamic_rays = always_redraw(get_dynamic_rays)
        self.add(dynamic_rays)

        # ---------- 分段射入动画 ----------
        self.play(len_left.animate.set_value(1), run_time=1.5)
        self.play(len_mid.animate.set_value(1), run_time=1.5)
        self.play(len_right.animate.set_value(1), run_time=1.5)
        self.wait(1)   # 初始水平状态

        # ---------- 角度变化序列 ----------
        # 1. 向上 15°
        self.play(theta_tracker.animate.set_value(np.radians(15)), run_time=1)
        self.wait(1)

        # 2. 回到水平
        self.play(theta_tracker.animate.set_value(0), run_time=1)
        self.wait(1)

        # 3. 向下 15°
        self.play(theta_tracker.animate.set_value(np.radians(-15)), run_time=1)
        self.wait(1)

        # 4. 回到水平
        self.play(theta_tracker.animate.set_value(0), run_time=1)
        self.wait(2)
        # ----- 过渡到第四段 -----
        # 第四段参数
        m = 0.15
        f_val = 2.5
        x_lens4 = 0.5
        x_screen4 = x_lens4 + f_val
        x_slit = -2.5

        num_slits = 5
        y_slits = np.linspace(-0.6, 0.3, num_slits)
        half_width = 0.05

        # 1. 挡板
        barrier_lines = VGroup()
        bottom_y = -0.8
        first_low = y_slits[0] - half_width
        if first_low > bottom_y:
            barrier_lines.add(Line([x_slit, bottom_y, 0], [x_slit, first_low, 0], stroke_width=4))
        for i in range(num_slits - 1):
            low = y_slits[i] + half_width
            high = y_slits[i + 1] - half_width
            if high > low:
                barrier_lines.add(Line([x_slit, low, 0], [x_slit, high, 0], stroke_width=4))
        top_y = 0.5
        last_high = y_slits[-1] + half_width
        if top_y > last_high:
            barrier_lines.add(Line([x_slit, last_high, 0], [x_slit, top_y, 0], stroke_width=4))

        # 2. 透镜弧线
        lens4 = VGroup(
            ArcBetweenPoints([x_lens4, -1.6, 0], [x_lens4, 1.6, 0], angle=-0.5, stroke_width=4),
            ArcBetweenPoints([x_lens4, -1.6, 0], [x_lens4, 1.6, 0], angle=0.5, stroke_width=4)
        )

        # 3. 屏幕竖线
        screen4 = Line([x_screen4, -2.0, 0], [x_screen4, 2.0, 0], stroke_width=6, color=BLUE)

        # 4. f 箭头与标签
        f_arrow = DoubleArrow([x_lens4, -1.6, 0], [x_screen4, -1.6, 0], stroke_width=3)
        f_label = Text("f", font_size=40).next_to(f_arrow, DOWN, buff=0.15)

        # 5. 角度标注
        dash_line = DashedLine([x_lens4, 0, 0], [x_lens4 + 1.5, 0, 0], stroke_width=2)
        theta_val = np.arctan(m)
        angle_arc = Arc(radius=1, start_angle=0, angle=theta_val, arc_center=[x_lens4, 0, 0])
        theta_label = MathTex(r"\theta", font_size=40).next_to(angle_arc, RIGHT, buff=0.15)
        angle_group = VGroup(dash_line, angle_arc, theta_label)

        # 执行变换：将 bars 变挡板，两个箭头变两条弧线，screen 变竖线，淡出动态光线，淡入新元素
        self.play(
            Transform(bars, barrier_lines),
            Transform(up_arrow, lens4[0]),
            Transform(down_arrow, lens4[1]),
            Transform(screen, screen4),
            FadeIn(f_arrow),
            FadeIn(f_label),
         #   FadeIn(angle_group),
            FadeOut(dynamic_rays),
            run_time=2
        )
        self.wait(0.5)
        # 场景中已有 barrier_lines, lens4（由两个箭头变来）, screen4, f_arrow, f_label, angle_group
        # 与第四段开头完全一致（第四段会重新创建 device 并 FadeIn，但我们可以直接在下一段跳过 device 的创建）