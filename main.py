# Create a global state for generation
gen_stack = []
gen_visited = [[0 for _ in range(C)] for _ in range(R)]

def init_generation():
    global gen_stack
    start_r, start_c = random.randint(0, R-1), random.randint(0, C-1)
    gen_visited[start_r][start_c] = 1
    gen_stack.append((start_r, start_c))

def generate_maze_step():
    global gen_stack
    if not gen_stack:
        return True # Finished generation

    r, c = gen_stack[-1]
    candidates = []
    # ... (your candidate logic here) ...

    if candidates:
        nr, nc = random.choice(candidates)
        # Eat the wall logic...
        
        # ADD CHALLENGE: 1 in 20 chance to eat another wall nearby
        if random.random() < 0.05:
            # Code to remove a random adjacent wall even if visited
            pass

        gen_visited[nr][nc] = 1
        gen_stack.append((nr, nc))
    else:
        gen_stack.pop()
    return False