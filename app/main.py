import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

"""
    TODO:
        
        -Check for certain victory (a move which will land on a yummy enemy snake guaranteed)
        
        -alter behaviour based on hunger
        
"""
"""
   returns all of the length n paths from square
   any given path contains no cycles, but two paths can share squares
"""
    
def length_n_paths(square, length, dangerSquares, height, width):
    directions = ["up", "down", "left", "right"]
    
    safeMoves = safe_moves(square, dangerSquares, height, width)
    paths = []
    for move in safeMoves:
        startPath = [one_move(square, move)]
        paths.append(startPath)
        
    for i in range(length-1):
        longerPaths = []
        for path in paths:
            frontier = path[-1]
            safeMoves = safe_moves(frontier, dangerSquares, height, width)
            for move in safeMoves:
                nextSquare = one_move(square, move)
                if nextSquare not in path:
                    newPath = list(path)
                    newPath.append(nextSquare)
                longerPaths.append(newPath)
        paths = longerPaths
        
    return paths

def BFS_dist(source, sink, maxLen, dangerSquares, height, width):
    """
       returns bfs search distance, no more than maxLen squares


       TODO: return error instead of infinity?
    """
    directions = ["up", "down", "left", "right"]
    
    safeMoves = safe_moves(source, dangerSquares, height, width)
    paths = []
    discoveredSquares = []
    for move in directions:
        firstStep = one_move(source, move)
        if firstStep == sink:
            return 1    # returns 1 if sink is adjacent to source
    
    for move in safeMoves:
        firstStep = one_move(source, move)
        discoveredSquares.append(firstStep)
        startPath = [firstStep]
        paths.append(startPath)
        
    ## at this stage paths contains lists, each with a 'safe' adjacent square to the source    
    for i in range(2, maxLen + 1):
        longerPaths = []
        for path in paths:
            frontier = path[-1]    ## for each path, the frontier is the last visited square in the path
            
            for move in directions:
                nextSquare = one_move(frontier, move)
                if nextSquare is sink:
                    return i
                
            safeMoves = safe_moves(frontier, dangerSquares, height, width)
            for move in safeMoves:
                nextSquare = one_move(frontier, move)
                if nextSquare not in discoveredSquares:
                    newPath = list(path)
                    newPath.append(nextSquare)
                    discoveredSquares.append(nextSquare)
                    longerPaths.append(newPath)
        paths = longerPaths               ## next time through the loop, we will build off new longer paths
        if len(paths) == 0:
            return float("inf")    ##if no paths from source to sink, distance = infinity
    return i    ## returns maxLen if no path found before maxLen

def score_path(path, scarySneks, yummySneks, foods):
    score = 0
    for square in path:
        score = score + square_score(square, scarySneks, yummySneks, foods)
            
            ##TODO update square score to measure distance wth distace matric built by BFS search
    

def snek_dist(sq1,sq2):
    """
    takes in two x,y tuples and returns taxicab distance (totally ignores snakes)
    """
    dx = abs(sq1["x"]-sq2["x"])
    dy = abs(sq1["y"]-sq2["y"])
    return dx + dy

def one_move(square, direction):
    """
    takes in a square and a direction and returns the square one step in that direction
    """
    newSquare = {"x": 0, "y":0}
    if direction == "up":
        newSquare["x"] = square["x"]
        newSquare["y"] = square["y"] - 1
    elif direction == "down":
        newSquare["x"] = square["x"]
        newSquare["y"] = square["y"] + 1
    elif direction == "left":
        newSquare["x"] = square["x"] - 1
        newSquare["y"] = square["y"]
    elif direction == "right":
        newSquare["x"] = square["x"] + 1
        newSquare["y"] = square["y"]
    return newSquare

def square_is_safe(square, dangerSquares, height, width):
    """
    takes in a square and the danger squares and the height and width of the 
    data["height"]xdata["width"] grid,
    returns True if square is potentially a safe move for the next turn.
    
    *This function does not check for squares adjacent to enemy snake heads*
    """
    safe = True
    for dSquare in dangerSquares:
        if dSquare["x"] == square["x"] and dSquare["y"] == square["y"]:
            safe = False
    if square["x"]<0 or square["x"]>=width or square["y"]<0 or square["y"]>=height:
        safe = False
    return safe

def save_moves(currentSquare, dangerSquares, height, width):
    safeMoves = []
    directions = ['up', 'down', 'left', 'right']
    for move in directions:
        if square_is_safe(one_move(currentSquare, move), \
                          dangerSquares, height, width):
            safeMoves.append(move)
    
    return safeMoves


def bfs_square_score(square, scarySneks, yummySneks, foods, dangerSquares, height, width):
    """
    This functon scores a square based on how close it is to food, bigger snakes,
    and smaller snakes. A higher score should correspond to a better move.
    """
    
    score = 0
    for snek in scarySneks:
        if BFS_dist(square, snek[0], 10, dangerSquares, height, width) == 1:
            score = score - 4
        else:
            score = score - 4/(BFS_dist(square, snek[0], 10, dangerSquares, height, width))**2 #run from head
            
        if BFS_dist(square, snek[0], 10, dangerSquares, height, width) == 0:                  #run to tail
            score = score + 3
        elif BFS_dist(square, snek[0], 10, dangerSquares, height, width) == 1:
            score = score + 1   
            
            
    for snek in yummySneks:
        if BFS_dist(square, snek[0], 10, dangerSquares, height, width) == 1:
            score = score + 4
        else:
            score = score + 4/(BFS_dist(square, snek[0], 10, dangerSquares, height, width))**2

    for food in foods:
        if BFS_dist(square, food, 10, dangerSquares, height, width) == 0:
            score = score + 5
        else:
            score = score + 4/BFS_dist(square, food, 10, dangerSquares, height, width)
    return score
               
def square_score(square, scarySneks, yummySneks, foods):
    """
    This functon scores a square based on how close it is to food, bigger snakes,
    and smaller snakes. A higher score should correspond to a better move.
    """
    
    score = 0
    for snek in scarySneks:
        if snek_dist(square, snek[0]) == 1:
            score = score - 4
        else:
            score = score - 4/(snek_dist(square, snek[0]))**2 #run from head
            
        if snek_dist(square, snek[-1]) == 0:                  #run to tail
            score = score + 3
        elif snek_dist(square, snek[-1]) == 1:
            score = score + 1   
            
            
    for snek in yummySneks:
        if snek_dist(square, snek[0]) == 1:
            score = score + 4
        else:
            score = score + 4/(snek_dist(square, snek[0]))**2

    for food in foods:
        if snek_dist(square, food) == 0:
            score = score + 5
        else:
            score = score + 4/snek_dist(square, food)
    return score

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    color = "#6B5B95"
    headType = "silly"
    tailType = "freckled"
    return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
    data = bottle.request.json

    dangerSquares = []
    for snek in data['board']['snakes']:    #other sneks not safe (but tail is cool)
        for square in snek['body'][:-1]:
            dangerSquares.append(square)
    for square in data['you']['body'][:-1]:     #my snek not safe (but tail is cool)
        dangerSquares.append(square)
        
    currentSquare = data['you']['body'][0]    ##my head
    foods = data['board']['food']
    myLength = len(data['you']['body'])
    
    scarySneks = []
    yummySneks = []
    for snek in data['board']['snakes']:
        if len(snek['body'])>= myLength and snek['id'] != data['you']['id']:
            scarySneks.append(snek['body'])
        elif len(snek['body'])< myLength and snek['id'] != data['you']['id']:
            yummySneks.append(snek['body'])
    
    
    safeMoves = safe_moves(currentSquare, dangerSquares, data['board']['height'], data['board']['width'])
    
    if len(safeMoves) == 0:
        direction = random.choice(directions)    # when there are no safe moves, chaos ensues
    elif len(safeMoves) == 1:
        direction = safeMoves[0]                 # take the only safe move if that's the only choice!
    elif len(safeMoves) > 1:
        direction = safeMoves[0]
        for move in safeMoves:
            if square_score(one_move(currentSquare, move), scarySneks, yummySneks, foods) > \
            square_score(one_move(currentSquare, direction), scarySneks, yummySneks, foods):
                direction = move
               
                
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()



if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
