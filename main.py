import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import time

# --- 1. Maze Configuration ---
R, C = 12, 16 
WALL_HEIGHT = 0.7
CELL_SIZE = 1.0

# Required Data Structures
north_wall = [[1 for _ in range(C)] for _ in range(R)]
east_wall = [[1 for _ in range(C)] for _ in range(R)]

# State Management
PHASE = "GENERATING" 
gen_stack = []
gen_visited = [[0 for _ in range(C)] for _ in range(R)]

# ADDENDUM: Interior Start and End Points
start_node = (random.randint(2, R-3), random.randint(2, C-3))
end_node = (random.randint(2, R-3), random.randint(2, C-3))
while end_node == start_node: # Ensure they aren't the same
    end_node = (random.randint(2, R-3), random.randint(2, C-3))

solver_stack = [start_node]
path_stack = []
dead_ends = [] 
visited_solver = [[False for _ in range(C)] for _ in range(R)]
current_pos = start_node

# --- 2. 3D Drawing Helpers ---

def draw_cube(x, y, z, sx, sy, sz, color):
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
    off_x, off_z = -(C * CELL_SIZE) / 2, -(R * CELL_SIZE) / 2
    for r in range(R):
        for c in range(C):
            x, z = off_x + c * CELL_SIZE, off_z + r * CELL_SIZE
            # North wall logic
            if north_wall[r][c]:
                draw_cube(x + CELL_SIZE/2, WALL_HEIGHT/2, z, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.6, 0.6, 0.6))
            # East wall logic
            if east_wall[r][c]:
                draw_cube(x + CELL_SIZE, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.5, 0.5, 0.5))
            # Phantom edges (Bottom and Left boundary)
            if r == R-1: # Bottom
                draw_cube(x + CELL_SIZE/2, WALL_HEIGHT/2, z + CELL_SIZE, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.6, 0.6, 0.6))
            if c == 0: # Left
                draw_cube(x, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.5, 0.5, 0.5))
    # Floor
    draw_cube(0, -0.02, 0, (C*CELL_SIZE)/2, 0.01, (R*CELL_SIZE)/2, (0.1, 0.1, 0.1))

# --- 3. Logic Functions ---

def generate_step():
    global PHASE
    if not gen_stack:
        # ADDENDUM: Eat extra walls (1 in 20 chance) to create cycles
        for ir in range(1, R-1):
            for ic in range(1, C-1):
                if random.random() < 0.05: # 1/20 probability
                    if random.choice([True, False]): north_wall[ir][ic] = 0
                    else: east_wall[ir][ic] = 0
        PHASE = "SOLVING"
        return

    r, c = gen_stack[-1]
    gen_visited[r][c] = 1
    candidates = []
    if r > 0 and not gen_visited[r-1][c]: candidates.append((r-1, c))
    if r < R-1 and not gen_visited[r+1][c]: candidates.append((r+1, c))
    if c > 0 and not gen_visited[r][c-1]: candidates.append((r, c-1))
    if c < C-1 and not gen_visited[r][c+1]: candidates.append((r, c+1))

    if candidates:
        nr, nc = random.choice(candidates)
        if nr < r: north_wall[r][c] = 0
        elif nr > r: north_wall[nr][nc] = 0
        elif nc < c: east_wall[r][c-1] = 0
        elif nc > c: east_wall[r][c] = 0
        gen_visited[nr][nc] = 1
        gen_stack.append((nr, nc))
    else:
        gen_stack.pop()

def solve_step():
    """Backtracking solver following the provided logic."""
    global PHASE, current_pos
    if not solver_stack: return
    
    r, c = solver_stack[-1]
    current_pos = (r, c)
    
    if (r, c) == end_node: 
        PHASE = "FINISHED"
        return
    
    if not visited_solver[r][c]:
        visited_solver[r][c] = True
        path_stack.append((r, c))

    # Try moving in random directions
    dirs = [(-1,0),(1,0),(0,1),(0,-1)]
    random.shuffle(dirs)
    
    moved = False
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < R and 0 <= nc < C and not visited_solver[nr][nc]:
            # Wall check logic
            wall = False
            if dr == -1 and north_wall[r][c]: wall = True
            elif dr == 1 and north_wall[nr][nc]: wall = True
            elif dc == 1 and east_wall[r][c]: wall = True
            elif dc == -1 and east_wall[r][c-1]: wall = True
            
            if not wall:
                solver_stack.append((nr, nc))
                moved = True
                break
    
    if not moved:
        # Rule: Change color to blue and backtrack (put a 'mental' wall up)
        dead_ends.append(path_stack.pop())
        solver_stack.pop()

# --- 4. Main Loop ---
def main():
    if not glfw.init(): return
    window = glfw.create_window(1200, 900, "Final Challenge: 3D Backtracking Maze", None, None)
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1200/900, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    gen_stack.append(start_node)
    view_angle = 0

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera Positioning
        gluLookAt(0, 11, 13,  0, 0, 0,  0, 1, 0)
        glRotatef(view_angle, 0, 1, 0)
        view_angle += 0.1 # Rotation for visual clarity

        draw_maze_3d()

        off_x, off_z = -(C*CELL_SIZE)/2, -(R*CELL_SIZE)/2

        # Start and End Markers (Interior)
        draw_cube(off_x + start_node[1]*CELL_SIZE + 0.5, 0.01, off_z + start_node[0]*CELL_SIZE + 0.5, 0.4, 0.01, 0.4, (0, 1, 0)) # Green
        draw_cube(off_x + end_node[1]*CELL_SIZE + 0.5, 0.01, off_z + end_node[0]*CELL_SIZE + 0.5, 0.4, 0.01, 0.4, (1, 0.8, 0)) # Gold

        # Dead ends: BLUE Footprints
        for dr, dc in dead_ends:
            draw_cube(off_x + dc*CELL_SIZE + 0.5, 0.05, off_z + dr*CELL_SIZE + 0.5, 0.2, 0.02, 0.2, (0, 0, 1))

        # Active Path: Yellow Footprints
        for pr, pc in path_stack:
            draw_cube(off_x + pc*CELL_SIZE + 0.5, 0.04, off_z + pr*CELL_SIZE + 0.5, 0.15, 0.02, 0.15, (1, 1, 1))

        # The Mouse: RED Dot
        draw_cube(off_x + current_pos[1]*CELL_SIZE + 0.5, 0.25, off_z + current_pos[0]*CELL_SIZE + 0.5, 0.25, 0.2, 0.25, (1, 0, 0))

        # Execution
        if PHASE == "GENERATING":
            generate_step()
            time.sleep(0.01)
        elif PHASE == "SOLVING":
            solve_step()
            time.sleep(0.05)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()