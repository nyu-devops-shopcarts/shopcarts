"""
<your resource name> API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service.models import ShopCart, CartItem
from tests.factories import ShopCartFactory, CartItemFactory
from flask_api import status  # HTTP Status Codes
from service.models import db
from service.service import app, init_db

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')


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
        """ Factory method to create ShopCarts in bulk """
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
#  S H O P C A R T   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_shopcart(self):
        """ Create a ShopCart  """
        shopcart = ShopCartFactory()
        resp = self.app.post(
            "/shopcarts", 
            json=shopcart.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        
        #Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["items"], shopcart.items, "Items do not match")
        self.assertEqual(new_shopcart["customer_id"], shopcart.customer_id, "Customer ID does not match")

        #Check that the location header was correct by getting it
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["items"], shopcart.items, "Names does not match")
        self.assertEqual(new_shopcart["customer_id"], shopcart.customer_id, "Customer ID does not match")

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
        """ Get a Shopcart that is not found """
        resp = self.app.get("/shopcarts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart(self):
        """ Update an existing ShopCart """
        # create a ShopCart to update
        test_shopcart = ShopCartFactory()
        resp = self.app.post(
            "/shopcarts", 
            json=test_shopcart.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the ShopCart
        new_shopcart = resp.get_json()
        new_shopcart["customer_id"] = 12345678
        resp = self.app.put(
            "/shopcarts/{}".format(new_shopcart["id"]),
            json=new_shopcart,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["customer_id"],12345678)

#### Delete 
    def test_delete_shopcart(self):
        """ Delete a ShopCart """
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.app.delete(
            "/shopcarts/{}".format(shopcart.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

#### List
    def test_get_shopcart_list(self):
        """ Get list of ShopCarts """
        self._create_shopcarts(5)
        resp = self.app.get("/shopcarts")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_bad_request(self):
        """ Send wrong media type """
        shopcart = ShopCartFactory()
        resp = self.app.post(
            "/shopcarts", 
            json={"name": "not enough data"}, ###name should be changed?
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """ Send wrong media type """
        shopcart = ShopCartFactory()
        resp = self.app.post(
            "/shopcarts", 
            json=shopcart.serialize(), 
            content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """ Make an illegal method call """
        resp = self.app.put(
            "/shopcarts", 
            json={"not": "today"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#  C A R T I T E M   T E S T   C A S E S   H E R E 
######################################################################

    def test_add_item(self):
        """ Add an item to a ShopCart """
        shopcart = self._create_shopcarts(1)[0]
        item = CartItemFactory()
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["item_name"], item.item_name)
        self.assertEqual(data["sku"], item.sku)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_get_item(self):
        """ Get an item from a ShopCart """
        # create a known address
        shopcart = self._create_shopcarts(1)[0]
        item = CartItemFactory()
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(shopcart.id, item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["item_name"], item.item_name)
        self.assertEqual(data["sku"], item.sku)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_update_item(self):
        """ Update an item in a ShopCart """
        # create a known address
        shopcart = self._create_shopcarts(1)[0]
        item = CartItemFactory()
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["item_name"] = "item_name"

        # send the update back
        resp = self.app.put(
            "/shopcarts/{}/items/{}".format(shopcart.id, item_id), 
            json=data, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(shopcart.id, item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["item_name"], "item_name")

##### Listing Test Case ## 
    def test_get_shopcart_items_list(self):
        """ Get a list of Items in a ShopCart """
        # add two addresses to account
        shopcart = self._create_shopcarts(1)[0]
        item_list = CartItemFactory.create_batch(2)

        # Create item 1
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item_list[0].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item_list[1].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.app.get(
            "/shopcarts/{}/items".format(shopcart.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_delete_item(self):
        """ Delete an Item """
        shopcart = self._create_shopcarts(1)[0]
        item = CartItemFactory()
        resp = self.app.post(
            "/shopcarts/{}/items".format(shopcart.id), 
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.app.delete(
            "/shopcarts/{}/items/{}".format(shopcart.id, item_id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(shopcart.id, item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)