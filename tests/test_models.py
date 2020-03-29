"""
Test cases for ShopCart and CartItem Models

"""
import logging
import unittest
import os
from service import app
from service.models import ShopCart, CartItem, DataValidationError, db
from tests.factories import ShopCartFactory, CartItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopCart(unittest.TestCase):
    """ Test Cases for ShopCart Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        ShopCart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
#####################################################################
    
    def _create_shopcart(self, items=[]):
        """ Creates a ShopCart from Factory """
        fake_shopcart = ShopCartFactory()
        shopcart = ShopCart(
            customer_id = fake_shopcart.customer_id,
            items = items
        )
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.id, None)
        return shopcart

    def _create_item(self):
        """ Creates a CartItem from Factory """
        fake_item= CartItemFactory()
        item = CartItem(
            shopcart_id = fake_item.shopcart_id,
            item_name = fake_item.item_name,
            sku = fake_item.sku,
            quantity = fake_item.quantity,
            price = fake_item.price
        )
        self.assertTrue(item != None)
        self.assertEqual(item.id, None)
        return item

######################################################################
#  C A R T  &  I T E M   T E S T   C A S E S   H E R E
######################################################################
    def test_create_shopcart(self):
        """ Create a ShopCart -- Asserts that it exists """
        fake_shopcart = ShopCartFactory()
        shopcart = ShopCart(
            customer_id = fake_shopcart.customer_id
        )
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.customer_id, fake_shopcart.customer_id)

    def test_add_shopcart(self):
        """ Create a ShopCart -- Add it to the database """
        shopcarts = ShopCart.all()
        self.assertEqual(shopcarts, [])
        shopcart = self._create_shopcart()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(shopcart.id, 1)
        shopcarts = ShopCart.all()
        self.assertEqual(len(shopcarts), 1)

    def test_serialize_cart(self):
        """ Serializes a ShopCart """
        item = self._create_item()
        shopcart = self._create_shopcart(items=[item])
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart['customer_id'], shopcart.customer_id)
        self.assertEqual(len(serial_shopcart['items']), 1)
        items = serial_shopcart['items']
        self.assertEqual(items[0]['shopcart_id'], item.shopcart_id)
        self.assertEqual(items[0]['item_name'], item.item_name)
        self.assertEqual(items[0]['sku'], item.sku)
        self.assertEqual(items[0]['quantity'], item.quantity)
        self.assertEqual(items[0]['price'], item.price)

    def test_deserialize_cart(self):
        """ Deserializes a ShopCart """
        item = self._create_item()
        shopcart = self._create_shopcart(items=[item])
        serial_shopcart = shopcart.serialize()
        new_shopcart = ShopCart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertEqual(new_shopcart.id, shopcart.id)

    def test_delete_shopcart_item(self):
        """ Delete a ShopCart item """
        shopcarts = ShopCart.all()
        self.assertEqual(shopcarts, [])

        item = self._create_item()
        shopcart = self._create_shopcart(items=[item])
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(shopcart.id, 1)
        shopcarts = ShopCart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = ShopCart.find(shopcart.id)
        item = shopcart.items[0]
        item.delete()
        shopcart.save()

        # Fetch it back again
        shopcart = ShopCart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)

######################################################################
#  SERIALIZE/DESERIALIZE TEST CASES
######################################################################
    def test_deserialize_cart_key_error(self):
        """ Deserializes a ShopCart with a KeyError """
        shopcart = ShopCart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_cart_type_error(self):
        """ Deserializes a ShopCart with a TypeError """
        shopcart = ShopCart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

    def test_deserialize_item_key_error(self):
        """ Deserializes a CartItem with a KeyError """
        cart_item = CartItem()
        self.assertRaises(DataValidationError, cart_item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """ Deserializes a CarItem with a TypeError """
        cart_item = CartItem()
        self.assertRaises(DataValidationError, cart_item.deserialize, {})