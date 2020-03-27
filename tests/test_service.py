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

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()


    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()
        pass

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_shopcarts(self, count):
        """ Factory method to create shopcarts in bulk """
        shopcarts = []
        for _ in range(count):
            shopcart = ShopCartFactory()
            resp = self.app.post(
                "/shopcarts", json=shopcart.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Shopcart"
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcarts.append(shopcart)
        return shopcarts

######################################################################
#  SHOPCART   T E S T   C A S E S   H E R E 
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

    def test_get_shopcart(self):
        """ Get a single ShopCart """
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.app.get(
            "/shopcarts/{}".format(shopcart.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], shopcart.id)
    
    def test_get_shopcart_not_found(self):
        """ Get an Shopcart that is not found """
        resp = self.app.get("/shopcarts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

######################################################################
#  CART ITEM   T E S T   C A S E S   H E R E 
######################################################################