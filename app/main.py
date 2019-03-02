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
    myName = data["you"]["name"]
    head = body[0]
    board = data["board"]
    food_locations = data["board"]["food"]
    health = data["you"]["health"]
    x = 5
    y = 15
    nearest_food = calculate_nearest_food(food_locations, head)
    direction = generate_next_move(nearest_food, body)
    print(data["turn"])
    #print(direction)
    count = 0
    direction = correct_path(direction, body, board, nearest_food, count, myName)
    #print(direction)

    # if (len(food_locations) == 0):
    #     direction = coil()
    # else:
    #     if (len(snake) >= x):
    #         if (health < distance_to_nearest_food + y):
    #             direction = coil()
    #         else:
    #             direction = move_to_food()
    #     else:
    #         direction = move_to_food()
    #
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

def correct_path(direction, body, board,nearest_food, count, myName):
    print(count)
    if count < 4:
        head = body[0]
        enemy_coords = []
        enemy_heads = []
        enemies = board["snakes"]
        for enemy in enemies:

            if enemy["name"] != myName:
                if enemy["body"][0] not in board["food"]:
                    for i in range(len(enemy["body"]) - 1):
                        if i == 0:
                            enemy_heads.append(enemy["body"][i])
                        enemy_coords.append(enemy["body"][i])
                else:
                    for i in range(len(enemy["body"])):
                        if i == 0:
                            enemy_heads.append(enemy["body"][i])
                        enemy_coords.append(enemy["body"][i])



        if direction == "up":
            next_place = {"x": head["x"], "y": head["y"] - 1}
            if next_place in body or next_place["y"] == -1 or next_place in enemy_coords or surround_check(enemy_heads, next_place, nearest_food):
                direction = "right"
                count += 1
                return correct_path(direction, body, board, nearest_food, count, myName)
            else:
                return direction

        elif direction == "down":
            next_place = {"x": head["x"], "y": head["y"] + 1}
            if next_place in body or next_place["y"] == board["height"] or next_place in enemy_coords or surround_check(enemy_heads, next_place, nearest_food):
                direction = "left"
                count += 1
                return correct_path(direction, body, board, nearest_food, count, myName)
            else:
                return direction

        elif direction == "right":
            next_place = {"x": head["x"] + 1, "y": head["y"]}
            if next_place in body or next_place["x"] == board["width"] or next_place in enemy_coords or surround_check(enemy_heads, next_place, nearest_food):
                direction = "down"
                count += 1
                return correct_path(direction, body, board, nearest_food, count, myName)
            else:
                return direction

        elif direction == "left":
            next_place = {"x": head["x"] - 1, "y": head["y"]}
            if next_place in body or next_place["x"] == -1 or next_place in enemy_coords or surround_check(enemy_heads, next_place, nearest_food):
                direction = "up"
                count += 1
                return correct_path(direction, body, board, nearest_food, count, myName)
            else:
                return direction
    else:
        return direction

def surround_check(enemy_heads, next_place, nearest_food):
    if next_place == nearest_food:
        surround = []
        surround.append({"x": next_place["x"] + 1, "y": next_place["y"]})
        surround.append({"x": next_place["x"] - 1, "y": next_place["y"]})
        surround.append({"x": next_place["x"], "y": next_place["y"] + 1})
        surround.append({"x": next_place["x"], "y": next_place["y"] - 1})
        for coord in surround:
            if coord in enemy_heads:
                return True
    return False






if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
