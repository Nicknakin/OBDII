#!/usr/bin/env pybricks-micropython

#from pybricks.hubs import EV3Brick
#from pybricks.ev3devices import Motor, GyroSensor
#from pybricks.parameters import Port, Stop

import math

"""
Pathfinding Steps:
  ✓ 1) Combine obstacles to reduce compute time
  ✓ 2) Generate outside vertices of obstacle groups
  ✓ 3) Follow visibility graph algorithm to generate paths
  ✓ 4) Search for complete path
  ✓ 5) Convert each leg of path in to movement
"""

#ROBOTICS INSTANTIATION
#ev3 = EV3Brick()
#left_motor = Motor(Port.B)
#right_motor = Motor(Port.C)
#gyro = GyroSensor(Port.S1)

# CONSTANTS
OBST_SIDE = 0.3051
WIDTH = 4.88
HEIGHT = 3.05

SPEED = 360

WHEEL_DIAMETER = 0.07 
AXLE_DIFF = 0.128
ROBOT_WIDTH = 0.16
ROTATION_DISTANCE = math.pi * WHEEL_DIAMETER
ROTATIONS_PER_DEGREE = AXLE_DIFF / WHEEL_DIAMETER / 360

#Rotate by an angle
def rotate(angle):
    #Get number of rotations for a given angle
    rotations = angle*ROTATIONS_PER_DEGREE

    ##Turn the two motors in opposition the same amount to achieve a rotation
    #right_motor.run_angle(SPEED, rotations*360, wait=False)
    #left_motor.run_angle(SPEED, -1*rotations*360)

#def gyroAssisstedRotate(angle):
    #gyro.reset_angle(-angle)
    #while abs(gyro.angle()) > 1 :
        #rotate(-gyro.angle())

#Move the robot a distance
def linearMove(distance):
    #Get the number of rotations needed to move a distance
    rotations = distance/ROTATION_DISTANCE

    ##Rotate both motors the same direction that amount to move forward that distance
    #left_motor.run_angle(SPEED, rotations*360, wait=False)
    #right_motor.run_angle(SPEED, rotations*360)

def edge(point1, point2):
    offset = [point2[0]-point1[0], point2[1]-point1[1]]
    return {
        "offset" : offset,
        "angle" : math.atan2(offset[1], offset[0]),
        "distance" : math.sqrt(offset[0]*offset[0]+offset[1]*offset[1])
    }

#Turn the obstacle locations into a list of groups
def groupObstacles(obstacles):
    #Prepare some groups
    obstacleGroups = []

    for obstacle in obstacles:
        #Check every group to see if there is an adjacent obstacle in that group
        foundGroups = []
        for groupNum, group in enumerate(obstacleGroups):
            #Check every point in the group to see if it adjacent to our current obstacle
            for point in group:
                if (point[0] == obstacle[0] and abs(point[1]-obstacle[1]) < OBST_SIDE) or \
                   (point[1] == obstacle[1] and abs(point[0]-obstacle[0]) < OBST_SIDE):
                    #If it's not already in a group add it to one
                    if not foundGroups:
                        group.append(obstacle)
                    #Keep track of the groups it should be a member of
                    foundGroups.append(groupNum)
                    break

        #If we have found groups merge them
        if foundGroups:
            obstacleGroups.append(sum([obstacleGroups[i] for i in foundGroups], []))
            #Clear out all of the old groups
            foundGroups.reverse()
            for index in foundGroups:
                obstacleGroups.pop(index)
        #Otherwise we need our own group
        else:
            obstacleGroups.append([obstacle])

    return obstacleGroups

#Turn every group in to a set of outer vertices
def generateGroupVertices(group):
    #Prepare a list of vertices
    vertices = []

    #Check all of our points to see if it is a corner piece
    for point in group:
        #Prepare flags to check if our neighbors exist
        directions = [True, True, True, True]

        #Check all the other points
        for otherPoint in group:
            #Ignore ourselves
            if point == otherPoint:
                continue

            #If both points share an X
            if point[0] == otherPoint[0]:
                distance = point[1] - otherPoint[1]
                if distance < OBST_SIDE and distance > 0:
                    directions[2] = False
                if distance > -OBST_SIDE and distance < 0:
                    directions[0] = False

            #If both points share a Y
            if point[1] == otherPoint[1]:
                distance = point[0] - otherPoint[0]
                if distance < OBST_SIDE and distance > 0:
                    directions[1] = False
                if distance > -OBST_SIDE and distance < 0:
                    directions[3] = False

        MARGIN = OBST_SIDE*1.5
        if directions[3]:
            if directions[0]: 
                vertices.append([point[0]+MARGIN, point[1]+MARGIN])
            if directions[2]:
                vertices.append([point[0]+MARGIN, point[1]-MARGIN])
        if directions[1]:
            if directions[0]:
                vertices.append([point[0]-MARGIN, point[1]+MARGIN])
            if directions[2] :
                vertices.append([point[0]-MARGIN, point[1]-MARGIN])

    return vertices;

#Generate a network where every edge is a valid path 
def generateVisibilityGraph(vertices, obstacles):
    #Prepare paths
    paths = []
    #Iterate through vertices
    for vertIndex in range(0, len(vertices)):
        vert = vertices[vertIndex]
        #Iterate through all un-checked other vertices
        for otherVertIndex in range(vertIndex+1, len(vertices)):
            otherVert = vertices[otherVertIndex]
            mainEdge = edge(vert, otherVert)

            #Assume edge is valid
            flag = True
            for obstacle in obstacles:
                otherEdge = edge(vert, obstacle)
                if otherEdge["distance"] < OBST_SIDE:
                    flag = False
                    break

                #Get the angle between the line to the other vertex and the line to the obstacle
                angleDiff = mainEdge["angle"]-otherEdge["angle"]
                
                #See how far away a potential collision would occur
                intersectDist = math.cos(angleDiff)*otherEdge["distance"]
                #If that distance isn't within the range of our line segment then move on
                if intersectDist > mainEdge["distance"]+ROBOT_WIDTH or intersectDist <= -ROBOT_WIDTH:
                    continue
                #Otherwise make sure that the closest point isn't close enough to collide with
                radius = abs(math.sin(angleDiff)*otherEdge["distance"])
                #If it is, then throw it out
                if radius < OBST_SIDE:
                    flag = False
                    break
            #If the flag was never flipped then we can consider this edge A-OK
            if flag:
                paths.append([vert, otherVert])
    return paths

#Basic greedy search, with an optional heuristic list
def search(start, goal, paths, heuristics):
    #Boilerplate for greedy search
    generated = 0
    expanded = 0
    fringe = [{"node": start, "cost": 0, "path":[start]}]
    closedSet = []
    #As long as our fringe has elements
    while fringe:
        #Pop the top element to use for this iteration
        current = fringe.pop(0)
        node = current["node"]
        #If the current node is the goal then we're done
        if node == goal:
            return current
        #Otherwise lets prepare the next nodes to look at
        #If we've looked at this node before then move on, we're not trying to be optimal here
        if node not in closedSet:
            #Note that we've looked at this node now
            closedSet.append(node)
            #For every node that connects to this one prepare a new element for the fringe
            possiblePaths = []
            possiblePaths = list(filter(lambda nodes: node in list(nodes), paths.keys()))
            possiblePaths.sort(key = lambda cityPair: paths[cityPair])
            possiblePaths = list(map(lambda cityPair: {"node": list(cityPair.difference([node]))[0],
                "cost": current["cost"]+paths[cityPair],
                "path": []+(current["path"])+(list(cityPair.difference([node])))}, possiblePaths))
            #If we have a hueristics table then reference that when choosing which next paths to prioritize
            if heuristics:
                possiblePaths.sort(key = lambda city: heuristics[city["node"]])
            #Otherwise lets just throw those on the pile and sort the whole thing, we'll just always take the cheapest path
            fringe.extend(possiblePaths)
            if not heuristics:
                fringe.sort(key = lambda node: node["cost"])
    return None

#Actually navigate the field
def navigateRoute(route, orientation):
    #Iterate over the route such that we can always reference the next element
    for nodeIndex in range(0, len(route)-1):
        #Turn our current segment in to an edge
        path = [route[nodeIndex], route[nodeIndex+1]]
        pathEdge = edge(path[0], path[1])

        #Calculate the angle that we are going to be moving
        newOrientation = pathEdge["angle"]*180/math.pi
        #Rotate by difference in the angle we would like to be and the angle we are
        #gyroAssisstedRotate(newOrientation-orientation)
        #Save new orientation
        orientation = newOrientation
    
        #Move by that amount
        linearMove(pathEdge["distance"])


def main():
    #List of obstacle locations
    #obstacles = [[0.61,2.743],[0.915,2.743],[1.219,2.743],[1.829,1.219],[1.829,1.524],[1.829,1.829],[1.829,2.134],[2.743,0.305],[2.743,0.61],[2.743,0.915],[2.743,2.743],[3.048,2.743],[3.353,2.743]]
    obstacles = [[0.915, 0.305], [0.915, 0.61], [0.915, 0.915], [0.915, 1.22], [0.915, 1.525], [1.829, 1.22], [1.829, 1.525], [1.829, 1.829], [1.829, 2.134], [1.829, 2.439], [1.829, 2.743], [3.048, 1.22], [3.048, 1.525], [3.048, 1.829], [3.353, 0.915], [3.353, 1.22], [3.658, 0.915], [3.658, 1.22]]

    start = [0.305, 0.61]
    end = [3.658, 1.829]
    orientation = 90
    
    #Group our obstacles
    groups = groupObstacles(obstacles)
    print(f"groups = {groups}\n")
    
    #Turn our obstacle groups in to vertices
    groupVertices = list(map(generateGroupVertices, groups))
    print(f"groupVertices = {groupVertices}\n")

    #Convert group vertices in to a 1d array, remove any that are out of bounds
    groupVertices.append([start, end])
    vertices = sum(groupVertices, [])
    vertices = list(filter(lambda vertex: \
            vertex[0] > ROBOT_WIDTH/2 and vertex[0] < WIDTH-ROBOT_WIDTH/2 and \
            vertex[1] > ROBOT_WIDTH/2 and vertex[1] < HEIGHT-ROBOT_WIDTH/2, \
            vertices))
    
    #Generate valid paths between obstacle vertices
    paths = generateVisibilityGraph(vertices, obstacles)
    print(f"graph = {paths}\n")

    #Prepare a heuristics object using distance squared
    heuristics = dict(map(lambda vertex: (str(vertex), (vertex[0]-end[0])**2+(vertex[1]-end[1])**2), vertices))
    #Prepare a modified paths object using frozensets
    modifiedPaths = dict(map(lambda path: \
            (frozenset(map(str, path)),\
            (path[0][0]-path[1][0])**2+(path[0][1]-path[1][1])**2,),\
            paths))

    #Pick a route through the paths
    route = search(str(start), str(end), modifiedPaths, heuristics)["path"]
    #Convert the weirdly formatted output to be a happy list again
    route = list(map(lambda point: list(map(float, point[1:-1].split(','))), route))
    print(f"route = {route}\n")

    #Navigate route
    navigateRoute(route, orientation)

if __name__ == "__main__":
    main()
