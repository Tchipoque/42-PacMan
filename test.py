from mazegenerator import MazeGenerator

# Create a maze (default size is 15x15 per the class, not 20x20 — check your constructor call)
maze_gen = MazeGenerator(size=(20, 20), perfect=False, seed=42)

maze_grid = maze_gen.maze
shortest_path = maze_gen.shortest_path

print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
print(f"Shortest path length: {len(shortest_path) if shortest_path else 'N/A (no path found)'}")


def maze_to_text(maze: list[list[int]]) -> str:
    """Render the wall-bitmask grid as an ASCII maze."""
    lines = []
    for row in maze:
        top = "".join("+" + ("---" if cell & 1 else "   ") for cell in row) + "+"
        mid = "".join(("|" if cell & 8 else " ") + "   " for cell in row)
        mid += "|" if row[-1] & 2 else " "
        lines.append(top)
        lines.append(mid)
    lines.append("+---" * len(maze[0]) + "+")
    return "\n".join(lines)


ascii_maze = maze_to_text(maze_grid)

# 1) Print it to the terminal
print(ascii_maze)

# 2) Also save it to a text file so you can study it
with open("mazes/maze_dump.txt", "w") as f:
    f.write(ascii_maze)
