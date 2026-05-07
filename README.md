# Assignment: 3D Procedural Maze Generation and Autonomous Navigation

## Project Title
**Visualizing Backtracking Algorithms through 3D Simulation**

---

## Technical Description

This project is a real-time 3D simulation developed to demonstrate the fundamental principles of **graph traversal** and **procedural content generation**. The system constructs and navigates a complex environment using standard data structures and algorithmic logic.

The implementation is divided into two core algorithmic phases:

### 1. Procedural Maze Generation (DFS)
The environment is generated using a **Stack-based Depth-First Search (DFS)** algorithm. 
* **Mechanism:** The "generator" moves through a grid, removing walls between adjacent cells based on random selection from a stack of unvisited neighbors.
* **Integrity:** The maze is stored in two 2D matrices (`north_wall` and `east_wall`), ensuring strict wall integrity and a "perfect" maze structure (one unique path between any two points).

### 2. Autonomous Backtracking Solver
After generation, an autonomous "Rat" agent is deployed to solve the maze. 
* **Algorithm:** It utilizes a **Backtracking Algorithm** to navigate from an interior start node to an interior goal.
* **Path Memory:** The agent maintains a stack of the current path, visualized by white trail markers.
* **Dead-End Logic:** Upon reaching a trapped state (no valid unvisited neighbors), the agent marks the cell with a **blue marker**, pops the stack (backtracks), and attempts the next available branch.
* **Collision Detection:** The solver interfaces directly with the `north_wall` and `east_wall` arrays to determine passable routes.

### 3. Advanced Features (Addendums)
To fulfill high-level assignment requirements, the following features were added:
* **Interior Node Logic:** Start and End points are placed randomly within the maze's interior (avoiding edges) to ensure a non-trivial solution.
* **Graph Cycles:** Approximately 5% of internal walls are randomly removed after the initial generation to create cycles and loops, testing the solver's ability to handle non-tree graph structures.
* **3D Visual Fidelity:** Implemented via **PyOpenGL**, featuring a tilted 3D perspective, depth testing, and **Texture Mapping** for a realistic animated agent (the "Real Rat").

---

## Visual Legend
* **Green Pad:** Interior Start Position
* **Gold Pad:** Interior Exit/Goal
* **Red Rat:** The Autonomous Agent
* **White Markers:** The active "Best Guess" path
* **Blue Blocks:** Identified Dead Ends (Backtracked paths)
* **Gray Geometry:** 3D Walls generated from the matrix data

## Initial Procedural State: The Closed Grid Matrix

Before the randomized Depth-First Search algorithm begins "eating" walls, the entire maze is initialized as a closed system. This is a crucial first step in procedural generation, where every possible wall exists by default.

This image visualizes that initial uniform grid state. Architecturally, this represents that the underlying `north_wall` and `east_wall` matrices are filled entirely with values of `1` (Wall Integrity intact). We also observe the predefined interior start position (green pad) and end position (gold pad), established just before the generation loop consumes the first wall.

![closed grid](image.png)