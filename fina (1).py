from manim import *
import numpy as np

class FiveSlits(Scene):
    def construct(self):
        # 物理参数
        m = 0.15
        theta = np.arctan(m)
        f = 2.5
        x_lens = 0.5
        x_screen = x_lens + f
        x_slit = -2.5

        # ---- 分组 ----
        left_rays = VGroup()
        middle_rays = VGroup()
        right_rays = VGroup()

        # ---- 装置：五条缝 ----
        num_slits = 5
        y_slits = np.linspace(-0.6, 0.3, num_slits)   # 缝的中心纵坐标
        half_width = 0.05                             # 缝的半宽度

        # 生成挡板线段（确保光线穿过缝）
        barrier_lines = VGroup()
        bottom_y = -0.8
        first_low = y_slits[0] - half_width
        if first_low > bottom_y:
            barrier_lines.add(Line([x_slit, bottom_y, 0], [x_slit, first_low, 0], stroke_width=4))
        for i in range(num_slits - 1):
            low = y_slits[i] + half_width
            high = y_slits[i+1] - half_width
            if high > low:
                barrier_lines.add(Line([x_slit, low, 0], [x_slit, high, 0], stroke_width=4))
        top_y = 0.5
        last_high = y_slits[-1] + half_width
        if top_y > last_high:
            barrier_lines.add(Line([x_slit, last_high, 0], [x_slit, top_y, 0], stroke_width=4))

        # 透镜和屏幕
        lens = VGroup(
            ArcBetweenPoints([x_lens, -1.6, 0], [x_lens, 1.6, 0], angle=-0.5, stroke_width=4),
            ArcBetweenPoints([x_lens, -1.6, 0], [x_lens, 1.6, 0], angle=0.5, stroke_width=4)
        )
        screen = Line([x_screen, -2.0, 0], [x_screen, 2.0, 0], stroke_width=6, color=BLUE)
        f_arrow = DoubleArrow([x_lens, -1.6, 0], [x_screen, -1.6, 0], stroke_width=3)
        f_label = Text("f", font_size=40).next_to(f_arrow, DOWN, buff=0.15)

        # 角度标注
        dash_line = DashedLine([x_lens, 0, 0], [x_lens + 1.5, 0, 0], stroke_width=2)
        angle_arc = Arc(radius=1, start_angle=0, angle=theta, arc_center=[x_lens, 0, 0])
        theta_label = MathTex(r"\theta", font_size=40).next_to(angle_arc, RIGHT, buff=0.15)
        angle_group = VGroup(dash_line, angle_arc, theta_label)

        device = VGroup(barrier_lines, lens, screen, f_arrow, f_label)

        # ---- 计算垂线 ----
        y_s0 = y_slits[0]
        start_point = np.array([x_slit, 0.5, 0])
        x_intersect0 = x_slit + (0.5 - y_s0) / (m + 1/m)
        y_intersect0 = y_s0 + m * (x_intersect0 - x_slit)
        end_point = np.array([x_intersect0, y_intersect0, 0])
        perp_vec = end_point - start_point
        perp_vec_norm = perp_vec / np.linalg.norm(perp_vec)

        # ---- 生成五条光线 ----
        for i, y_s in enumerate(y_slits):
            color = YELLOW
            width = 4

            start_h = np.array([x_slit - 2.0, y_s, 0])
            end_h = np.array([x_slit, y_s, 0])
            lens_pt = np.array([x_lens, y_s + m*(x_lens - x_slit), 0])
            focus = np.array([x_screen, 2*m, 0])

            p0 = np.array([x_slit, y_s, 0])
            v1 = lens_pt - p0
            v2 = perp_vec_norm
            denom = v1[0]*v2[1] - v1[1]*v2[0]
            if abs(denom) > 1e-9:
                t = ((start_point[0]-p0[0])*v2[1] - (start_point[1]-p0[1])*v2[0]) / denom
                if 0 <= t <= 1:
                    intersect_pt = p0 + t * v1
                else:
                    intersect_pt = lens_pt
            else:
                intersect_pt = lens_pt

            left_rays.add(Line(start_h, end_h, color=color, stroke_width=width))
            middle_rays.add(Line(end_h, intersect_pt, color=color, stroke_width=width))
            right_seg = VMobject()
            right_seg.set_points_as_corners([intersect_pt, lens_pt, focus])
            right_seg.set_color(color).set_stroke(width=width)
            right_rays.add(right_seg)

        # ---- 两条虚线 ----
        slit_dash = DashedLine([x_slit, 0.5, 0], [x_slit, -0.8, 0], stroke_width=2, color=WHITE)
        perp_line = DashedLine(start_point, end_point, stroke_width=3, color=WHITE)

        # ---- 分组 ----
        left_group = left_rays
        middle_group = VGroup(barrier_lines, middle_rays, perp_line)
        right_group = VGroup(lens, screen, f_arrow, f_label, dash_line, angle_arc, theta_label, right_rays)

        # ---- 动画 ----
        self.play(FadeIn(device))
        self.wait(0.5)

        self.play(AnimationGroup(*[Create(obj) for obj in left_rays], lag_ratio=0), run_time=1.5)
        self.play(AnimationGroup(*[Create(obj) for obj in middle_rays], lag_ratio=0), run_time=0.1)
        self.play(AnimationGroup(*[Create(obj) for obj in right_rays], lag_ratio=0), run_time=2.0)
        self.wait(0.5)

        self.play(FadeIn(angle_group))
        self.wait(1)

        self.play(AnimationGroup( Create(perp_line), lag_ratio=0), run_time=1.5)
        self.wait(1.5)

        # ---- 分割动画 ----
        target_pos = np.array([4, 3, 0])
        chayi = Text("光程差", font_size=30).move_to(np.array([-4, 3, 0]))

        self.play(
            left_group.animate.shift(target_pos - left_group.get_center()).set_opacity(0),
            right_group.animate.shift(target_pos - right_group.get_center()).set_opacity(0),
            middle_group.animate.scale(3),
            FadeIn(chayi),
            run_time=2
        )
        self.wait(1)

        # ---- 展示光程差 ----
        line1 = middle_rays[0]
        line2 = middle_rays[1]
        A1 = line1.get_start()
        A2 = line2.get_start()
        d = abs(A2[1] - A1[1])

        d_line = Line(A1, A2, color=BLUE, stroke_width=4)
        d_label = MathTex(r"d", font_size=30).next_to(d_line, LEFT, buff=0.1)

        p0 = np.array([x_slit, y_slits[0], 0])
        lens_pt0 = np.array([x_lens, y_slits[0] + m*(x_lens - x_slit), 0])
        v_dir = lens_pt0 - p0
        v_dir = v_dir / np.linalg.norm(v_dir)
        t = np.dot(A2 - A1, v_dir)
        P = A1 + t * v_dir
        perp_seg = DashedLine(A2, P, color=WHITE, stroke_width=2)

        delta_x = MathTex(r"\Delta x = d\sin\theta", font_size=30)
        delta_x.next_to((A2 + P)/2, RIGHT, buff=0.2)

        self.play(Create(d_line), Write(d_label))
        self.wait(0.5)
        self.play(Create(perp_seg))
        self.wait(0.5)
        self.play(Write(delta_x))
        self.wait(1)

        # ---- 将 Δx 公式移到画面中央，放大 ----
        self.play(
            delta_x.animate.scale(2).move_to(ORIGIN + np.array([0, 1, 0])),
            FadeOut(d_line, d_label, perp_seg, chayi, perp_line, barrier_lines, middle_rays),
            run_time=1.5
        )
        self.wait(0.5)

        # ---- 显示明纹条件 + Δx = kλ 并框起来 ----
        condition_text = Text("明纹条件", font_size=35, color=YELLOW)
        condition_eq = MathTex(r"\Delta x = k\lambda", font_size=35)
        cond_group = VGroup(condition_text, condition_eq).arrange(DOWN, buff=0.3)
        cond_group.next_to(delta_x, UP, buff=0.8)
        box = SurroundingRectangle(cond_group, color=WHITE, buff=0.2)

        self.play(FadeIn(cond_group), Create(box))
        self.wait(0.5)

        # ---- 框和明纹条件消失，Δx = kλ 飞向 delta_x 并替换 ----
        # 创建最终公式，与放大后的 delta_x 同样大小 (delta_x 实际字体大小为 60)
        new_formula = MathTex(r"k\lambda = d\sin\theta", font_size=60)
        new_formula.move_to(delta_x.get_center())

        # 让 condition_eq 飞到 delta_x 的位置（稍偏左，模拟替换 Δx）
        target_pos = delta_x.get_center() + np.array([-delta_x.get_width()/6-0.5, 0, 0])

        self.play(
            FadeOut(box),
            FadeOut(condition_text),
            condition_eq.animate.scale(0.1).move_to(target_pos),  # 缩小并飞向目标
            Transform(delta_x, new_formula),
            run_time=1.5
        )
        # 清除 condition_eq（它已淡出，但可能残留）
        self.remove(condition_eq)
        self.wait(0.5)

        # ---- 下方显示 k = 0, ±1, ±2, ... ----
        k_note = MathTex(r"k = 0, \pm 1, \pm 2, \cdots", font_size=30)
        k_note.next_to(delta_x, DOWN, buff=0.6)
        self.play(Write(k_note))
        self.wait(2)

        # ---- 最终淡出 ----
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)