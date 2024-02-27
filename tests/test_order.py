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
Test cases for Order Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        O R D E R   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(TestCase):
    """Order Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["customer_id"], order.customer_id)
        self.assertEqual(serial_order["order_date"], str(order.order_date))
        self.assertEqual(serial_order["status"], order.status)
        self.assertEqual(serial_order["shipping_address"], order.shipping_address)
        self.assertEqual(serial_order["total_amount"], order.total_amount)
        self.assertEqual(serial_order["payment_method"], order.payment_method)
        self.assertEqual(serial_order["shipping_cost"], order.shipping_cost)
        self.assertEqual(serial_order["expected_date"], str(order.expected_date))
        self.assertEqual(serial_order["order_notes"], order.order_notes)
        self.assertEqual(len(serial_order["items"]), 1)
        items = serial_order["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["order_id"], item.order_id)
        self.assertEqual(items[0]["product_id"], item.product_id)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["unit_price"], item.unit_price)
        self.assertEqual(items[0]["total_price"], item.total_price)
        self.assertEqual(items[0]["description"], item.description)
