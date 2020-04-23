"""
ShopCarts Service

<Describe what your service does here>

Paths:

DELETE /shopcarts/{id}/items/{id}

"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import ShopCart, CartItem, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

#---------------------------------------------------------------------
#                S H O P C A R T   M E T H O D S
#---------------------------------------------------------------------


######################################################################
# CREATE A SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a shopping cart
    This endpoint will create a Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create a ShopCart")
    app.logger.info(request.get_json())
    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    shopcart.create()
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    ) 

######################################################################
# RETRIEVE A SHOPCART - Robert UNG
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single ShopCart
    This endpoint will return an ShopCart based on its id
    """
    app.logger.info("Request for ShopCart with id: %s", shopcart_id)
    shopcart = ShopCart.find_or_404(shopcart_id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING SHOPCART - Neil Vijapura
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update an existing shopcart
    This endpoint will update an shopcart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    check_content_type("application/json")
    shopcart = ShopCart.find(shopcart_id)
    if not shopcart:
        raise NotFound("ShopCart with id '{}' was not found.".format(shopcart_id))
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.save()
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A SHOPCART - Robert Ung
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a shopcart
    This endpoint will delete an shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", shopcart_id)
    shopcart = ShopCart.find(shopcart_id)
    if shopcart:
        shopcart.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# LIST ALL ShopCarts - Neil Vijpapura
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """ Returns IDs of the ShopCarts """
    app.logger.info("Request for ShopCart list")
    shopcarts = []
    id = request.args.get("id")
    if id:
        shopcarts = ShopCart.find(id)
    else:
        shopcarts = ShopCart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)  


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    ShopCart.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
#---------------------------------------------------------------------
#                C A R T  I T E M   M E T H O D S
#---------------------------------------------------------------------

######################################################################
# ADD AN ITEM TO A SHOPCART
######################################################################
@app.route('/shopcarts/<int:shopcart_id>/items', methods=['POST'])
def create_items(shopcart_id):
    """
    Create an Item in a Shopcart
    This endpoint will add an item to a shopcart
    """
    app.logger.info("Request to add an item to a shopcart")
    check_content_type("application/json")
    shopcart = ShopCart.find_or_404(shopcart_id)
    item = CartItem()
    item.deserialize(request.get_json())
    shopcart.items.append(item)
    shopcart.save()
    message = item.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# RETRIEVE AN ITEM FROM A SHOPCART
######################################################################
@app.route('/shopcarts/<int:shopcart_id>/items/<int:item_id>', methods=['GET'])
def get_addresses(shopcart_id, item_id):
    """
    Get an Item
    This endpoint returns just an item
    """
    app.logger.info("Request to get an item with id: %s", item_id)
    item = CartItem.find_or_404(item_id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", shopcart_id)
    item = CartItem.find(item_id)
    if item:
        item.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# LIST ALL ITEMS FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """ Returns all of the items within the shopcart """
    app.logger.info("Request to list items from the shopping cart")

    shopcart = ShopCart.find_or_404(shopcart_id)
    results = [item.serialize() for item in shopcart.items]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_items (shopcart_id, item_id):
    """
    Update an Item
    This endpoint will update an item based the body that is posted
    """
    app.logger.info("Request to update item with id: %s", item_id)
    check_content_type("application/json")
    item = CartItem.find_or_404(item_id)
    item.deserialize(request.get_json())
    item.id = item_id
    item.save()
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# CLEAR ALL ITEMS FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/clear", methods=["PUT"])
def clear_shopcart (shopcart_id):
    """ Returns all of the items within the shopcart """
    app.logger.info("Request to clear items from the shopping cart")

    shopcart = ShopCart.find_or_404(shopcart_id)
    results = [item.delete() for item in shopcart.items]
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# CLEAR ALL SHOPCARTS
######################################################################
@app.route("/shopcarts/clear", methods=["PUT"])
def clear_shopcart (shopcart_id):
    """ Returns all of the items within the shopcart """
    app.logger.info("Request to clear items from the shopping cart")

    shopcart = ShopCart.find_or_404(shopcart_id)
    results = [item.delete() for item in shopcart.items]
    return make_response("", status.HTTP_204_NO_CONTENT)


LIST
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """ Returns IDs of the ShopCarts """
    app.logger.info("Request for ShopCart list")
    shopcarts = []
    id = request.args.get("id")
    if id:
        shopcarts = ShopCart.find(id)
    else:
        shopcarts = ShopCart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)  