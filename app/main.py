import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

# DATA OBJECT
# {
#     "game": "hairy-cheese",
#     "mode": "advanced",
#     "turn": 4,
#     "height": 20,
#     "width": 30,
#     "snakes": [
#         <Snake Object>, <Snake Object>, ...
#     ],
#     "food": [
#         [1, 2], [9, 3], ...
#     ],
#     "walls": [    // Advanced Only
#         [2, 2]
#     ],
#     "gold": [     // Advanced Only
#         [5, 5]
#     ]
# }

#SNAKE
# {
#     "id": "1234-567890-123456-7890",
#     "name": "Well Documented Snake",
#     "status": "alive",
#     "message": "Moved north",
#     "taunt": "Let's rock!",
#     "age": 56,
#     "health": 83,
#     "coords": [ [1, 1], [1, 2], [2, 2] ],
#     "kills": 4,
#     "food": 12,
#     "gold": 2
# }

def snek_dist(sq1,sq2):
    '''
    takes in two tuples and returns taxicab distance
    '''
    dx = abs(sq1[0]-sq2[0])
    dy = abs(sq1[1]-sq2[1])
    return dx + dy

def one_move(square, direction):
    newSquare = [0,0]
    if direction == "up":
        newSquare[0] = square[0]
        newSquare[1] = square[1] + 1
    elif direction == "down":
        newSquare[0] = square[0]
        newSquare[1] = square[1] - 1
    elif direction == "left":
        newSquare[0] = square[0] - 1
        newSquare[1] = square[1]
    elif direction == "right":
        newSquare[0] = square[0] + 1
        newSquare[1] = square[1]
    return newSquare

def square_is_safe(square, dangerSquares, height, width):
    '''
    takes in danger squares and returns safe squares for a 
    data["height"]xdata["width"] grid
    '''
    safe = True
    if square in dangerSquares:
        safe = False
    if square[0]<0 or square[0]>=width or square[1]<0 or square[1]>=length:
        safe = False
    return safe
#def next_move(snakeHead):
    '''
    out of move options, choose safe square closest to another snake
    '''






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
    print(data.keys())
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """

    dangerSquares = []
    for snek in data['snakes']:
        for square in snek['coords']:
            dangerSquares.append(square)
            
    safeMoves = []
    directions = ['up', 'down', 'left', 'right']
    for direction in directions:
        if square_is_safe(one_move(direction), dangerSquares, data["height"], data["width"]):
            safeMoves.append(direction)
    
    if len(safeMoves) == 0:
        direction = random.choice(directions)
    elif len(safeMoves) == 1:
        direction = safeMoves[0]
    elif len(safeMoves) > 1:
        direction = random.choice(safeMoves)

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
