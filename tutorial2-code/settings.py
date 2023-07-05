from utils import *


TRACK_LINES = []

FRAMES_PER_BONUS_LINE = 40
BONUS_LINES = []
STARTING_POSITION = (0, 0)
MAX_VEL = 7
ROTATION_VEL = 15
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.3)


WIN_SHAPE = (1000, 1000)  # This is the default value - the program changes it once main.py runs


pygame.display.set_caption("Racing Game!")

FPS = 60

