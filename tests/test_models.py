"""
Test cases for ShopCarts Model

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
        """ Creates a shopcart from a Factory """
        fake_shopcart = ShopCartFactory()
        shopcart = ShopCart(
            id=fake_shopcart.id,
            items = items
        )
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.id, 0) # 0 or None?
        return shopcart
    
    def _create_item(self):
        """ Creates fake item from factory """
        fake_item = CartItemFactory()
        item = CartItem(
            id = fake_item.id,
            shopcart_id = fake_item.shopcart_id,
            name=fake_item.name
        )
        self.assertTrue(item != None)
        self.assertEqual(item.id, 0) #0 or None?
        return item


######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################
    def test_delete_shopcart_item(self):
        """ Delete a shopcart item """
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


    # def test_deserialize_a_pet(self):
    #     """ Test deserialization of a Pet """
    #     data = {"id": 1, "name": "kitty", "category": "cat", "available": True}
    #     pet = Pet()
    #     pet.deserialize(data)
    #     self.assertNotEqual(pet, None)
    #     self.assertEqual(pet.id, None)
    #     self.assertEqual(pet.name, "kitty")
    #     self.assertEqual(pet.category, "cat")
    #     self.assertEqual(pet.available, True)
