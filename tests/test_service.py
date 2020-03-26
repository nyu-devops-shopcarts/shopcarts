"""
<your resource name> API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service.models import ShopCart, CartItem
from tests.factories import ShopCartFactory, CartItemFactory
from flask_api import status  # HTTP Status Codes
from service.models import db
from service.service import app, init_db

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()


    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # def test_create_shopcart(self):
    #     """ Create a new ShopCart """
    #     test_cart = ShopCartFactory()
    #     resp = self.app.post(
    #         "/shopcarts", 
    #         json=test_cart.serialize(), 
    #         content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


    #     Make sure location header is set
    #     location = resp.headers.get("Location", None)
    #     self.assertIsNotNone(location)
        
    #     Check the data is correct
    #     new_shopcart = resp.get_json()
    #     self.assertEqual(new_shopcart["items"], shopcart.items, "Names does not match")
    #     Add for other attributes

    #     Check that the location header was correct by getting it
    #     resp = self.app.get(location, content_type="application/json")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     new_shopcart = resp.get_json()
    #     self.assertEqual(new_shopcart["items"], shopcart.items, "Names does not match")
        
