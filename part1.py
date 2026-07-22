from manim import *
import numpy as np

class Dgz(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=90 * DEGREES, theta=-90 * DEGREES)

        laser_dist = 3.5
        theta_10_initial = 150 * DEGREES
        outward = np.array([np.cos(theta_10_initial), np.sin(theta_10_initial), 0])
        laser_dir = -outward
        laser_pos = laser_dist * outward

        grating_center = np.array([0.0, 0.0, 0.0])
        grating_thick = 0.001
        grating_width = 0.3
        grating_height = 0.5

        # ----- 创建衍射光栅（只有条纹）-----
        n_lines = 40
        line_thick = 0.004
        stripe_spacing = grating_width / n_lines
        stripes = VGroup()
        for i in range(n_lines):
            z_pos = -grating_width/2 + (i + 0.5) * stripe_spacing
            stripe = Cube(side_length=1, fill_color=GRAY, fill_opacity=0.6, stroke_width=0)
            stripe.scale([grating_thick * 1.5, grating_height, line_thick])
            stripe.rotate(angle_between(RIGHT, laser_dir), axis=rotate_axis(RIGHT, laser_dir))
            stripe.shift(z_pos * (np.cross(laser_dir, UP) / np.linalg.norm(np.cross(laser_dir, UP))))
            for part in stripe.family_members_with_points():
                part.set_fill(GRAY, opacity=1)
                part.set_stroke(width=0)
            stripes.add(stripe)

        grating = VGroup(stripes)

        # ----- 将光栅旋转到侧视图（条纹排列方向指向 X 轴），并放大10倍 -----
        grating.rotate(120 * DEGREES, axis=OUT)
        grating.scale(10, about_point=ORIGIN)

        # 显示光栅
        self.add(grating)
        self.wait(1)

        # 绕Z轴（OUT）逆时针旋转90°
        self.play(grating.animate.rotate(90 * DEGREES, axis=OUT), run_time=2)
        self.wait(2)

        # ----- 投影到 y=0 平面，过渡到 2D 场景 -----
        projected = grating.copy()
        projected.apply_function(lambda p: np.array([p[0], 0, p[2]]))
        self.play(Transform(grating, projected), run_time=2)
        self.wait(2)
        self.play(FadeOut(grating), run_time=1.5)
        self.wait(0.5)



def angle_between(v1, v2):
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))


def rotate_axis(v1, v2):
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    if np.allclose(v1, v2):
        return OUT
    if np.allclose(v1, -v2):
        return RIGHT
    axis = np.cross(v1, v2)
    return axis / np.linalg.norm(axis)
