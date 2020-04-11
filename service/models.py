"""
Models for ShopCarts and CartItems

All of the models are stored in this module

Models

--------
ShopCart - A cart with items in it

Attributes:
id
customer_id
items

--------
CartItem

Attributes:
id
shopcart_id
item_name
sku
quantity
price

"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass
 
import json
DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

from cloudant.client import Cloudant
from cloudant.query import Query
from cloudant.adapters import Replay429Adapter
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 10))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 1))
RETRY_BACKOFF = int(os.environ.get('RETRY_BACKOFF', 2))

############################################################
# P E R S I S T E N T   B A S E    M O D E L 
############################################################
class PersistentBase():
    """ Base class added persistent methods """

    def create(self):
        """
        Creates a ShopCart to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a ShopCart to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes a ShopCart from the data store """
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the records in the database """
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a record by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a record by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)


#############################################################
# S H O P C A R T    M O D E L 
#############################################################

class ShopCart(db.Model, PersistentBase):
    __tablename__ = 'shopcart'
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id =  db.Column(db.Integer)
    items  = db.relationship('CartItem', backref='shopcart', lazy=True)
   
    def __repr__(self):
        return "<ShopCart id=[%s]>" % (self.id)

    def serialize(self):
        """ Serializes a ShopCart into a dictionary """       
        item_list = {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": []
        }
        for item in self.items:
            item_list['items'].append(item.serialize())
        return item_list

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing ShopCart data
        """
        try:
            self.customer_id = data["customer_id"]
            item_list = data.get("items")
            for json_item in item_list:
                item = CartItem()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid ShopCart: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCart: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def find_by_item_name(cls, name):
        """ Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCarts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.item_name == name)

#############################################################
# I T E M    M O D E L 
#############################################################
class CartItem(db.Model, PersistentBase):
    
    """
    Class that represents an CartItem
    """
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(db.Integer, db.ForeignKey('shopcart.id'), nullable=False)
    item_name = db.Column(db.String(64)) 
    sku = db.Column(db.String(16))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __repr__(self):
        return "<Item %r id=[%s] ShopCart [%s]>" % (self.item_name, self.id, self.shopcart_id)

    def __str__(self):
        return "%s: %s,%s,%s " % (self.item_name, self.sku, self.quantity, self.price)

    def serialize(self):
        """ Serializes a Item into a dictionary """
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "item_name": self.item_name,
            "sku":self.sku,
            "quantity":self.quantity,
            "price":self.price
        }

    def deserialize(self, data):
        """
        Deserializes a CartItem from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.item_name = data["item_name"]
            self.sku = data["sku"]
            self.quantity = data["quantity"]
            self.price = data["price"]

        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained" "bad or no data"
            )
        return self

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='pets'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        # Try and get VCAP from the environment
        if 'VCAP_SERVICES' in os.environ:
            Pet.logger.info('Found Cloud Foundry VCAP_SERVICES bindings')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith('cloudantNoSQLDB'):
                    opts = vcap_services[service][0]['credentials']

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts and 'BINDING_CLOUDANT' in os.environ:
            Pet.logger.info('Found Kubernetes BINDING_CLOUDANT bindings')
            opts = json.loads(os.environ['BINDING_CLOUDANT'])

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            Pet.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            opts = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            raise DatabaseConnectionError('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')

        Pet.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Pet.logger.info('Running in Admin Party Mode...')
            Pet.client = Cloudant(opts['username'],
                                  opts['password'],
                                  url=opts['url'],
                                  connect=True,
                                  auto_renew=True,
                                  admin_party=ADMIN_PARTY,
                                  adapter=Replay429Adapter(retries=10, initialBackoff=0.01)
                                 )

        except ConnectionError:
            raise DatabaseConnectionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Pet.database = Pet.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Pet.database = Pet.client.create_database(dbname)
        # check for success
        if not Pet.database.exists():
            raise DatabaseConnectionError('Database [{}] could not be obtained'.format(dbname))
© 2020 GitHub, Inc.