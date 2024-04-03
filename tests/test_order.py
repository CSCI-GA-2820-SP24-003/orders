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
from service.models.order import OrderStatus
from service.models import Order, Item, DataValidationError, db

from wsgi import app
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    # pylint: disable=duplicate-code
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
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#        O R D E R   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(TestCase):
    """Order Model Test Cases"""

    # pylint: disable=duplicate-code
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
        self.assertEqual(serial_order["status"], order.status.name)
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

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.order_date, order.order_date)
        self.assertEqual(new_order.status.name, serial_order["status"])
        self.assertEqual(new_order.shipping_address, order.shipping_address)
        self.assertEqual(new_order.total_amount, order.total_amount)
        self.assertEqual(new_order.payment_method, order.payment_method)
        self.assertEqual(new_order.shipping_cost, order.shipping_cost)
        self.assertEqual(new_order.expected_date, order.expected_date)
        self.assertEqual(new_order.order_notes, order.order_notes)
        self.assertEqual(len(new_order.items), len(order.items))

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_delete_a_order(self):
        """It should Delete a Order"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)
        # delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            id=fake_order.id,
            customer_id=fake_order.customer_id,
            order_date=fake_order.order_date,
            status=fake_order.status,
            shipping_address=fake_order.shipping_address,
            total_amount=fake_order.total_amount,
            payment_method=fake_order.payment_method,
            shipping_cost=fake_order.shipping_cost,
            expected_date=fake_order.expected_date,
            order_notes=fake_order.order_notes,
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.id, fake_order.id)
        self.assertEqual(order.customer_id, fake_order.customer_id)
        self.assertEqual(order.order_date, fake_order.order_date)
        self.assertEqual(order.status, fake_order.status)
        self.assertEqual(order.shipping_address, fake_order.shipping_address)
        self.assertEqual(order.total_amount, fake_order.total_amount)
        self.assertEqual(order.payment_method, fake_order.payment_method)
        self.assertEqual(order.shipping_cost, fake_order.shipping_cost)
        self.assertEqual(order.expected_date, fake_order.expected_date)
        self.assertEqual(order.order_notes, fake_order.order_notes)

    def test_add_an_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    @patch("service.models.db.session.commit")
    def test_add_order_failed(self, exception_mock):
        """It should not create an Order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.create)

    def test_update_order(self):
        """It should Update an order"""
        order = OrderFactory(customer_id=55)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        self.assertEqual(order.customer_id, 55)

        # Fetch it back
        order = Order.find(order.id)
        order.customer_id = 55
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(order.customer_id, 55)

    @patch("service.models.db.session.commit")
    def test_update_order_failed(self, exception_mock):
        """It should not update an Order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.update)

    def test_find_by_total_amount(self):
        """filter and sort orders by total amount"""

        OrderFactory(total_amount=30.0).create()
        OrderFactory(total_amount=20.0).create()
        OrderFactory(total_amount=50.0).create()
        OrderFactory(total_amount=10.0).create()
        OrderFactory(total_amount=40.0).create()

        orders = Order.find_by_total_amount(
            min_amount=15.0, max_amount=40.0, sort_by="total_amount"
        )
        # Check length
        self.assertEqual(len(orders), 3)
        # Check range
        self.assertGreaterEqual(orders[0].total_amount, 15)
        self.assertLessEqual(orders[0].total_amount, 40)
        # Check Order
        self.assertEqual(orders[0].total_amount, 40)
        self.assertEqual(orders[1].total_amount, 30)
        self.assertEqual(orders[2].total_amount, 20)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Order Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################


class TestModelQueries(TestCaseBase):
    """Order Model Query Tests"""

    def test_query_orders_by_status(self):
        """Test querying orders by status."""
        orders = OrderFactory.create_batch(5, status=OrderStatus.STARTED)
        for order in orders:
            order.create()
        logging.debug(orders)
        # make sure they got saved
        self.assertEqual(len(Order.all()), 5)
        # find orders with status "STARTED"
        started_orders = Order.find_by_status(OrderStatus.STARTED)
        self.assertEqual(len(started_orders), 5)
        for order in started_orders:
            self.assertEqual(order.status, OrderStatus.STARTED)

        # change status of the 2nd order to "PACKING"
        orders[1].status = OrderStatus.PACKING
        orders[1].update()

        # find orders with status "PACKING"
        packing_orders = Order.find_by_status(OrderStatus.PACKING)
        self.assertEqual(len(packing_orders), 1)
        self.assertEqual(packing_orders[0].id, orders[1].id)
