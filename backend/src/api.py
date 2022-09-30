from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks_list():
    drinks_query = Drink.query.order_by(Drink.id).all()
    # Loop through all the items in drink query using list comprehension
    drinks = [drink.short() for drink in drinks_query]

    # If there are no drinks in the list, 
    # it will abort the request indicating a 404 error
    if len(drinks) == 0:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": drinks
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drink_detail(payload):
    drinks_query = Drink.query.order_by(Drink.id).all()
    drinks = [drink.long() for drink in drinks_query]

    # If there are no drinks in the list, 
    # it will abort the request indicating a 404 error
    if len(drinks) == 0:
        abort(404)       

    return jsonify({
        "success": True, 
        "drinks": drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # Get request body with request.get_json()
    try:
        body = request.get_json()

        title = body.get('title', None)
        # We serialize the recipe request object and turn it into a json string
        # so it can be processed into the database as a string rather than a list of dictionary... 

        # Here I also allowed the request to be `None` 
        # in case the client might decide to not to add a recipe
        recipe = json.dumps(body.get('recipe', None))

        new_added_drink = Drink(title=title, recipe=recipe)

        new_added_drink.insert()

        return jsonify({
            "success": True, 
            "drinks": [new_added_drink.long()] # drink an array containing only the newly created drink
        })
    except Exception:
        abort(400) # Aborts a 400 bad request error if request is not processed





'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):

    body = request.get_json()

    if not body:
        abort(400)

    title = body.get('title', None)
    # We serialize the recipe request object and turn it into a json string
    # so it can be processed into the database as a string rather than a list of dictionary... 

    # Here I also allowed the request to be `None` 
    # in case the client might decide to not to add a recipe 
    recipe = json.dumps(body.get('recipe', None))

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.title = title
    drink.recipe = recipe

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [ drink.long() ] # where drink is an array containing only the updated drink
    })


    


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404) # Aborts a 404 not found error if drink query is not found

        drink.delete()

    except:
        abort(422) # Aborts a 422 unprocessible error if request is not processed

    return jsonify({
        "success": True, 
        "delete": drink_id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
each error handler should return (with approprate messages):
    jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

# All Error Handlers 

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessible"
    }), 422

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized user"
    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(403)
def forbidden_request(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden request"
    }), 403


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500



if __name__ == "__main__":
    app.debug = True
    app.run()
