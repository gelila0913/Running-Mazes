import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import time

# --- 1. Maze Configuration ---
R, C = 15, 20 
CELL_SIZE = 1.0
WALL_HEIGHT = 0.5

# Required Data Structure
north_wall = [[1 for _ in range(C)] for _ in range(R)]
east_wall = [[1 for _ in range(C)] for _ in range(R)]

# State Management
PHASE = "GENERATING" 
gen_stack = []
gen_visited = [[0 for _ in range(C)] for _ in range(R)]

# ADDENDUM: Interior Start and End Points
start_node = (random.randint(2, R-3), random.randint(2, C-3))
end_node = (random.randint(2, R-3), random.randint(2, C-3))
while end_node == start_node:
    end_node = (random.randint(2, R-3), random.randint(2, C-3))

solver_stack = [start_node]
path_stack = []
dead_ends = [] 
visited_solver = [[False for _ in range(C)] for _ in range(R)]
current_pos = start_node

# --- 2. 3D Drawing Helpers ---

def draw_block(x, y, z, sx, sy, sz, color):
    """Draws a 3D cube/wall."""
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

def render_scene():
    """Draws the floor and all walls."""
    # Center the maze at (0,0)
    off_x, off_z = -(C * CELL_SIZE) / 2, -(R * CELL_SIZE) / 2
    
    # Draw Floor
    draw_block(0, -0.05, 0, (C*CELL_SIZE)/2, 0.02, (R*CELL_SIZE)/2, (0.1, 0.1, 0.1))

    for r in range(R):
        for c in range(C):
            x, z = off_x + c * CELL_SIZE, off_z + r * CELL_SIZE
            
            # North Walls
            if north_wall[r][c]:
                draw_block(x + CELL_SIZE/2, WALL_HEIGHT/2, z, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.7, 0.7, 0.7))
            # East Walls
            if east_wall[r][c]:
                draw_block(x + CELL_SIZE, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.6, 0.6, 0.6))
            # Left Boundary
            if c == 0:
                draw_block(x, WALL_HEIGHT/2, z + CELL_SIZE/2, 0.05, WALL_HEIGHT/2, CELL_SIZE/2, (0.6, 0.6, 0.6))
            # Bottom Boundary
            if r == R-1:
                draw_block(x + CELL_SIZE/2, WALL_HEIGHT/2, z + CELL_SIZE, CELL_SIZE/2, WALL_HEIGHT/2, 0.05, (0.7, 0.7, 0.7))

# --- 3. Logic Functions ---

def generate_step():
    global PHASE
    if not gen_stack:
        # ADDENDUM: Create cycles by eating 1 in 20 random walls
        for _ in range(int((R*C)/20)):
            ir, ic = random.randint(1, R-2), random.randint(1, C-2)
            if random.random() > 0.5: north_wall[ir][ic] = 0
            else: east_wall[ir][ic] = 0
        PHASE = "SOLVING"
        return

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
        gen_visited[nr][nc] = 1
        gen_stack.append((nr, nc))
    else:
        gen_stack.pop()

def solve_step():
    global PHASE, current_pos
    if not solver_stack: return
    r, c = solver_stack[-1]
    current_pos = (r, c)
    if (r, c) == end_node: 
        PHASE = "FINISHED"; return
    if not visited_solver[r][c]:
        visited_solver[r][c] = True; path_stack.append((r, c))

    dirs = [(-1,0),(1,0),(0,1),(0,-1)]
    random.shuffle(dirs)
    moved = False
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < R and 0 <= nc < C and not visited_solver[nr][nc]:
            wall = False
            if dr == -1 and north_wall[r][c]: wall = True
            elif dr == 1 and north_wall[nr][nc]: wall = True
            elif dc == 1 and east_wall[r][c]: wall = True
            elif dc == -1 and east_wall[r][c-1]: wall = True
            if not wall:
                solver_stack.append((nr, nc)); moved = True; break
    if not moved:
        # Assignment Rule: "Dead end = blue and backtrack"
        dead_ends.append(path_stack.pop())
        solver_stack.pop()

# --- 4. Main ---
def main():
    if not glfw.init(): return
    window = glfw.create_window(1200, 900, "3D Backtracking Maze Runner", None, None)
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    # Perspective Setup
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1200/900, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    gen_stack.append(start_node)
    
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.05, 0.05, 0.08, 1.0)
        glLoadIdentity()
        
        # Camera Positioning (Tilted Perspective)
        gluLookAt(0, 15, 15,  0, 0, 0,  0, 1, 0)

        render_scene()
        
        off_x, off_z = -(C*CELL_SIZE)/2, -(R*CELL_SIZE)/2
        
        # Start (Green) and End (Gold)
        draw_block(off_x + start_node[1]*CELL_SIZE + 0.5, 0.02, off_z + start_node[0]*CELL_SIZE + 0.5, 0.4, 0.02, 0.4, (0, 1, 0))
        draw_block(off_x + end_node[1]*CELL_SIZE + 0.5, 0.02, off_z + end_node[0]*CELL_SIZE + 0.5, 0.4, 0.02, 0.4, (1, 0.8, 0))

        # Dead Ends: BLUE cubes
        for dr, dc in dead_ends:
            draw_block(off_x + dc*CELL_SIZE + 0.5, 0.05, off_z + dr*CELL_SIZE + 0.5, 0.2, 0.05, 0.2, (0, 0, 1))

        # Path: WHITE footprints
        for pr, pc in path_stack:
            draw_block(off_x + pc*CELL_SIZE + 0.5, 0.05, off_z + pr*CELL_SIZE + 0.5, 0.1, 0.03, 0.1, (1, 1, 1))

        # The Mouse: RED block
        draw_block(off_x + current_pos[1]*CELL_SIZE + 0.5, 0.2, off_z + current_pos[0]*CELL_SIZE + 0.5, 0.2, 0.2, 0.2, (1, 0, 0))

        if PHASE == "GENERATING": generate_step(); time.sleep(0.01)
        elif PHASE == "SOLVING": solve_step(); time.sleep(0.04)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()