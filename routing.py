import cv2
from PIL import Image
import time

size = 4
count = 0

#========================================================================== 

# function to determine pixels that are non-passable (black pixels)
def is_blocked(p):
    global count
    x,y = p
    pixel = path_pixels[x,y]

    #if (pixel < 255):
    if any(c < 225 for c in pixel):
        return True

#========================================================================== 
    
# 4 connectivity neighbours
def neighbours_4(p):
    x, y = p
    neighbors = [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
    return [p for p in neighbors if not is_blocked(p)]

# 8 connectivity neighbours
def neighbours_8(p):
    x, y = p
    neighbors = [(x-1, y), (x, y-1), (x+1, y), (x, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]
    return [p for p in neighbors if not is_blocked(p)]

#========================================================================== 

# 2 types of heuristics
def manhattan(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def squared_euclidean(p1, p2):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

#========================================================================== 

def return_route(startx, starty, endx, endy):
    global path_pixels
    
    # shrink coordinates 
    start = (startx/size, starty/size)
    goal = (endx/size, endy/size)
    
    # shrink target map image
    img_c = cv2.imread("maptestcolor.png")
    img = cv2.imread("maptest.png",0)
    w,h = img.shape
    w = int(w/size)
    h = int(h/size)
    img = cv2.resize(img, (h,w), interpolation=cv2.INTER_AREA)
    img_c = cv2.resize(img_c, (h,w), interpolation=cv2.INTER_AREA)
    
    # arrays for storing new goal and new starting coordinates
    start_arr = []
    goal_arr = []
    
    # create new coordinates on starting location lot and append into an array
    # right side
    count = 0
    for x in range(start[0],w):
        for y in range(start[1]-1,start[1]):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    start_arr.append((x+5,y))
                break
    # left side
    count = 0
    for x in range(start[0],0,-1):
        for y in range(start[1]-1,start[1]):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    start_arr.append((x-5,y))
                break
    # bottom side
    count = 0
    for x in range(start[0]-1,start[0]):
        for y in range(start[1],h):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    start_arr.append((x,y+5))
                break
    # top side
    count = 0
    for x in range(start[0]-1,start[0]):
        for y in range(start[1],0,-1):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    start_arr.append((x,y-5))
                break
                
    # create new coordinates on destination lot and append into an array
    # right side
    count = 0
    for x in range(goal[0],w):
        for y in range(goal[1]-1,goal[1]):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    goal_arr.append((x+5,y))
                break
    # left side
    count = 0
    for x in range(goal[0],0,-1):
        for y in range(goal[1]-1,goal[1]):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    goal_arr.append((x-5,y))
                break
    # bottom side
    count = 0
    for x in range(goal[0]-1,goal[0]):
        for y in range(goal[1],h):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    goal_arr.append((x,y+5))
                break
    # top side
    count = 0
    for x in range(goal[0]-1,goal[0]):
        for y in range(goal[1],0,-1):
            channels_xy = img[y,x]
            if (channels_xy < 225):    
                count += 1
                if count == 1:
                    goal_arr.append((x,y-5))
                break

    cv2.imwrite("maptest2.png", img)
    cv2.imwrite("maptestcolor2.png", img_c)
    
    # convert image into RGB
    # load image pixel information
    path_img = Image.open("maptest2.png").convert('RGB')
    color_img = Image.open("maptestcolor2.png")
    path_pixels = path_img.load()
    path_pixels_c = color_img.load()
    
    # set distance and heuristic types
#    distance = manhattan
#    heuristic = manhattan
    
    distance = squared_euclidean
    heuristic = squared_euclidean
    
    # obtain A Star shortest path
    path = AStar(start_arr, goal_arr, neighbours_8, distance, heuristic)
    
    print ""
    print "plotting route..."
    
    # plot the path in the color red
    for position in path:
        x,y = position
        path_pixels_c[x,y] = (255,0,0) # red
    
    # save the image with plotted path 
    color_img.save("route.png")
    
#========================================================================== 

# A Star Algorithm
def AStar(start_arr, goal_arr, neighbor_nodes, distance, cost_estimate):
    
    # function to obtain path from start to goal after current node reaches goal 
    def reconstruct_path(came_from, current_node):
        path = []
        
        # while there are still path nodes, append into an array
        while current_node is not None:
            path.append(current_node)
            current_node = came_from[current_node]   
        # return the array that contains path
        return list(reversed(path))
    
    start_time = time.time()
    # for each coordinate in starting coordinates array
    for x in range(0,len(start_arr)):
        start = start_arr[x]
        
        # for each coordinate in goal coordinates array
        for y in range (0,len(goal_arr)):
            goal = goal_arr[y]
            
            # For each node, the cost of getting from the start node to that node. (g score)
            # The cost of going from start to start is zero.
            g_score = {start: 0}    
            
            # For each node, the total cost of getting from the start node to the goal
            # by passing by that node. That value is partly known, partly heuristic. (f score)
            # For the first node, that value is completely heuristic.
            f_score = {start: g_score[start] + cost_estimate(start, goal)}
            
            # The set of currently discovered nodes that are not evaluated yet. (openset)
            # Initially, only the start node is known.
            openset = {start}
            
            #The set of nodes already evaluated (closedSet)
            closedset = set()
            
            # For each node, which node it can most efficiently be reached from. (cameFrom)
            # If a node can be reached from many nodes, cameFrom will eventually contain the
            # most efficient previous step.
            came_from = {start: None}
        
            while openset:
                
                current = min(openset, key=lambda x: f_score[x])
                
                # if goal is reached, return path array
                if current == goal:
                    print "Found path!"
                    print("--- %s seconds ---" % (time.time() - start_time))
                    return reconstruct_path(came_from, goal)
                
                # remove current node from openset and add into closedset
                openset.remove(current)
                closedset.add(current)
                
                # loop through each neighbour
                for neighbor in neighbor_nodes(current):
                    # ignore neighbor which is already evaluated.
                    if neighbor in closedset:
                        continue
                    # add new node to openset
                    if neighbor not in openset:
                        openset.add(neighbor)
                        
                    # The distance from start to a neighbor
                    tentative_g_score = g_score[current] + distance(current, neighbor)
                    
                    # if tentative g score is more than previous neighbour node g score, this is not a better path.
                    if tentative_g_score >= g_score.get(neighbor, float('inf')):
                        continue
                    
                    # resultant node will yield best path, save all info
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + cost_estimate(neighbor, goal)
            
            
            print "cant find path"
    
    # return empty path array if no paths found
    print  ""
    print "no available paths found"
    return []

#========================================================================== 

