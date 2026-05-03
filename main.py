import glfw
from OpenGL.GL import *
import random
import time

try:
    from PIL import Image
except ImportError:
    Image = None

# --- 1. Maze Configuration ---
R, C = 15, 20
CELL_SIZE = 1.8 / max(R, C)

north_wall = [[1 for _ in range(C)] for _ in range(R)]
east_wall = [[1 for _ in range(C)] for _ in range(R)] 
left_wall = [1 for _ in range(R)] 

PHASE = "GENERATING" 
gen_stack = []
gen_visited = [[0 for _ in range(C)] for _ in range(R)]

# Define Openings
start_r = random.randint(0, R-1)
end_r = random.randint(0, R-1)
start_node = (start_r, 0)
end_node = (end_r, C-1)

# Opening the perimeter walls
left_wall[start_r] = 0        
east_wall[end_r][C-1] = 0     

solver_stack = [start_node]
path_stack = []
dead_ends = []
visited_solver = [[False for _ in range(C)] for _ in range(R)]

# Start the mouse "outside" to show the opening
current_pos = (start_r, -0.8) 
mouse_angle = 0.0
mouse_texture_id = None

# --- 2. Graphics Helpers ---
def load_texture(filename):
    if not Image: return None
    try:
        img = Image.open(filename)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGBA").tobytes()
        width, height = img.size
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return tex_id
    except: return None

def draw_line(x1, y1, x2, y2):
    glBegin(GL_LINES); glVertex2f(x1, y1); glVertex2f(x2, y2); glEnd()

def draw_cell_marker(r, c, color_rgb, size=8.0):
    x = -0.9 + c * CELL_SIZE + (CELL_SIZE / 2.0)
    y = 0.9 - r * CELL_SIZE - (CELL_SIZE / 2.0)
    glColor3f(*color_rgb)
    glPointSize(size)
    glBegin(GL_POINTS); glVertex2f(x, y); glEnd()

def draw_rat(r, c, texture_id, angle):
    # Scale coordinates for smooth transition at exit
    cx = -0.9 + c * CELL_SIZE + (CELL_SIZE / 2.0)
    cy = 0.9 - r * CELL_SIZE - (CELL_SIZE / 2.0)
    s = CELL_SIZE / 2.2
    if texture_id:
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, texture_id); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1, 1, 1); glPushMatrix(); glTranslatef(cx, cy, 0); glRotatef(angle, 0, 0, 1)
        glBegin(GL_QUADS); glTexCoord2f(0,0); glVertex2f(-s,-s); glTexCoord2f(1,0); glVertex2f(s,-s); glTexCoord2f(1,1); glVertex2f(s,s); glTexCoord2f(0,1); glVertex2f(-s,s); glEnd()
        glPopMatrix(); glDisable(GL_TEXTURE_2D)
    else:
        glColor3f(1, 1, 0); glPointSize(14.0); glBegin(GL_POINTS); glVertex2f(cx, cy); glEnd()

# --- 3. Logic Functions ---
def generate_step():
    global PHASE, current_pos
    if not gen_stack:
        PHASE = "ADDING_CYCLES"; return
    r, c = gen_stack[-1]
    current_pos = (r, c)
    candidates = []
    if r > 0 and gen_visited[r-1][c] == 0: candidates.append((r-1, c))
    if r < R-1 and gen_visited[r+1][c] == 0: candidates.append((r+1, c))
    if c > 0 and gen_visited[r][c-1] == 0: candidates.append((r, c-1))
    if c < C-1 and gen_visited[r][c+1] == 0: candidates.append((r, c+1))
    if candidates:
        nr, nc = random.choice(candidates)
        if nr < r: north_wall[r][c] = 0
        elif nr > r: north_wall[nr][nc] = 0
        elif nc < c: east_wall[r][c-1] = 0
        elif nc > c: east_wall[r][c] = 0
        gen_visited[nr][nc] = 1; gen_stack.append((nr, nc))
    else: gen_stack.pop()

def add_cycles():
    global PHASE
    for i in range(1, R-1):
        for j in range(1, C-1):
            if random.random() < 0.05:
                if random.choice([True, False]): north_wall[i][j] = 0
                else: east_wall[i][j] = 0
    PHASE = "SOLVING"

def solve_step():
    global PHASE, current_pos, mouse_angle
    if not solver_stack: return
    r, c = solver_stack[-1]
    current_pos = (r, c)
    if (r, c) == end_node:
        path_stack.append((r, c))
        current_pos = (r, c + 1.2) # Mouse walks out of the maze
        PHASE = "FINISHED"; return
    if not visited_solver[r][c]:
        visited_solver[r][c] = True; path_stack.append((r, c))
    dirs = [(-1,0,90),(1,0,270),(0,1,0),(0,-1,180)]; random.shuffle(dirs)
    moved = False
    for dr, dc, angle in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and not visited_solver[nr][nc]:
            wall = False
            if dr == -1 and north_wall[r][c]: wall = True
            elif dr == 1 and north_wall[nr][nc]: wall = True
            elif dc == 1 and east_wall[r][c]: wall = True
            elif dc == -1 and east_wall[r][c-1]: wall = True
            if not wall:
                solver_stack.append((nr, nc)); mouse_angle = angle; moved = True; break
    if not moved: dead_ends.append(path_stack.pop()); solver_stack.pop()

# --- 4. Main ---
def main():
    if not glfw.init(): return
    window = glfw.create_window(1000, 800, "Maze: Smooth Entry and Exit", None, None)
    glfw.make_context_current(window)
    global mouse_texture_id
    mouse_texture_id = load_texture("rat.png")
    gen_visited[start_node[0]][start_node[1]] = 1; gen_stack.append(start_node)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT); glClearColor(0.1, 0.1, 0.1, 1.0)
        glLineWidth(3.0); glColor3f(1, 1, 1)
        for i in range(R):
            for j in range(C):
                x, y = -0.9 + j*CELL_SIZE, 0.9 - i*CELL_SIZE
                if north_wall[i][j]: draw_line(x, y, x+CELL_SIZE, y)
                if east_wall[i][j]: draw_line(x+CELL_SIZE, y, x+CELL_SIZE, y-CELL_SIZE)
                if i == R-1: draw_line(x, y-CELL_SIZE, x+CELL_SIZE, y-CELL_SIZE)
                if j == 0 and left_wall[i]: draw_line(x, y, x, y-CELL_SIZE)

        # Draw solving paths (Small red dots)
        for r, c in path_stack: draw_cell_marker(r, c, (1, 0, 0), 5.0)
        for r, c in dead_ends: draw_cell_marker(r, c, (0, 0.5, 0.8), 5.0)

        draw_rat(current_pos[0], current_pos[1], mouse_texture_id, mouse_angle)

        if PHASE == "GENERATING": generate_step(); time.sleep(0.01)
        elif PHASE == "ADDING_CYCLES": add_cycles()
        elif PHASE == "SOLVING": solve_step(); time.sleep(0.04)

        glfw.swap_buffers(window); glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__": main()