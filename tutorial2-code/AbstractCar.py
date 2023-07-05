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
        """
        Rotates the car
        :param _left:
        :param _right:
        :return:
        """
        if _left:
            self.angle += self.rotation_vel
        elif _right:
            self.angle -= self.rotation_vel

    def draw(self, _win):
        """
        Draws the car and its sensors. Used by the draw function.
        :param _win:
        :return:
        """
        blit_rotate_center(_win, self.img, (self.x, self.y), self.angle)
        self.sensors = draw_sensors(_win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        """
        Updates the vel of the car.
        :return:
        """
        self.vel = min(self.vel + self.acceleration, self.max_vel)

    def move_backward(self):
        """
        Updates the vel of the car.
        :return:
        """
        self.vel = max(self.vel - self.acceleration*0.5, 0)

    def move(self):
        """
        Updates the location of the car. Called every frame.
        :return:
        """
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self):
        """
        Checks if the car hits a track line.
        :return:
        """
        car_rect = self.img.get_rect(x=self.x, y=self.y)
        for line in settings.TRACK_LINES:
            if car_rect.clipline(line):
                return True
        return False

    def sense(self):
        """
        Checks the distances between the sensors and the surrounding walls.
        :return: The distances sensed and updates the points sensed.
        """
        points = []
        distances = []
        self.sensors = [self.sensors[0], self.sensors[1], self.sensors[2], self.sensors[-1], self.sensors[-2]]
        for sensor in self.sensors:
            point_coordinate = None
            shortest_dist = None
            for track_line in settings.TRACK_LINES:
                temp = intersection(sensor, track_line)
                if temp is not None:
                    x1, y1 = sensor[0]
                    x2, y2 = temp
                    dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                    if shortest_dist is None or dist < shortest_dist:
                        shortest_dist = dist
                        point_coordinate = temp
            if point_coordinate is not None and shortest_dist is not None:
                points.append(((255, 0, 0), point_coordinate, 5))
                distances.append(shortest_dist)
            else:
                points.append(None)
                distances.append(400)

        self.points_sensor = points
        return distances

    def get_distance_from_next_bonus_line(self):
        """
        :return: The distances from the next bonus line
        """
        point_a, point_b = self.next_bonus_line
        point_a_x, point_a_y = point_a
        point_b_x, point_b_y = point_b
        dist_from_a = math.hypot(point_a_x - self.x, point_a_y - self.y)
        dist_from_b = math.hypot(point_b_x - self.x, point_b_y - self.y)
        return dist_from_a, dist_from_b

    def update_input_layer(self):
        """
        Updates the input layer attribute of the car for NEAT.
        :return:
        """
        input_layer = self.sense()
        input_layer.append(self.vel)
        distances_from_next_bonus_line = self.get_distance_from_next_bonus_line()

        input_layer+=[*distances_from_next_bonus_line]
        self.input_layer = input_layer

    def print_input_layer(self):
        print("input layer:", self.input_layer)

    def take_action(self, output_layer):
        """
        Decides what action to take based on the NEAT feed forward function.
        :param output_layer: NEATs output
        :return: Nothing.
        """
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

