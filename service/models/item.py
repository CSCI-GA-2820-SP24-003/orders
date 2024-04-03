"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Double)
    total_price = db.Column(db.Double)
    description = db.Column(db.String(1024))

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] order[{self.order_id}]>"

    def __str__(self):
        return f"{self.name}: {self.quantity}, {self.unit_price}, {self.total_price} {self.description}"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "description": self.description,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.order_id = data["order_id"]
            self.product_id = data["product_id"]
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.unit_price = data["unit_price"]
            self.total_price = data["total_price"]
            self.description = data["description"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @classmethod
    def find_by_product_id(cls, product_id):
        """Returns all Items with the given product_id

        Args:
            product_id (integer): the product_id of the Items you want to match
        """
        logger.info("Processing product_id query for %s ...", product_id)
        # return Item.query.filter(Item.product_id == product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_name(cls, order_id, name):
        """Returns all Items with the given name

        Args:
            order_id (integer): the id of the Order
            name (string): the name of the Items you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(
            cls.order_id == order_id, cls.name.ilike(f"%{name}%")
        ).all()
