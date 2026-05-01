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

