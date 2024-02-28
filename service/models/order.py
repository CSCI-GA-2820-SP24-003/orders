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

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    order_date = db.Column(db.Date(), nullable=False, default=date.today())
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, default=OrderStatus.STARTED
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
        status_value = (
            self.status if isinstance(self.status, str) else self.status.value
        )

        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.isoformat(),
            "status": status_value,
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
            self.status = OrderStatus(data["status"])
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
