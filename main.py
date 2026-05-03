
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import time

# --- 1. Maze Configuration ---
R, C = 12, 16  # Slightly smaller for better 3D performance
WALL_HEIGHT = 0.5
CELL_SIZE = 1.0

north_wall = [[1 for _ in range(C)] for _ in range(R)]
east_wall = [[1 for _ in range(C)] for _ in range(R)]
left_wall = [1 for _ in range(R)]

PHASE = "GENERATING"
gen_stack = []
gen_visited = [[0 for _ in range(C)] for _ in range(R)]

# Openings
start_r, end_r = random.randint(0, R-1), random.randint(0, R-1)
start_node, end_node = (start_r, 0), (end_r, C-1)
left_wall[start_r] = 0
east_wall[end_r][C-1] = 0

solver_stack, path_stack, dead_ends = [start_node], [], []
visited_solver = [[False for _ in range(C)] for _ in range(R)]
current_pos = (start_r, 0)

# --- 2. 3D Drawing Helpers ---

def draw_cube(x, y, z, sx, sy, sz, color):
    """Draws a 3D block at x,y,z with scale sx,sy,sz"""
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    
    glBegin(GL_QUADS)
    # Top
    glVertex3f(1,1,-1); glVertex3f(-1,1,-1); glVertex3f(-1,1,1); glVertex3f(1,1,1)
    # Bottom
    glVertex3f(1,-1,1); glVertex3f(-1,-1,1); glVertex3f(-1,-1,-1); glVertex3f(1,-1,-1)
    # Front
    glVertex3f(1,1,1); glVertex3f(-1,1,1); glVertex3f(-1,-1,1); glVertex3f(1,-1,1)
    # Back
    glVertex3f(1,-1,-1); glVertex3f(-1,-1,-1); glVertex3f(-1,1,-1); glVertex3f(1,1,-1)
    # Left
    glVertex3f(-1,1,1); glVertex3f(-1,1,-1); glVertex3f(-1,-1,-1); glVertex3f(-1,-1,1)
    # Right
    glVertex3f(1,1,-1); glVertex3f(1,1,1); glVertex3f(1,-1,1); glVertex3f(1,-1,-1)
    glEnd()
    glPopMatrix()

def draw_maze_3d():
    """Renders the 2D wall data as 3D blocks"""
    offset_x = -(C * CELL_SIZE) / 2
    offset_z = -(R * CELL_SIZE) / 2

    for r in range(R):
        for c in range(C):
            x = offset_x + c * CELL_SIZE
            z = offset_z + r * CELL_SIZE
            
            # North Walls
            if north_wall[r][c]:
                draw_cube(x + CELL_SIZE/2, WALL_HEIGHT/2, z, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.7, 0.7, 0.7))
            # East Walls
            if east_wall[r][c]:
                draw_cube(x + CELL_SIZE, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.6, 0.6, 0.6))
            # Left boundary
            if c == 0 and left_wall[r]:
                draw_cube(x, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.6, 0.6, 0.6))
            # Bottom boundary
            if r == R-1:
                draw_cube(x + CELL_SIZE/2, WALL_HEIGHT/2, z + CELL_SIZE, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.7, 0.7, 0.7))
    
    # Floor
    draw_cube(0, -0.05, 0, (C*CELL_SIZE)/2, 0.01, (R*CELL_SIZE)/2, (0.2, 0.2, 0.2))

# --- 3. Logic Functions (Same as 2D) ---
def generate_step():
    global PHASE
    if not gen_stack: PHASE = "SOLVING"; return
    r, c = gen_stack[-1]
    gen_visited[r][c] = 1
    cand = []
    if r > 0 and not gen_visited[r-1][c]: cand.append((r-1, c))
    if r < R-1 and not gen_visited[r+1][c]: cand.append((r+1, c))
    if c > 0 and not gen_visited[r][c-1]: cand.append((r, c-1))
    if c < C-1 and not gen_visited[r][c+1]: cand.append((r, c+1))
    if cand:
        nr, nc = random.choice(cand)
        if nr < r: north_wall[r][c] = 0
        elif nr > r: north_wall[nr][nc] = 0
        elif nc < c: east_wall[r][c-1] = 0
        elif nc > c: east_wall[r][c] = 0
        gen_visited[nr][nc] = 1; gen_stack.append((nr, nc))
    else: gen_stack.pop()

def solve_step():
    global PHASE, current_pos
    if not solver_stack: return
    r, c = solver_stack[-1]
    current_pos = (r, c)
    if (r, c) == end_node: PHASE = "FINISHED"; return
    if not visited_solver[r][c]:
        visited_solver[r][c] = True; path_stack.append((r, c))
    dirs = [(-1,0),(1,0),(0,1),(0,-1)]; random.shuffle(dirs)
    moved = False
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < R and 0 <= nc < C and not visited_solver[nr][nc]:
            wall = False
            if dr == -1 and north_wall[r][c]: wall = True
            elif dr == 1 and north_wall[nr][nc]: wall = True
            elif dc == 1 and east_wall[r][c]: wall = True
            elif dc == -1 and east_wall[r][c-1]: wall = True
            if not wall: solver_stack.append((nr, nc)); moved = True; break
    if not moved: dead_ends.append(path_stack.pop()); solver_stack.pop()

# --- 4. Main ---
def main():
    if not glfw.init(): return
    window = glfw.create_window(1000, 800, "3D Maze Runner", None, None)
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST) # CRITICAL FOR 3D

    # Setup Perspective
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1000/800, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    gen_stack.append((0,0))
    angle = 0

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position Camera
        # Look down from an angle
        gluLookAt(0, 12, 12,  0, 0, 0,  0, 1, 0)
        glRotatef(angle, 0, 1, 0) # Rotate maze for effect
        angle += 0.2

        draw_maze_3d()

        # Draw "Rat" (Red Sphere/Cube) and Path
        off_x, off_z = -(C*CELL_SIZE)/2, -(R*CELL_SIZE)/2
        # Current Rat
        draw_cube(off_x + current_pos[1]*CELL_SIZE + 0.5, 0.15, off_z + current_pos[0]*CELL_SIZE + 0.5, 0.2, 0.15, 0.2, (1, 0, 0))
        
        # Draw Solver Path
        for pr, pc in path_stack:
            draw_cube(off_x + pc*CELL_SIZE + 0.5, 0.02, off_z + pr*CELL_SIZE + 0.5, 0.1, 0.01, 0.1, (1, 1, 0))

        if PHASE == "GENERATING": generate_step(); time.sleep(0.01)
        elif PHASE == "SOLVING": solve_step(); time.sleep(0.05)

        glfw.swap_buffers(window); glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__": main()