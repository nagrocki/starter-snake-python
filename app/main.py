import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


def snek_dist(sq1,sq2):
    '''
    takes in two tuples and returns taxicab distance
    '''
    dx = abs(sq1["x"]-sq2["x"])
    dy = abs(sq1["y"]-sq2["y"])
    return dx + dy

def one_move(square, direction):
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
    '''
    takes in danger squares and returns safe squares for a 
    data["height"]xdata["width"] grid
    '''
    safe = True
    for dSquare in dangerSquares:
        if dSquare["x"] == square["x"] and dSquare["y"] == square["y"]:
            safe = False
    if square["x"]<0 or square["x"]>=width or square["y"]<0 or square["y"]>=height:
        safe = False
    return safe

def square_score(square, scarySneks, yummySneks):
    score = 0
    for snek in scarySneks:
        score = score + snek_dist(square, snek[0])
    for snek in yummySneks:
        score = score - snek_dist(square, snek[0])
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

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    dangerSquares = []
    for snek in data['board']['snakes']:    #other sneks not safe
        for square in snek['body']:
            dangerSquares.append(square)
    for square in data['you']['body']:    ##head and body not safe 
        dangerSquares.append(square)
        
    currentSquare = data['you']['body'][0]    ##my head
    
    myLength = len(data['you']['body'])
    
    scarySneks = []
    yummySneks = []
    for snek in data['board']['snakes']:
        if len(snek['body'])>= myLength:
            scarySneks.append(snek['body'])
        else:
            yummySneks.append(snek['body'])
    
    
    safeMoves = []
    directions = ['up', 'down', 'left', 'right']
    for move in directions:
        if square_is_safe(one_move(currentSquare, move), \
                          dangerSquares, data['board']["height"], \
                          data['board']["width"]):
            safeMoves.append(move)
    
    if len(safeMoves) == 0:
        direction = random.choice(directions)
    elif len(safeMoves) == 1:
        direction = safeMoves[0]
    elif len(safeMoves) > 1:
        direction = safeMoves[0]
        for move in safeMoves:
            if square_score(one_move(currentSquare, move), scarySneks, yummySneks) > \
            square_score(one_move(currentSquare, direction), scarySneks, yummySneks):
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
