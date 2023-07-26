import math
import numpy as np
import pygame


def relu(_w):
    return np.maximum(0, _w)


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    div = det(xdiff, ydiff)
    if div == 0:
        return None
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    if min(line1[0][0], line1[1][0]) <= x <= max(line1[0][0], line1[1][0]) and min(line1[0][1], line1[1][1]) <= y <= max(line1[0][1], line1[1][1]) and min(line2[0][0], line2[1][0]) <= x <= max(line2[0][0], line2[1][0]) and min(line2[0][1], line2[1][1]) <= y <= max(line2[0][1], line2[1][1]):
        return x, y
    return None


def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def draw_sensors(win, img, top_left, angle):
    sensors_coordinates = []
    center = img.get_rect(topleft=top_left).center
    while angle < 0:
        angle += 360
    angle += 180
    radians = math.radians(angle)
    x, y = center
    sensor_length = 50
    sensor_length_multiplier = 2
    sensor_x = round(x + sensor_length_multiplier * sensor_length * math.sin(radians))
    sensor_y = round(y + sensor_length_multiplier * sensor_length * math.cos(radians))
    coordinates = sensor_x, sensor_y
    pygame.draw.line(win, "white", center, coordinates)
    sensors_coordinates.append((center, coordinates))
    sensor_length_multiplier = 2

    radians -= math.pi / 8
    for i in range(15):
        sensor_x = round(x + sensor_length_multiplier * sensor_length * math.sin(radians))
        sensor_y = round(y + sensor_length_multiplier * sensor_length * math.cos(radians))
        coordinates = sensor_x, sensor_y
        pygame.draw.line(win, "white", center, coordinates)
        sensors_coordinates.append((center, coordinates))
        radians -= math.pi/8
    return sensors_coordinates


