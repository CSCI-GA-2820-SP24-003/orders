######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Persistent Base class for database CRUD functions
"""
import logging
from enum import Enum
from datetime import date
from sqlalchemy import desc
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")


######################################################################
#  O R D E R   M O D E L
######################################################################
class OrderStatus(Enum):
    """
    Enum for Order Statuses
    """

    STARTED = 1
    PACKING = 2
    SHIPPING = 3
    DELIVERED = 4
    CANCELLED = 5
    RETURNED = 6


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    order_date = db.Column(db.Date(), nullable=False, default=date.today())
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.STARTED.name)
    )
    shipping_address = db.Column(db.String(256))
    total_amount = db.Column(db.Double)
    payment_method = db.Column(db.String(64))
    shipping_cost = db.Column(db.Double)
    expected_date = db.Column(db.Date)
    order_notes = db.Column(db.String(1024))
    items = db.relationship("Item", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order {self.customer_id} id=[{self.id}]>"

    def serialize(self):
        """Converts an Order into a dictionary"""

        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.isoformat(),
            "status": self.status.name,
            "shipping_address": self.shipping_address,
            "total_amount": self.total_amount,
            "payment_method": self.payment_method,
            "shipping_cost": self.shipping_cost,
            "expected_date": self.expected_date.isoformat(),
            "order_notes": self.order_notes,
            "items": [],
        }
        for item in self.items:
            order["items"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Populates an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.order_date = date.fromisoformat(data["order_date"])
            self.status = getattr(OrderStatus, data["status"])
            self.shipping_address = data["shipping_address"]
            self.total_amount = data["total_amount"]
            self.payment_method = data["payment_method"]
            self.shipping_cost = data["shipping_cost"]
            self.expected_date = date.fromisoformat(data["expected_date"])
            self.order_notes = data["order_notes"]

            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @staticmethod
    def find_by_date_range(start_date, end_date=None):
        """
        Finds orders within a specific date range.

        Args:
            start_date: The start date of the range to query for.
            end_date: The end date of the range to query for. If None, queries all orders from the start date to current.

        Returns:
            List[Order]: A list of orders within the specified date range.
        """
        logger.info("Querying for orders from %s to %s", start_date, end_date or "now")

        query = Order.query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        return query.order_by(Order.order_date.desc()).all()

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_customer_id(cls, customer_ids):
        """Returns all Orders with the given customer id

        Args:
            customer_id (Integer): the customer_id of the Orders you want to match
        """
        logger.info("Processing name query for %s ...", customer_ids)
        return cls.query.filter(cls.customer_id.in_(customer_ids)).order_by(desc(Order.order_date))

    @classmethod
    def find_by_total_amount(
        cls, min_amount=0.0, max_amount=0.0, sort_by="total_amount"
    ):
        """Returns all Items with the given product_id

        Args:
            product_id (integer): the product_id of the Items you want to match
        """
        logger.info(
            "Processing min = %s and max = %s amount (sorted by %s) query for orders ...",
            min_amount,
            max_amount,
            sort_by,
        )
        if sort_by.lower() == "total_amount":
            sort_criterion = cls.total_amount.desc()
        return (
            cls.query.filter(
                cls.total_amount >= min_amount, cls.total_amount <= max_amount
            )
            .order_by(sort_criterion)
            .all()
        )

    @classmethod
    def find_by_status(cls, status: OrderStatus) -> list:
        """Returns all Orders with a specific status

        :param status: the status of the Orders you want to match
        :type status: OrderStatus
        :return: a collection of Orders with that status
        :rtype: list
        """
        logger.info("Processing status query for %s ...", status.name)
        return cls.query.filter(cls.status == status).all()
