"""
Models for ShopCarts and CartItems

All of the models are stored in this module

Models

--------
ShopCart - A cart with items in it

Attributes:

--------


"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass
 

############################################################
# P E R S I S T E N T   B A S E    M O D E L 
############################################################
class PersistentBase():
    """ Base class added persistent methods """

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Account to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes a Account from the data store """
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
    """
    Class that represents a ShopCart
    """
    __tablename__ = 'shopcart'
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    items  = db.relationship('CartItem', backref='shopcart', lazy=True)

    def __repr__(self):
        return "<ShopCart id=[%s]>" % (self.id)

    def save(self):
        """
        Updates a ShopCart to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def serialize(self):
        """ Serializes a ShopCart into a dictionary """
        
        return {
            "id": self.id,
            "items": []
        }
        for item in self.items:
            ShopCart['items'].append(item.serialize())
        return ShopCart

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing ShopCart data
        """
        try:
            self.name = data["name"]
        except KeyError as error:
            raise DataValidationError("Invalid ShopCart: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCart: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def find_by_name(cls, name):
        """ Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCarts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

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
    name = db.Column(db.String(64)) # e.g., black-leather shoes, spatula.

    def __repr__(self):
        return "<Item %r id=[%s] ShopCart account[%s]>" % (self.name, self.id, self.shopcart_id)

    def __str__(self):
        return "%s" % (self.name)

    def serialize(self):
        """ Serializes a Address into a dictionary """
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name
        }

    def deserialize(self, data):
        """
        Deserializes a Address from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.name = data["name"]
        except KeyError as error:
            raise DataValidationError("Invalid Address: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained" "bad or no data"
            )
        return self
