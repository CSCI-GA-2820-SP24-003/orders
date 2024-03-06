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
            float(new_order["total_amount"]),
            float(order.total_amount),
            "total_amount does not match",
        )
        self.assertEqual(
            new_order["payment_method"],
            order.payment_method,
            "payment_method does not match",
        )
        self.assertEqual(
            float(new_order["shipping_cost"]),
            float(order.shipping_cost),
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
            float(new_order["total_amount"]),
            float(order.total_amount),
            "total_amount does not match",
        )
        self.assertEqual(
            new_order["payment_method"],
            order.payment_method,
            "payment_method does not match",
        )
        self.assertEqual(
            float(new_order["shipping_cost"]),
            float(order.shipping_cost),
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

        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["id"], item["id"])

        sad_path_order_id = -1
        response = self.client.get(
            f"/orders/{sad_path_order_id}/items/123",
            content_type="application/json",
        )
        # If the order does not exist
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
        sad_path_item_id = -1
        response = self.client.get(
            f"/orders/{order.id}/items/{sad_path_item_id}",
            content_type="application/json",
        )

        # If the item does not exist
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_update_order(self):
        """It should Update an existing Order"""
        # create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_order = resp.get_json()
        new_order["shipping_address"] = "New Road New City"
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["shipping_address"], "New Road New City")

    def test_add_item(self):
        """It should add an item to a valid order id"""
        # if given valid order id, item should be created and added to the order
        test_order = self._create_orders(1)[0]
        test_item = ItemFactory()
        response = self.client.post(
            f"{BASE_URL}/{test_order.id}/items",
            json=test_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["order_id"], test_order.id)
        self.assertEqual(data["product_id"], test_item.product_id)
        self.assertEqual(data["quantity"], test_item.quantity)
        self.assertEqual(data["unit_price"], float(test_item.unit_price))

        # order id is not found
        sad_path_order_id = -1
        sad_path_test_item = ItemFactory()
        response = self.client.post(
            f"{BASE_URL}/{sad_path_order_id}/items",
            json=sad_path_test_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_list(self):
        """It should return the list of items in an order"""
        # add two items to order
        order = self._create_orders(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{order.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_delete_item(self):
        """It should Delete an Item"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item(self):
        """It should Update an item on an order"""
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["name"], "XXXX")

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Todo: Add your test cases here...
