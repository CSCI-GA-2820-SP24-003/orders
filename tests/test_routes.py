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
        app.config["DEBUG"] = True
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
    #  O R D E R   T E S T   C A S E S
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

    def test_update_order(self):
        """It should Update an existing Order"""
        # Create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Update the Order
        new_order = resp.get_json()
        new_order["shipping_address"] = "New Road New City"
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["shipping_address"], "New Road New City")

    def test_update_nonexistent_order(self):
        """It should not Update an Order that doesn't exist"""
        # Create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Fail to Update a nonexistent Order
        new_order = resp.get_json()
        new_order["shipping_address"] = "New Road New City"
        new_order_id = new_order["id"] + 1
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_success(self):
        """It should Cancel an Order that isn't shipped yet"""
        # Create an Order to cancel
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Cancel a Started Order
        started_order = resp.get_json()
        order_id = started_order["id"]
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], "CANCELLED")

        # Update to Packing Order
        updated_order["status"] = "PACKING"
        resp = self.client.put(f"{BASE_URL}/{order_id}", json=updated_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        packing_order = resp.get_json()
        self.assertEqual(packing_order["status"], "PACKING")

        # Cancel a Packing Order
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], "CANCELLED")

        # Update to Shipping Order
        updated_order["status"] = "SHIPPING"
        resp = self.client.put(f"{BASE_URL}/{order_id}", json=updated_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        shipping_order = resp.get_json()
        self.assertEqual(shipping_order["status"], "SHIPPING")

        # Cancel a Shipping Order
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        cancelled_order = resp.get_json()
        self.assertEqual(cancelled_order["status"], "CANCELLED")

        # Cancel a Cancelled Order (testing idempotence)
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        recancelled_order = resp.get_json()
        self.assertEqual(recancelled_order["status"], "CANCELLED")

    def test_cancel_order_failure(self):
        """It should not Cancel an Order that is shipped"""
        # Create an Order to cancel
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Update the Order to Delivered
        new_order = resp.get_json()
        new_order["status"] = "DELIVERED"
        order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        delivered_order = resp.get_json()
        self.assertEqual(delivered_order["status"], "DELIVERED")

        # Fail at Cancelling Delivered Order
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.get_data(as_text=True)
        data = data.replace("<p>", "*")
        data = data.replace("</p>", "*")
        tokens = data.split("*")
        data = tokens[1]
        self.assertEqual(data, "Orders that have been delivered cannot be cancelled")

        # Update the Order to Returned
        delivered_order["status"] = "RETURNED"
        resp = self.client.put(f"{BASE_URL}/{order_id}", json=delivered_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        returned_order = resp.get_json()
        self.assertEqual(returned_order["status"], "RETURNED")

        # Fail at Cancelling Returned Order
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        data = resp.get_data(as_text=True)
        data = data.replace("<p>", "*")
        data = data.replace("</p>", "*")
        tokens = data.split("*")
        data = tokens[1]
        self.assertEqual(data, "Orders that have been delivered cannot be cancelled")

    def test_cancel_nonexistent_order(self):
        """It should not Cancel an Order that doesn't exist"""
        # Create an Order to cancel
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Fail to Cancel a nonexistent Order
        started_order = resp.get_json()
        started_order["status"] = "CANCELLED"
        order_id = started_order["id"]+1
        resp = self.client.put(f"{BASE_URL}/{order_id}/cancel", json=started_order)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        """It should Delete a Order"""
        test_order = self._create_orders(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

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

    def test_get_items(self):
        """It should return the item"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        print(item)
        print("SENDING:", item.serialize())
        resp = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        print("GOT BACK:", resp.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        item_id = data["id"]
        response = self.client.get(f"/orders/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["id"], item_id)

    def test_get_items_sad(self):
        """It should not return the item and give error"""
        order = self._create_orders(1)[0]
        response = self.client.get(f"/orders/{order.id}/items/-1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
