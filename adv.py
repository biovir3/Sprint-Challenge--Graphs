from room import Room
from player import Player
from world import World
import queue
import random
from ast import literal_eval
from collections import deque

class Queue:
    def __init__(self):
        self.queue = []
    def enqueue(self, value):
        self.queue.append(value)
    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None
    def size(self):
        return len(self.queue)

world = World()

# You may uncomment the smaller maps for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_map=literal_eval(open(map_file, "r").read())
world.load_graph(room_map)

# Print an ASCII map
#world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []







#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")

# if we have come to a dead end, we need to go back to the most recent unexplored direction
# backtrack will put the moves required for getting to this room into the move queue variable
def backtrack(player):
    # create a Queue for the backtrack
    q = Queue()
    # create a visited set
    visited = set()
    # enqueue our current room
    q.enqueue([player.current_room.id])
    while q.size() > 0:
        # Set our path to the top of the queue
        path = q.dequeue()
        # now we start walking backwards
        last_room = path[-1]
        if last_room not in visited:
            visited.add(last_room)
            # If there is an exit in the room, we have gotten to our last room, and we need to start exploring from here
            for exit in map[last_room]:
                if map[last_room][exit] == "?":
                    return path
                else:
                    dup_path = list(path)
                    dup_path.append(map[last_room][exit])
                    q.enqueue(dup_path)
    return [] # if q ever gets to 0 meaning we have no new rooms to explore our algorithm is over

# The walk function gets our next move to room, if we are at a dead end, it sets move to the path that will take
# us to the last unexplored portion of the maze
def walk(player, move):
    # Gets curent room and checks for directions it can move from the current room
    currentRoomExits = map[player.current_room.id]
    unexploredExits = []
    for dir in currentRoomExits:
        if currentRoomExits[dir] == "?":
            unexploredExits.append(dir)
    # If there are no unexplored exits in the room, it will call backtrack to get the moves to go to the last unexplored
    # room
    if len(unexploredExits) == 0:
        # Our backtrack function gives us the rooms back to the last unexplored exit
        path_to_unexplored = backtrack(player)
        room_on_path = player.current_room.id
        # We need to set our moves queue so that our for loop can know how to get back.
        for next_room in path_to_unexplored:
            for dir in map[room_on_path]:
                if map[room_on_path][dir] == next_room:
                    move.enqueue(dir)
                    room_on_path = next_room
                    break
    # If there are unexplored exits to the current room, it will randomly pick one, and that is the direction we will
    # travel
    else:
        move.enqueue(unexploredExits[random.randint(0, len(unexploredExits) - 1)])

# For loop to find the Best path out of the traversal_paths tested

numTrials = 500
bestLen = 9999
bestPath = []

for i in range(numTrials):
    # Create Player object to move through the maze
    player = Player(world.starting_room)
    # Create our map to traverse the maze
    map = {}

    # newRoom has to be initialized to work with the function
    newRoom = {}
    # This for loop initializes the exits to be explored in the room
    for dir in player.current_room.get_exits():
        newRoom[dir] = "?"
    # Finally we set our new room in our map
    map[world.starting_room.id] = newRoom

    # move is a Queue to hold our move to make
    # a list to hold our traversal path
    move = Queue()
    traversal_path = []
    # Now walk is called to set the move to travel in, and check if we are at a dead end and need to backtrack
    walk(player, move)

    inverse_directions = {"n": "s", "s": "n", "e": "w", "w": "e"}

    # The while loop moves us through the maze using the walk function to give us the direction to walk in.
    # The walk function also tells us if we need to backtrack because we have hit a deadend.

    while move.size() > 0:
        # set current room
        startRoom = player.current_room.id
        # pull our next move from the move queue
        nextMove = move.dequeue()
        # Call the travel method to move our player in the maze
        player.travel(nextMove)
        # append our move to the traversal_path
        traversal_path.append(nextMove)
        # Set our new room to end room
        endRoom = player.current_room.id
        # Add the room we are now in to the map
        map[startRoom][nextMove] = endRoom
        # Set all exits to the room we are in now to un checked '?'
        if endRoom not in map:
            map[endRoom] = {}
            for exit in player.current_room.get_exits():
                map[endRoom][exit] = "?"
        # set the link in our map of the direction we came from the the previous room
        map[endRoom][inverse_directions[nextMove]] = startRoom
        # Now that we have moved, we need to call walk to get our next move to point,
        if move.size() == 0:
            walk(player, move)

    if len(traversal_path) < bestLen:
        bestPath = traversal_path
        bestLen = len(traversal_path)


# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in bestPath:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_map):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_map) - len(visited_rooms)} unvisited rooms")

print(bestPath)
print(traversal_path)