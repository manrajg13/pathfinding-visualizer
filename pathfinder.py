from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys

BLACK = '#000000'
WHITE = '#8f8f8f'
BLUE = '#0038c7'
RED = '#cc2941'
YELLOW = '#ffcb3b'
GREEN = '#00de6b'
CYAN = '#00cfde'

# Node object to populate graph with
class Node:
	def __init__(self, row, col):
		self.x = row
		self.y = col
		self.start = False
		self.wall = False
		self.end = False
		self.queued = False
		self.visited = False
		self.neighbours = []
		self.prior = None

	# draws Node at a given position and subtracts 1 pixel 
	# from dimensions to simulate a grid
	def draw(self, win, color, node_width):
		pygame.draw.rect(win, color, (self.x * node_width, self.y * node_width, node_width - 1, node_width - 1))

	# reset node type in case nodes need to be erased
	def reset(self):
		self.start = False
		self.wall = False
		self.end = False
		self.queued = False
		self.visited = False
		self.prior = None

	# appends all non diagonally adjacent nodes to neighbours list
	def set_neightbours(self, grid, cols, rows):
		# horizontal neighbours
		if self.x > 0:
			self.neighbours.append(grid[self.x - 1][self.y])
		if self.x < cols - 1:
			self.neighbours.append(grid[self.x + 1][self.y])
		#vertical neighbours
		if self.y > 0:
			self.neighbours.append(grid[self.x][self.y - 1])
		if self.y < rows - 1:
			self.neighbours.append(grid[self.x][self.y + 1])

# populate grid with nodes
def create_grid(cols, rows):
	grid = []
	for i in range(cols):
		grid.append([])
		for j in range(rows):
			grid[i].append(Node(i, j))

	return grid

# get mouse position in terms of node position
def get_mouse_pos(height, rows):
	x, y = pygame.mouse.get_pos()
	x, y = x // (height // rows), y // (height // rows)

	return x, y

# standard draw function for pygame to fill windoow and update node types
def draw(win, grid, path, cols, rows, width, height):
	node_width = height // rows
	win.fill(WHITE)

	# draw nodes
	for i in range(cols):
		for j in range(rows):
			node = grid[i][j]
			node.draw(win, BLACK, node_width)

			if node.queued:
				node.draw(win, YELLOW, node_width)
			if node.visited:
				node.draw(win, GREEN, node_width)
			if node in path:
				node.draw(win, CYAN, node_width)

			if node.start:
				node.draw(win, BLUE, node_width)
			if node.wall:
				node.draw(win, WHITE, node_width)
			if node.end:
				node.draw(win, RED, node_width)

	pygame.display.update()

def dijkstra(queue, path, start_node, end_node):
	if len(queue) > 0:
		# current node becomes next node to visit in queue
		current_node = queue.pop(0)
		current_node.visited = True

		# if current node is the end node, then append prior nodes
		# to the path list until current node becomes the start node
		if current_node == end_node:
			while current_node.prior != start_node:
				path.append(current_node.prior)
				current_node = current_node.prior

			# no longer searching
			return False, True

		# if current node is not the end node, queue all unqeued neighbours that aren't walls
		else:
			for neighbour in current_node.neighbours:
				if not neighbour.queued and not neighbour.wall:
					neighbour.queued = True
					neighbour.prior = current_node
					queue.append(neighbour)

			# still searching
			return True, False

def main():
	width = cols * 20
	height = rows * 20
	win = pygame.display.set_mode((width, height))

	grid = create_grid(cols, rows)
	queue = []
	path = []

	start_node = None
	start_node_created = False
	end_node = None
	end_node_created = False

	begin_search = False
	searching = False
	found = False

	while True:
		for event in pygame.event.get():
			# exit on event QUIT
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# draw start, wall, and end nodes with left click if search hasn't began
			if pygame.mouse.get_pressed()[0] and not searching:
				# get position of clicked node
				x, y = get_mouse_pos(height, rows)
				node = grid[x][y]

				# draw start node if not created and other nodes don't exist at position
				if not start_node_created and node != end_node and not node.wall:
					start_node = grid[x][y]
					start_node.start = True
					start_node.visited = True
					start_node_created = True

				# draw end node if not created and other nodes don't exist at position
				elif not end_node_created and grid[x][y] != start_node and not node.wall:
					end_node = grid[x][y]
					end_node.end = True
					end_node_created = True

				# draw wall node but don't overlap with start and end nodes
				elif node != end_node and node != start_node:
					grid[x][y].wall = True
			elif pygame.mouse.get_pressed()[2] and not searching:
				# get position of clicked ndoe
				x, y = get_mouse_pos(height, rows)
				node = grid[x][y]

				# reset node type at position
				grid[x][y].reset()

				# update values if start node deleted
				if node == start_node:
					start_node = None
					start_node_created = False

				# update values if end node deleted
				if node == end_node:
					end_node = None
					end_node_created = False

			# if space is pressed and start and end nodes have been created, begin search
			elif event.type == pygame.KEYDOWN and start_node_created and end_node_created:
				if event.key == pygame.K_SPACE:

					# set neighbours of all nodes to begin search
					for i in range(cols):
						for j in range(rows):
							grid[i][j].set_neightbours(grid, cols, rows)

					begin_search = True
					searching = True
					queue.append(start_node)

					# pressing space again quits window and ends program
					if found:
						pygame.quit()
						sys.exit()

		# begins using dijkstra's algorithm to find path to end node
		if begin_search and searching:
			searching, found = dijkstra(queue, path, start_node, end_node)

		draw(win, grid, path, cols, rows, width, height)

# setting dimensions to arguments if provided
if __name__ == "__main__":
	if len(sys.argv) == 1:
		cols = 40
		rows = 25
	elif len(sys.argv) == 3:
		cols = int(sys.argv[1])
		rows = int(sys.argv[2])
	else:
		print("Please enter either\n\t(1) arguments for columns and rows\n\t(2) no arguments for default dimensions (40, 25)")
		sys.exit(1)

main()