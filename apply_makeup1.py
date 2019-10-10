import itertools
import scipy.interpolate
import cv2
import numpy as np
from skimage import color


class ApplyMakeup():
    """
    Class that handles application of color, and performs blending on the image.

    Functions available for use:
        1. apply_lipstick: Applies lipstick of desired colour on passed image of face.
        2. apply_liner: Applies black eyeliner on passed image of face.
    """

    def __init__(self, points):

        #(25, 25, 25) -> very dark grey
        #(0, 0, 0) -> black

        self.points = points
        self.alpha = 0.5
        self.height = 0
        self.width = 0
        self.red_e = 0
        self.green_e = 0
        self.blue_e = 0
        self.red_l = 0
        self.green_l = 0
        self.blue_l = 0
        self.image = 0
        self.copy = 0
        self.lip_x = []
        self.lip_y = []
        self.indices = {"left eye": [36, 37, 38, 39] ,"right eye": [42, 43, 44, 45] ,"upper lip u": [48, 49, 50, 51, 52, 53, 54] ,"upper lip b": [60, 61, 62, 63, 64] , "lower lip u": [60, 67, 66, 65, 64] ,"lower lip b": [48, 59, 58, 57, 56, 55, 54]}


    def draw_curve(self, kind):
        curvex=[]
        curvey=[]
        lip_xx=[]
        lip_yy=[]
        for i in self.indices[kind]:
            (x,y)=self.points[i]
            lip_xx.append(x)
            lip_yy.append(y)
        curve = scipy.interpolate.interp1d(lip_xx, lip_yy, 'cubic')
        for i in np.arange(lip_xx[0], lip_xx[len(lip_xx) - 1] + 1, 1):
            curvex.append(i)
            curvey.append(int(curve(i)))
        return curvex, curvey


    def fill_lip_line(self, outer, inner):
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        count = len(inner[0]) - 1
        last_inner = [inner[0][count], inner[1][count]]
        for o_point, i_point in itertools.zip_longest(
                outer_curve, inner_curve, fillvalue=last_inner
            ):
            line = scipy.interpolate.interp1d(
                [o_point[0], i_point[0]], [o_point[1], i_point[1]], 'linear')
            xpoints = list(np.arange(o_point[0], i_point[0], 1))
            self.lip_x.extend(xpoints)
            self.lip_y.extend([int(point) for point in line(xpoints)])
        return


    def fill_lip_solid(self, outer, inner):
        inner[0].reverse()
        inner[1].reverse()
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        points = []
        for point in outer_curve:
            points.append(np.array(point, dtype=np.int32))
        for point in inner_curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_l = int(self.red_l)
        self.green_l = int(self.green_l)
        self.blue_l = int(self.blue_l)
        cv2.fillPoly(self.image, [points], (self.red_l, self.green_l, self.blue_l))


    def fill_color(self, uol_c, uil_c, lol_c, lil_c):
        self.fill_lip_line(uol_c, uil_c)
        self.fill_lip_line(lol_c, lil_c)
        self.fill_lip_solid(uol_c, uil_c)
        self.fill_lip_solid(lol_c, lil_c)


    def __get_curves_lips(self, uol, uil, lol, lil):
        uol_curve = self.draw_curve(uol)
        uil_curve = self.draw_curve(uil)
        lol_curve = self.draw_curve(lol)
        lil_curve = self.draw_curve(lil)
        return uol_curve, uil_curve, lol_curve, lil_curve


    def apply_lipstick(self, image, blips, glips, rlips):
        self.red_l = rlips
        self.green_l = glips
        self.blue_l = blips
        self.image = image
        self.height, self.width = self.image.shape[:2]
        lips=[]
        self.copy=self.image.copy()
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        curve_uu, curve_ub, curve_lu, curve_lb = self.__get_curves_lips("upper lip u", "upper lip b", "lower lip b", "lower lip u")
        self.fill_color(curve_uu, curve_ub, curve_lb, curve_lu)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        cv2.addWeighted(self.image, self.alpha, self.copy, 1 - self.alpha, 0, self.copy)
        return self.copy


    def draw_liner(self, type):
        eye_x=[]
        eye_y=[]
        x_points=[]
        y_points=[]

        if type=="right":
            xx="right eye"
        else:
            xx="left eye"

        for i in self.indices[xx]:
            (x,y)=self.points[i]
            x_points.append(x)
            y_points.append(y)
        curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
        for point in np.arange(x_points[0], x_points[len(x_points) - 1] + 1, 1):
            eye_x.append(point)
            eye_y.append(int(curve(point)))

        if type=="left":
            y_points[0] -= 1
            y_points[1] -= 1
            y_points[2] -= 1
            x_points[0] -= 5
            x_points[1] -= 1
            x_points[2] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 2)
                else:
                    eye_y.append(int(curve(point)) - 3)
        else:
            x_points[3] += 5
            x_points[2] += 1
            x_points[1] += 1
            y_points[3] -= 1
            y_points[2] -= 1
            y_points[1] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 2)
                elif count:
                    eye_y.append(int(curve(point)) - 3)
        curve = zip(eye_x, eye_y)
        points = []
        for point in curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_e = 25
        self.green_e = 25
        self.blue_e = 25
        cv2.fillPoly(self.image, [points], (self.red_e, self.green_e, self.blue_e))
        return


    def apply_liner(self, image):
        self.image=image
        self.copy=self.image.copy()
        self.draw_liner("left")
        self.draw_liner("right")
        cv2.addWeighted(self.image, self.alpha, self.copy, 1 - self.alpha, 0, self.copy)
        return self.copy
