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

            # Skip drawing the north wall at the entrance (0, 0)
            if i == 0 and j == 0:
                pass # Leave it open
            elif north_wall[i][j] == 1:
                draw_line(x1, y1, x2, y1)
                
            if east_wall[i][j] == 1:
                draw_line(x2, y1, x2, y2)
                
            # Skip drawing the bottom wall at the exit (R-1, C-1) to make it an opening
            if i == R - 1 and j == C - 1:
                pass # Leave the bottom exit open
            elif i == R - 1:
                draw_line(x1, y2, x2, y2)
                
            if j == 0:
                draw_line(x1, y1, x1, y2)

    # Draw markers
    for (r, c) in path_stack:
        draw_cell_marker(r, c, (1.0, 0.0, 0.0))
    for (r, c) in dead_ends:
        draw_cell_marker(r, c, (0.0, 0.5, 1.0))
        
    draw_cell_marker(current_solver_pos[0], current_solver_pos[1], (1.0, 1.0, 0.0))

# --- Maze Generation ---
def generate_maze():
    stack = []
    start_c = random.randint(0, C - 1)
    start_r = random.randint(0, R - 1)

    visited[start_r][start_c] = 1
    stack.append((start_r, start_c))

    while len(stack) > 0:
        current = stack[-1]
        r, c = current[0], current[1]

        candidates = []
        if r > 0 and visited[r - 1][c] == 0: candidates.append((r - 1, c))
        if r < R - 1 and visited[r + 1][c] == 0: candidates.append((r + 1, c))
        if c > 0 and visited[r][c - 1] == 0: candidates.append((r, c - 1))
        if c < C - 1 and visited[r][c + 1] == 0: candidates.append((r, c + 1))

        if len(candidates) > 0:
            next_cell = random.choice(candidates)
            nr, nc = next_cell[0], next_cell[1]

            if nr < r: north_wall[r][c] = 0
            elif nr > r: north_wall[nr][nc] = 0
            elif nc < c: east_wall[r][c - 1] = 0
            elif nc > c: east_wall[r][c] = 0

            visited[nr][nc] = 1
            stack.append(next_cell)
        else:
            stack.pop()

# --- Iterative Solver Step ---
def solve_maze_step(end_r, end_c):
    global solver_stack, path_stack, dead_ends, current_solver_pos, solver_finished

    if solver_finished or not solver_stack:
        return

    current_pos = solver_stack[-1]
    r, c = current_pos
    current_solver_pos = (r, c)

    if r == end_r and c == end_c:
        path_stack.append((r, c))
        solver_finished = True
        return

    # If this is the first time evaluating the cell
    if not visited_solver[r][c]:
        visited_solver[r][c] = True
        path_stack.append((r, c))

    # Determine next possible candidates
    dr = [-1, 1, 0, 0]
    dc = [0, 0, 1, -1]
    
    moved = False
    for i in range(4):
        nr, nc = r + dr[i], c + dc[i]

        if 0 <= nr < R and 0 <= nc < C:
            wall_exists = False
            
            if dr[i] == -1 and north_wall[r][c] == 1: wall_exists = True
            elif dr[i] == 1 and north_wall[nr][nc] == 1: wall_exists = True
            elif dc[i] == 1 and east_wall[r][c] == 1: wall_exists = True
            elif dc[i] == -1 and east_wall[r][c - 1] == 1: wall_exists = True

            if not wall_exists and not visited_solver[nr][nc]:
                # Temporarily wall off to avoid loops
                north_wall[r][c] = 1
                solver_stack.append((nr, nc))
                moved = True
                break
                
    if not moved:
        # Backtrack if dead-end is reached
        dead_ends.append(path_stack.pop())
        solver_stack.pop()

# --- Main Program ---
def main():
    global solver_stack
    
    if not glfw.init():
        return

    window = glfw.create_window(800, 650, "PyOpenGL Maze Generator", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    generate_maze()
    
    start_r, start_c = 0, 0
    end_r, end_c = R - 1, C - 1
    
    # Initialize the non-recursive stack
    solver_stack.append((start_r, start_c))

    while not glfw.window_should_close(window):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        draw_maze()

        solve_maze_step(end_r, end_c)
        time.sleep(0.02) # To control frame step interval

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()