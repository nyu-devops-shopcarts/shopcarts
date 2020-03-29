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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return "Reminder: return some useful information in json format about the service here", status.HTTP_200_OK

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
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["DELETE"])
def delete_item(shopcart_id):
    # """
    # Delete a Pet
    # This endpoint will delete a Pet based the id specified in the path
    # """
    app.logger.info("Request to delete an item from the shopping cart")
    #Need to make a class for cart# 
    cart = ShopCart.find(shopcart_id)
    if not cart:
        return make_response("", status.HTTP_204_NO_CONTENT)
    item = CartItem()
    item.deserialize(request.get_json())
    cart.items.remove(item)  # <- we simply append to items list
    cart.save()  


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
