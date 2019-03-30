import cv2
import numpy as np
import math
import time

## List of methods to be used
def is_in_rect(x,y,p1,p4):
    f1 = y - p1[1]
    f2 = y - p4[1]
    f3 = x - p1[0]
    f4 = x - p4[0]
    if f1 >= 0 and f2 <= 0 and f3 >= 0 and f4 <=0:
        return True

def is_in_circle(x,y,h,k,r):
    f5 = (x-h)**2 + (y-k)**2 - r**2
    if f5 <= 0:
        return True

def is_in_ellipse(x,y,a,b,h,k):
    f6 = ((x-h)**2)/a**2 + ((y-k)**2)/b**2 - 1
    if f6 <= 0:
        return True

def get_line_equation(x,y,p1,p2):
    if p2[0] - p1[0] != 0:
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        f = y - p1[1] - m * x + m * p1[0]
    else:
        f = x - p2[0]
    return f

def is_poly(x,y,scale):
    in_poly1 = False
    in_poly2 = False
    in_poly3 = False
    p1 = [125*scale,94*scale]
    p2 = [163*scale,98*scale]
    p3 = [150*scale,135*scale]
    # Equation of half planes for poly one
    f7 = get_line_equation(x,y,p1,p2)
    f8 = get_line_equation(x,y,p2,p3)
    f9 = get_line_equation(x,y,p1,p3)            
    if f7 >= 0 and f8 <= 0 and f9 <=0:
        in_poly1 = True
    
    p1 = [150*scale,135*scale]
    p2 = [163*scale,98*scale]
    p3 = [163*scale,135*scale]
    # Equation of half planes for poly two
    f10 = get_line_equation(x,y,p1,p2)
    f11 = get_line_equation(x,y,p2,p3)
    f12 = get_line_equation(x,y,p1,p3)            
    if f10 >= 0 and f11 <= 0 and f12 <=0:
        in_poly2 = True
    
    p1 = [163*scale,135*scale]
    p2 = [163*scale,98*scale]
    p3 = [170*scale,60*scale]
    p4 = [193*scale,98*scale]
    p5 = [173*scale,135*scale]
    # Equation of half planes for poly three
    f13 = get_line_equation(x,y,p1,p2)
    f14 = get_line_equation(x,y,p2,p3)
    f15 = get_line_equation(x,y,p3,p4)
    f16 = get_line_equation(x,y,p4,p5)
    f17 = get_line_equation(x,y,p5,p1)
    if f13>=0 and f14>=0 and f15>=0 and f16<=0 and f17<=0:
        in_poly3 = True
        
    return in_poly1 or in_poly2 or in_poly3
    
# Draw obstacles using obstacle points on pygame surface
def draw_obstacles(obstacle_set):
    for p in obstacle_set:
        pxarray[p[0], p[1]] = pygame.Color(0, 0, 0)
        pygame.display.update()

        
def draw_obstacles_bg(img,obstacle_set):
    for p in obstacle_set:
        img[p[1],p[0]] = 0
        
### Apply minkowski sum to obstacle points 
def minkowski_sum(bg,r,obstacle_set,width,height):
    new_obstacle_set = set()
    for p in obstacle_set:
        h = p[0]
        k = p[1]
        # skip convolution for pixels that are completely inside the circle
        #if bg[k,h-r] == (0,0,0) and bg[k,h+r] == (0,0,0) and bg[k-r,h] == (0,0,0) and bg[k+r,h] == (0,0,0):
        #    continue
        for x in range(h-r,h+r):
            for y in range(k-r,k+r):
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue
                else:
                    f = (x-h)**2 + (y-k)**2 - r**2
                    if f <= 0:
                        new_obstacle_set.add((x,y))
                    
    return new_obstacle_set
    # using each point find new obstacle points

class Node:
    def __init__(self):
        self.visited = False
        self.neighbours = {}
        self.prev_node = None
        self.on_path = False
        self.explored = False
        
class Graph:
    # graph constructor that creates an empty dictionary
    # nodes = {(x,y):Node} where x,y are coordinates of node
    def __init__(self):
        self.nodes = {}
        self.costs = {}
    # loop through image and create node object for each pixel
    def create_nodes(self,width,height,obstacle_set):
        for x in range(0,width):
            for y in range(0,height):
                if (x,y) not in obstacle_set:
                    self.nodes[(x,y)] = Node()
                    #self.costs[(x,y)] = 9999999
    # for given pixel and find it's neighbours
    def calculate_neighbours(self,node_tuple,width,height):
        x = node_tuple[0]
        y = node_tuple[1]
        dig = 1.41
        strght = 1
        if (x-1,y-1) not in obstacle_set and x-1  >= 0 and y-1 >= 0:
            self.nodes[(x,y)].neighbours[(x-1,y-1)] = dig
        if (x,y-1) not in obstacle_set and y-1 >= 0:
            self.nodes[(x,y)].neighbours[(x,y-1)] = strght
        if (x+1,y-1) not in obstacle_set and x+1 < width and y-1 >=0:
            self.nodes[(x,y)].neighbours[(x+1,y-1)] = dig
        if (x-1,y) not in obstacle_set and x-1 >= 0:
            self.nodes[(x,y)].neighbours[(x-1,y)] = strght
        if (x+1,y) not in obstacle_set and x+1 < width:
            self.nodes[(x,y)].neighbours[(x+1,y)] = strght
        if (x-1,y+1) not in obstacle_set and x-1 >= 0 and y+1 < height:
            self.nodes[(x,y)].neighbours[(x-1,y+1)] = dig
        if (x,y+1) not in obstacle_set and y+1 < height:
            self.nodes[(x,y)].neighbours[(x,y+1)] = strght
        if (x+1,y+1) not in obstacle_set and x+1 < width and y+1 < height:
            self.nodes[(x,y)].neighbours[(x+1,y+1)] = dig
    def get_smallest(self,costs):
        smallest = 9999999;
        smallest_key = None
        for key, value in costs.items():
            if value < smallest:
                smallest = value
                smallest_key = key
        return smallest_key
    # get shortest path using Dijkstra algorithm
    def dijkstra_algo(self,rob_x,rob_y,goal_x,goal_y,bg):
        # get coordinates for the start node
        start_node = (rob_x,rob_y)
        # get coordinates for the goal node
        goal_node = (goal_x,goal_y)
        # make cost of start node zero
        self.costs[start_node] = 0
        # set current node equal to start node
        curr_node = start_node
        # loop until goal node is reached
        while not curr_node == goal_node:
            # loop through each neighbour
            for n in self.nodes[curr_node].neighbours:
                # if neighbour is visted skip
                if self.nodes[n].visited:
                    continue
                if not n in self.costs:
                    self.costs[n] = 9999999
                self.nodes[n].explored = True
                # calculate total cost to go to the node
                total_cost = self.costs[curr_node] + self.nodes[curr_node].neighbours[n]
                # if total cost is less than current cost of the 
                # neighbour then update it.
                if total_cost < self.costs[n]:
                    self.costs[n] = total_cost
                    self.nodes[n].prev_node = curr_node
            # mark current node as visited
            self.nodes[curr_node].visited = True
            # delete cost of current node
            del self.costs[curr_node]
            # get smallest univisited node with smallest cost
            curr_node = self.get_smallest(self.costs)
        # Track the path from goal node to start node and mask nodes on the path
        while not self.nodes[curr_node].prev_node == None:
            self.nodes[curr_node].on_path = True
            curr_node = self.nodes[curr_node].prev_node
        cv2.destroyAllWindows()

# scale the window size
scale = 1
height = 150*scale
width = 250*scale

# create a background image
bg = np.zeros((height,width,3),dtype=np.uint8)
for x in range(0,bg.shape[0]):
    for y in range(0,bg.shape[1]):
        bg[x,y] = (255,255,255)

# Define obstacle point x and y set
obstacle_set = set()

# iterate for each pixel and find out if it is an obstacle
# if it is in the obstacle store it in the obstacle set
for x in range(0,width):
    for y in range(0,height):
        if is_in_rect(x,y,[50*scale,38*scale],[100*scale,83*scale]) or is_in_circle(x,y,190*scale,20*scale,15*scale) or is_in_ellipse(x,y,30*scale,12*scale,140*scale,30*scale) or is_poly(x,y,scale):
            obstacle_set.add((x,y))
            bg[y,x] = (0,0,0)  
cv2.imwrite("without_minkowski.png",bg)

# Calculate Mikowski space
r = int(input("Please enter robot radius: "))
c = int(input("Please enter robot clearance: "))
r = r + c
print("Calculating Minowski Space. please wait")
obstacle_set = minkowski_sum(bg,r*scale,obstacle_set,width,height)
draw_obstacles_bg(bg,obstacle_set)
cv2.imwrite("with_minkowski.png",bg)

# Take user input for start node
robo_str = input("Please enter start coordinate separated by space: ")
lst = robo_str.split()
inp_lst = (int(lst[0]),int(lst[1]))
while(inp_lst in obstacle_set or int(inp_lst[0]) < 0 or int(inp_lst[0]) >= width or int(inp_lst[1]) < 0 or int(inp_lst[1]) >= height):
    print("Invalid input. Point is on the obstacle or outside the map.")
    robo_str = input("Please enter another start coordinates separated by space.")
    lst = robo_str.split()
    inp_lst = (int(lst[0]),int(lst[1]))
x_r = inp_lst[0]
y_r = inp_lst[1]
# take user input for goal node
goal_str = input("Please enter end coordinate separated by space: ")
lst = goal_str.split()
inp_lst = (int(lst[0]),int(lst[1]))
while(inp_lst in obstacle_set or int(inp_lst[0]) < 0 or int(inp_lst[0]) >= width or int(inp_lst[1]) < 0 or int(inp_lst[1]) >= height):
    print("Invalid input. Point is on the obstacle or outside the map.")
    goal_str = input("Please enter end coordinate separated by space: ")
    lst = goal_str.split()
    inp_lst = (int(lst[0]),int(lst[1]))
x_g = inp_lst[0]
y_g = inp_lst[1]

print("Calculating path, please wait.")

graph = Graph()
graph.create_nodes(width,height,obstacle_set)
for node in graph.nodes:
    graph.calculate_neighbours(node,width,height)
#for key,value in graph.nodes.items():
#    print(key,": ",value.neighbours)

# define color for visited node
green = (60,179,113)
# define color for unvisited node
grey = (192,192,192)
# define color for nodes on the path
blue = (250,50,50)
# color for explored node
yellow = (0,255,255)

start_time = time.time()
graph.dijkstra_algo(x_r,y_r,x_g,y_g,bg)
elapsed = time.time() - start_time
print("Time taken:",elapsed)

for node in graph.nodes:
        if graph.nodes[node].visited == False:
            bg[node[1],node[0]] = grey
        if graph.nodes[node].explored == True:
            bg[node[1],node[0]] = yellow
        if graph.nodes[node].visited == True:
            bg[node[1],node[0]] = green
        if graph.nodes[node].on_path == True:
            bg[node[1],node[0]] = blue    
            

bg = cv2.resize(bg,(3*width,3*height))
cv2.imshow("Scaled Dijkstra Image",bg)
cv2.waitKey(0)
cv2.destroyAllWindows()
