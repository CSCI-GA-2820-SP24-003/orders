"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrderService(TestCase):
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
    
    def _create_items_in_existing_order(self, order_id, count):
        """Factory method to create items in an existing order in bulk"""
        test_items = []
        for _ in range(count):
            test_item = ItemFactory()
            response = self.client.post(
                f"/orders/{order_id}/items",
                json=test_item.serialize(),
                content_type="application/json",
            )
            item = response.get_json()
            test_items.append(item)
        return test_items

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_order(self):
        """It should Delete a Order"""
        test_order = self._create_orders(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "customer_id does not match"
        )
        self.assertEqual(
            new_order["order_date"], str(order.order_date), "order_date does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "status does not match"
        )
        self.assertEqual(
            str(new_order["total_amount"]),
            str(order.total_amount),
            "total_amount does not match",
        )
        self.assertEqual(
            new_order["payment_method"],
            order.payment_method,
            "payment_method does not match",
        )
        self.assertEqual(
            str(new_order["shipping_cost"]),
            str(order.shipping_cost),
            "shipping_cost does not match",
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
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "customer_id does not match"
        )
        self.assertEqual(
            new_order["order_date"], str(order.order_date), "order_date does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "status does not match"
        )
        self.assertEqual(
            str(new_order["total_amount"]),
            str(order.total_amount),
            "total_amount does not match",
        )
        self.assertEqual(
            new_order["payment_method"],
            order.payment_method,
            "payment_method does not match",
        )
        self.assertEqual(
            str(new_order["shipping_cost"]),
            str(order.shipping_cost),
            "shipping_cost does not match",
        )
        self.assertEqual(
            new_order["expected_date"],
            str(order.expected_date),
            "expected_date does not match",
        )
        self.assertEqual(
            new_order["order_notes"], order.order_notes, "order_notes does not match"
        )

    def test_get_item_from_order(self):
        """
        It should return the item       
        """
        order = self._create_orders(1)[0]
        print(order)
        item = self._create_items_in_existing_order(order.id, 3)[0]

        response = self.client.get(
            f"/orders/{order.id}/items/{item['id']}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        print(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["id"], item["id"])
        print('here 1')
        sad_path_order_id = -1
        response = self.client.get(
            f"/orders/{sad_path_order_id}/items/123",
            content_type="application/json",
        )
        # If the order does not exist
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
        print('here 2')
        sad_path_item_id = -1
        print(order.id)
        response = self.client.get(
            f"/orders/{order.id}/items/{sad_path_item_id}",
            content_type="application/json",
        )

        # If the item does not exist
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )
        print('here 3')

    # Todo: Add your test cases here...
