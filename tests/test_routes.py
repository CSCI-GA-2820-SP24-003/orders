"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders


    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_orders(self):
        """It should list all orders"""
        sample_orders = [OrderFactory() for _ in range(5)]
        for order in sample_orders:
            order.create()

        # Make a GET request to the /orders endpoint
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Load the response data
        data = response.get_json()

        # Check that we got a list of orders
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(sample_orders))

        # Check that the data in the response matches what we put in the database
        for order_data in data:
            # Assuming your OrderFactory sets a unique customer_id for each order
            order = next(
                (
                    o
                    for o in sample_orders
                    if o.customer_id == order_data["customer_id"]
                ),
                None,
            )
            self.assertIsNotNone(order)
            self.assertEqual(order_data["customer_id"], order.customer_id)
            # Add more assertions here to check other fields if necessary

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["id"], order.id, "id does not match")
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "customer_id does not match"
        )
        self.assertEqual(new_order["order_date"], order.order_date, "order_date does not match")
        self.assertEqual(
            new_order["status"], order.status.name, "status does not match"
        )
        self.assertEqual(
            new_order["total_amount"], order.total_amount, "total_amount does not match"
        )
        self.assertEqual(
            new_order["payment_method"], order.payment_method, "payment_method does not match"
        )
        self.assertEqual(
            new_order["shipping_cost"], order.shipping_cost, "shipping_cost does not match"
        )
        self.assertEqual(
            new_order["expected_date"],
            str(order.expected_date),
            "expected_date does not match",
        )
        self.assertEqual(
            new_order["order_notes"], order.order_notes, "order_notes does not match"
        )
        

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["id"], order.id, "id does not match")
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "customer_id does not match"
        )
        self.assertEqual(new_order["order_date"], str(order.order_date), "order_date does not match")
        self.assertEqual(
            new_order["status"], order.status, "status does not match"
        )
        self.assertEqual(
            new_order["total_amount"], order.total_amount, "total_amount does not match"
        )
        self.assertEqual(
            new_order["payment_method"], order.payment_method, "payment_method does not match"
        )
        self.assertEqual(
            new_order["shipping_cost"], order.shipping_cost, "shipping_cost does not match"
        )
        self.assertEqual(
            new_order["expected_date"],
            str(order.expected_date),
            "expected_date does not match",
        )
        self.assertEqual(
            new_order["order_notes"], order.order_notes, "order_notes does not match"
        )
    
    # Todo: Add your test cases here...
