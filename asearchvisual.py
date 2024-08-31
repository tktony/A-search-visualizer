import pygame
import sys
import math
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os

# Initialize Pygame and create the screen
pygame.init()
screen = pygame.display.set_mode((750, 750))
pygame.display.set_caption("A*Search Path Finding Algorith Visualizer")

# Constants for grid size and colors
GRID_SIZE = 50
CELL_WIDTH = 750 // GRID_SIZE
CELL_HEIGHT = 750 // GRID_SIZE
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'grey': (105, 106, 107),    
    'white': (255, 255, 255),
    'path': (255, 8, 127),
}

# Spot class represents each cell in the grid
class Spot:
    def __init__(self, x, y):
        self.x, self.y = x, y
        # Calculation: f(total cost of a node) = g(cost from start to current node) + h(cost from current node to goal node)
        self.f, self.g, self.h = 0, 0, 0
        self.neighbors = []
        self.previous = None
        self.obs = False
        self.closed = False

    # Display the cell
    def show(self, color, outline_width):
        if not self.closed:
            pygame.draw.rect(screen, color, (self.x * CELL_WIDTH, self.y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT), outline_width)
            pygame.display.update()

    # Highlight the path
    def path(self, color, outline_width):
        pygame.draw.rect(screen, color, (self.x * CELL_WIDTH, self.y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT), outline_width)
        pygame.display.update()

    # Add neighboring cells for pathfinding
    def add_neighbors(self, grid):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and not grid[nx][ny].obs:
                self.neighbors.append(grid[nx][ny])

# Create the grid
grid = [[Spot(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

# Set start and end points default values
start, end = grid[1][1], grid[48][48]

# Display the grid
for row in grid:
    for spot in row:
        spot.show(COLORS['white'], 1)

# Draw grid borders
for i in range(GRID_SIZE):
    grid[0][i].show(COLORS['grey'], 0)
    grid[0][i].obs = True
    grid[GRID_SIZE-1][i].obs = True
    grid[GRID_SIZE-1][i].show(COLORS['grey'], 0)
    grid[i][0].obs = True
    grid[i][GRID_SIZE-1].obs = True
    grid[i][0].show(COLORS['grey'], 0)
    grid[i][GRID_SIZE-1].show(COLORS['grey'], 0)

# Set up Tkinter input window for start and end points
def on_submit():
    global start, end
    try:
        # Parse the input coordinates
        st = start_box.get().split(',')
        ed = end_box.get().split(',')

        # Convert coordinates to integers
        st_x, st_y = int(st[0]), int(st[1])
        ed_x, ed_y = int(ed[0]), int(ed[1])

        if not (1 <= st_x <= 48 and 1 <= st_y <= 48):
            raise ValueError("Start coordinates out of range!")
        if not (1 <= ed_x <= 48 and 1 <= ed_y <= 48):
            raise ValueError("End coordinates out of range!")
        
        # Set the start and end points based on valid input
        start, end = grid[st_x][st_y], grid[ed_x][ed_y]

        # Close the Tkinter window
        window.quit()
        window.destroy()
    except (ValueError, IndexError) as e:
        # Show an error message if coordinates are invalid
        messagebox.showerror("Invalid Input", f"Please enter coordinates within the range (1, 1) to (48, 48).\nError: {str(e)}")


window = Tk()
Label(window, text='Start(x,y): ').grid(row=0, pady=3)
start_box = Entry(window)
start_box.grid(row=0, column=1, pady=3)
Label(window, text='End(x,y): ').grid(row=1, pady=3)
end_box = Entry(window)
end_box.grid(row=1, column=1, pady=3)
var = IntVar()
ttk.Checkbutton(window, text='Show Steps :', onvalue=1, offvalue=0, variable=var).grid(columnspan=2, row=2)
Button(window, text='Submit', command=on_submit).grid(columnspan=2, row=3)

window.mainloop()

# Initialize Open and Closed Sets
open_set = [start]
closed_set = []  # Define closed_set to track visited nodes

# Function to handle mouse clicks
def mouse_press(pos):
    grid_x, grid_y = pos[0] // CELL_WIDTH, pos[1] // CELL_HEIGHT
    spot = grid[grid_x][grid_y]
    if spot != start and spot != end and not spot.obs:
        spot.obs = True
        spot.show(COLORS['white'], 0)

# Highlight start and end points
start.show(COLORS['path'], 0)
end.show(COLORS['path'], 0)

# Main loop to handle events
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif pygame.mouse.get_pressed()[0]:
            mouse_press(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            running = False

# Add neighbors for each cell
for row in grid:
    for spot in row:
        spot.add_neighbors(grid)

# Heuristic function for pathfinding (Euclidean distance)
def heuristic(node, goal):
    return math.sqrt((node.x - goal.x) ** 2 + (node.y - goal.y) ** 2)

# Main pathfinding function
def main():
    if not open_set:
        return
    
    # --- A* Search Algorithm ---
    
    # Step 1: Find the spot with the lowest f value in the open set
    current = min(open_set, key=lambda spot: spot.f)

    # Step 2: If the current spot is the end spot, reconstruct the path
    if current == end:
        print('Path found:', current.f)
        temp = current.f
        while current:
            current.closed = False
            current.show(COLORS['blue'], 0)
            current = current.previous
        end.show(COLORS['path'], 0)
        result = messagebox.askokcancel('Program Finished', f'The shortest path is {temp} blocks away.')
        if result:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            pygame.quit()
            sys.exit()

    # Step 3: Move the current spot from open set to closed set
    open_set.remove(current)
    closed_set.append(current)
    current.closed = True
    
    # Step 4: Evaluate all the neighbors of the current spot
    for neighbor in current.neighbors:
        if neighbor in closed_set:
            continue

        # Step 5: Calculate the tentative g score
        tentative_g = current.g + 1

        # Step 6: If the neighbor is not in the open set or the new g score is lower, update the neighbor's values
        if neighbor not in open_set or tentative_g < neighbor.g:
            neighbor.g = tentative_g
            neighbor.h = heuristic(neighbor, end)  # Calculate the heuristic (h score)
            neighbor.f = neighbor.g + neighbor.h  # f = g + h
            neighbor.previous = current  # Set the current spot as the previous spot for this neighbor
            
            # Step 7: If the neighbor is not in the open set, add it
            if neighbor not in open_set:
                open_set.append(neighbor)
                
    # Step 8: Optionally show the steps (visualization)
    if var.get():
        for spot in open_set:
            spot.show(COLORS['green'], 0)
        for spot in closed_set:
            if spot != start:
                spot.show(COLORS['red'], 0)
# Main execution loop
while True:
    pygame.display.update()
    main()
