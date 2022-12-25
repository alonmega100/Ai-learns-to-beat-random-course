import numpy
import pygame
import numpy as np
import math
import pandas as pd
from utils import *
import settings


class AbstractCar:
    def __init__(self, _max_vel, _rotation_vel, _wi=None, _bi=None, _w1=None, _b1=None):
        self.img = self.IMG
        self.max_vel = _max_vel
        self.vel = 1
        self.rotation_vel = _rotation_vel
        self.angle = 90
        self.x, self.y = settings.STARTING_POSITION
        self.acceleration = 0.1
        self.score = 0
        self.rounds_completed = 0
        self.index_of_bonus_line = 0
        self.next_bonus_line = settings.BONUS_LINES[self.index_of_bonus_line]
        # print(self.next_bonus_line, "my first bonus line")
        self.sensors = []
        self.points_sensor = []

    def rotate(self, _left=False, _right=False):
        if _left:
            self.angle += self.rotation_vel
        elif _right:
            self.angle -= self.rotation_vel

    def draw(self, _win):
        blit_rotate_center(_win, self.img, (self.x, self.y), self.angle)
        self.sensors = draw_sensors(_win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration*0.5, 0)

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self):
        car_rect = self.img.get_rect(x=self.x, y=self.y)
        for line in settings.TRACK_LINES:
            if car_rect.clipline(line):
                return True
        return False

    def sense(self):
        points = []
        distances = []
        self.sensors = [self.sensors[0], self.sensors[1], self.sensors[2], self.sensors[-1], self.sensors[-2]]
        for sensor in self.sensors:
            sensed_point = None
            shortest_point = None
            for track_line in settings.TRACK_LINES:

                (x1, y1), (x2, y2) = track_line
                (x3, y3), (x4, y4) = sensor
                x1 = int(round(x1))
                x2 = int(round(x2))
                x3 = int(round(x3))
                x4 = int(round(x4))
                y1 = int(round(y1))
                y2 = int(round(y2))
                y3 = int(round(y3))
                y4 = int(round(y4))
                if (max(x1, x2) < min(x3, x4)) or (min(x1, x2) > max(x3, x4)) \
                        or (max(y1, y2) < min(y3, y4)) or (min(y1, y2) > max(y3, y4)):
                    pass
                else:
                    if x1 == x2 and x3 == x4:
                        pass

                    elif x1 == x2:

                        y = int(((y4 - y3) / (x4 - x3)) * (x1 - x3) + y3)
                        if min(y1, y2) <= y <= max(y1, y2):
                            dist = math.sqrt((x1 - x3) ** 2 + (y - y3) ** 2)
                            if shortest_point is None or shortest_point > dist:
                                shortest_point = dist
                                sensed_point = ((255, 255, 0), (x1, y), 5)
                    elif x3 == x4:
                        y = int(((y2 - y1) / (x2 - x1)) * (x3 - x1) + y1)
                        if min(y3, y4) <= y <= max(y3, y4):
                            dist = math.sqrt((x3 - x3) ** 2 + (y3 - y) ** 2)
                            if shortest_point is None or shortest_point > dist:
                                shortest_point = dist
                                sensed_point = ((255, 0, 0), (x3, y), 5)
                    else:
                        b1 = ((y2 - y1) / (x2 - x1))
                        b2 = ((y4 - y3) / (x4 - x3))
                        if b1 != b2:
                            x = ((b2 * x3 - b1 * x1 + y1 - y3) / (b2 - b1))
                            y = (y1 + b1 * (x - x1))
                            if min(y3, y4) <= y <= max(y3, y4) and min(x3, x4) <= x <= max(x3, x4) \
                                    and min(x1, x2) <= x <= max(x1, x2):
                                dist = math.sqrt((x - x3) ** 2 + (y - y3) ** 2)
                                if shortest_point is None or shortest_point > dist:
                                    shortest_point = dist
                                    sensed_point = ((0, 255, 0), (x, y), 5)
            if sensed_point is not None and shortest_point is not None:
                points.append(sensed_point)
                distances.append(shortest_point)
            else:
                points.append(None)
                distances.append(400)

        self.points_sensor = points
        return distances

    def get_distance_from_next_bonus_line(self):
        point_a, point_b = self.next_bonus_line
        point_a_x, point_a_y = point_a
        point_b_x, point_b_y = point_b
        dist_from_a = math.hypot(point_a_x - self.x, point_a_y - self.y)
        dist_from_b = math.hypot(point_b_x - self.x, point_b_y - self.y)
        return dist_from_a, dist_from_b

    def update_input_layer(self):
        input_layer = self.sense()
        input_layer.append(self.vel)
        distances_from_next_bonus_line = self.get_distance_from_next_bonus_line()

        input_layer+=[*distances_from_next_bonus_line]
        self.input_layer = input_layer

    def reset(self):
        self.x, self.y = settings.STARTING_POSITION
        self.angle = 0
        self.vel = 0
        self.index_of_bonus_line = 0
        self.next_bonus_line = settings.BONUS_LINES[0]
        self.score = 0

    def print_input_layer(self):
        print("input layer:", self.input_layer)

    def take_action(self, output_layer):
        decided_action = np.argmax(output_layer)
        if decided_action == 0:
            self.move_forward()

        elif decided_action == 1:
            self.rotate(_right=True)

        elif decided_action == 2:
            self.rotate(_left=True)

        elif decided_action == 3:
            self.move_backward()

    def update_score(self, _score):
        self.score += _score


class PlayerCar(AbstractCar):

    IMG = settings.RED_CAR

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration * 0.1, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def crash(self):
        self.score -= 500

