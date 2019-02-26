import json
import os
import bottle

from api import ping_response, start_response, move_response, end_response

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
    #print(json.dumps(data))

    color = "#93abe1"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    #print(json.dumps(data))
    body = data["you"]["body"]
    head = body[0]
    board = data["board"]
    food_locations = data["board"]["food"]
    nearest_food = calculate_nearest_food(food_locations, head)
    direction = generate_next_move(nearest_food, body)
    print(data["turn"])
    #print(direction)
    direction = correct_path(direction, body, board)
    #print(direction)


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

def calculate_nearest_food(food_locations, head):
    min = abs(food_locations[0]["x"] - head["x"]) + abs(food_locations[0]["y"] - head["y"])
    min_index = 0
    for food in food_locations:
        dist = abs(food["x"] - head["x"]) + abs(food["y"] - head["y"])
        if dist <= min:
            min = dist
            min_index = food_locations.index(food)
    return (food_locations[min_index])

def generate_next_move(nearest_food, body):
    head = body[0]
    if ((head["x"] == nearest_food["x"]) and (head["y"] != nearest_food["y"])):
        if (head["y"] > nearest_food["y"]):
            output = "up"
        else:
            output = "down"
    elif ((head["y"] == nearest_food["y"])and (head["x"] != nearest_food["x"])):
        if (head["x"] > nearest_food["x"]):
            output = "left"
        else:
            output = "right"
    else:
        if abs(head["x"] - nearest_food["x"]) <= abs(head["y"] - nearest_food["y"]):
            if (head["x"] > nearest_food["x"]):
                output = "left"
            else:
                output = "right"
        else:
            if (head["y"] > nearest_food["y"]):
                output = "up"
            else:
                output = "down"
    return output

def correct_path(direction, body, board):
    head = body[0]
    enemies = board["snakes"]
    if direction == "up":
        next_place = {"x": head["x"], "y": head["y"] - 1}
        if next_place in body or next_place["y"] == -1:
            direction = "right"
            print(direction)
            return correct_path(direction, body, board)
        else:
            return direction
    elif direction == "down":
        next_place = {"x": head["x"], "y": head["y"] + 1}
        if next_place in body or next_place["y"] == board["height"]:
            direction = "left"
            print(direction)
            return correct_path(direction, body, board)
        else:

            return direction
    elif direction == "right":
        next_place = {"x": head["x"] + 1, "y": head["y"]}
        if next_place in body or next_place["x"] == board["width"]:
            direction = "down"
            print(direction)
            return correct_path(direction, body, board)
        else:
            return direction
    elif direction == "left":
        next_place = {"x": head["x"] - 1, "y": head["y"]}
        if next_place in body or next_place["x"] == -1:
            direction = "up"
            print(direction)
            return correct_path(direction, body, board)
        else:
            return direction

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
