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
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    ShopCart.init_db(app)
