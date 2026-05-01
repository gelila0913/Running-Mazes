import glfw
from OpenGL.GL import *
import random
import time

# --- Maze Configuration ---
R, C = 15, 20
CELL_SIZE = 1.8 / max(R, C)

# Data Structures
north_wall = [[1 for _ in range(C)] for _ in range(R)]
east_wall = [[1 for _ in range(C)] for _ in range(R)]
visited = [[0 for _ in range(C)] for _ in range(R)]

# Solver State
path_stack = []
dead_ends = []
solver_finished = False
current_solver_pos = (0, 0)

# We use a tracking stack for the iterative solver to avoid recursion limits
solver_stack = []
visited_solver = [[False for _ in range(C)] for _ in range(R)]

# --- Drawing Helpers ---
def draw_line(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_cell_marker(r, c, color_rgb):
    x = -0.9 + c * CELL_SIZE + (CELL_SIZE / 2.0)
    y = 0.9 - r * CELL_SIZE - (CELL_SIZE / 2.0)

    glColor3f(*color_rgb)
    glPointSize(8.0)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_maze():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)

    for i in range(R):
        for j in range(C):
            x = -0.9 + j * CELL_SIZE
            y = 0.9 - i * CELL_SIZE

            x1, y1 = x, y
            x2, y2 = x + CELL_SIZE, y - CELL_SIZE

            if north_wall[i][j] == 1:
                draw_line(x1, y1, x2, y1)
            if east_wall[i][j] == 1:
                draw_line(x2, y1, x2, y2)
            if i == R - 1:
                draw_line(x1, y2, x2, y2)
            if j == 0:
                draw_line(x1, y1, x1, y2)

   