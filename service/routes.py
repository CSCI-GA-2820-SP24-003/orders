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
Orders Service

This service implements a REST API that allows you to manage Orders for a financial service.
"""
import math

from datetime import datetime

from flask import jsonify

from flask import request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse

# pylint: disable=cyclic-import
from service.models import Order, Item
from service.models.order import OrderStatus
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
item_create_model = api.model(
    "Item",
    {
        "order_id": fields.Integer(
            required=True, description="The Order an Item is associated with"
        ),
        "product_id": fields.Integer(
            required=True, description="The product an Item is associated with"
        ),
        "name": fields.String(required=True, description="The name of the Item"),
        "quantity": fields.Integer(
            required=True, description="The quantity of the Item purchased"
        ),
        "unit_price": fields.Float(
            required=True, description="The unit price for the Item"
        ),
        "total_price": fields.Float(
            required=True, description="The total price of the Item purchased"
        ),
        "description": fields.String(
            required=True, description="The description for the Item"
        ),
    },
)

item_model = api.inherit(
    "ItemModel",
    item_create_model,
    {"id": fields.Integer(readOnly=True, description="The ID for the Item")},
)

order_create_model = api.model(
    "Order",
    {
        "customer_id": fields.Integer(
            required=True, description="The ID of the customer purchasing the Order"
        ),
        "order_date": fields.Date(
            required=True,
            description="The date the Order was made",
        ),
        # pylint: disable=protected-access
        "status": fields.String(
            enum=OrderStatus, description="The status of the Order"
        ),
        "shipping_address": fields.String(
            required=True, description="The place where the Order is delivered to"
        ),
        "total_amount": fields.Float(
            required=True, description="The total cost of items in the Order"
        ),
        "payment_method": fields.String(
            required=True, description="The payment method for the Order"
        ),
        "shipping_cost": fields.Float(
            required=True, description="The shipping cost of the Order"
        ),
        "expected_date": fields.Date(
            required=True, description="The date the Order is expected to arrive"
        ),
        "order_notes": fields.String(
            required=False, description="The notes for the Order delivery"
        ),
        "items": fields.List(
            fields.Nested(item_create_model),
            required=False,
            description="The items within the Order",
        ),
    },
)

order_model = api.inherit(
    "OrderModel",
    order_create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
item_args = reqparse.RequestParser()
item_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="List Items with a specific product id",
)
item_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="List Items with a specific name",
)

order_args = reqparse.RequestParser()
order_args.add_argument(
    "order-start",
    type=str,
    location="args",
    required=False,
    help="List Orders ordered after a date",
)
order_args.add_argument(
    "order-end",
    type=str,
    location="args",
    required=False,
    help="List Orders ordered before a date",
)
order_args.add_argument(
    "total-min",
    type=str,
    default=0.0,
    location="args",
    required=False,
    help="List Orders with a total cost above a price point",
)
order_args.add_argument(
    "total-max",
    type=str,
    default=math.inf,
    location="args",
    required=False,
    help="List Orders with a total cost below a price point",
)
order_args.add_argument(
    "customer-id",
    type=str,
    location="args",
    required=False,
    help="List Orders from a specific customer",
)
order_args.add_argument(
    "status",
    type=str,
    location="args",
    required=False,
    help="List Orders with a specific Order status",
)
order_args.add_argument(
    "sort_by",
    type=str,
    location="args",
    required=False,
    help="List Orders sorted by a particular metric",
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /orders/{order_id} - Returns an Order with the id
    PUT /orders/{order_id} - Update an Order with the id
    DELETE /orders/{order_id} -  Deletes an Order with the id
    """

    ######################################################################
    # READ AN ORDER
    ######################################################################
    @api.doc("get_orders")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order

        This endpoint will return a Order based on its id
        """
        app.logger.info("Request for order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        app.logger.info("Returning order: %s", order.id)
        return order.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING ORDER
    ######################################################################
    @api.doc("update_orders")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order

        This endpoint will update an Order based the body that is posted
        """
        app.logger.info("Request to update order with id: %s", order_id)
        check_content_type("application/json")
        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Update from the json in the body of the request

        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        order.deserialize(data)
        order.id = order_id
        order.update()
        return order.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE AN ORDER
    ######################################################################
    @api.doc("delete_orders")
    @api.response(204, "Order deleted")
    def delete(self, order_id):
        """
        Delete a Order

        This endpoint will delete a Order based the id specified in the path
        """
        app.logger.info("Request to delete order with id: %d", order_id)

        order = Order.find(order_id)
        if order:
            order.delete()
            app.logger.info("Order with ID: %d delete complete.", order_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """Handles all interactions with collections of Orders"""

    ######################################################################
    # LIST ALL ORDERS
    ######################################################################
    # flake8: noqa: C901
    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """Returns all Orders within a date range and total amount range if specified, sorted by order date or total amount."""
        app.logger.info("Request for Order list")

        # try:
        query = Order.query
        args = order_args.parse_args()

        if args["status"]:
            query = query.filter(Order.status == args["status"])

        if args["order-start"]:
            start_date = datetime.strptime(args["order-start"], "%Y-%m-%d").date()
            query = query.filter(Order.order_date >= start_date)

        if args["order-end"]:
            end_date = datetime.strptime(args["order-end"], "%Y-%m-%d").date()
            query = query.filter(Order.order_date <= end_date)

        if args["total-min"] is not None and args["total-max"] is not None:
            try:
                total_min = float(args["total-min"])
                total_max = float(args["total-max"])
                query = query.filter(Order.total_amount.between(total_min, total_max))
            except ValueError:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    "Please enter valid minimum and maximum values. They should be decimal values.",
                )
        if args["customer-id"] is not None:
            try:
                customer_id = [int(args["customer-id"])]
            except (TypeError, ValueError):
                try:
                    customer_id = args["customer-id"].split(",")
                    customer_id = [int(c_id) for c_id in customer_id]
                except (TypeError, ValueError):
                    abort(
                        status.HTTP_400_BAD_REQUEST,
                        f"{args['customer-id']} is not a valid customer_id. Please enter an integer.",
                    )

            query = query.filter(Order.customer_id.in_(customer_id))
            query_results = query.all()

            if not query_results:
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"{args['customer-id']} is not a valid customer_id. Please enter an integer.",
                )

        if args["sort_by"] == "total_amount":
            query = query.order_by(Order.total_amount.desc())
        else:  # sort on "order_date" by default:
            query = query.order_by(Order.order_date.desc())

        orders = query.all()
        return [order.serialize() for order in orders], status.HTTP_200_OK

    ######################################################################
    # CREATE A NEW ORDER
    ######################################################################
    @api.doc("create_orders")
    @api.response(400, "The posted data was not valid")
    @api.expect(order_create_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates an Order
        This endpoint will create an Order based the data in the body that is posted
        """
        app.logger.info("Request to create an Order")
        check_content_type("application/json")

        # Create the order
        order = Order()
        app.logger.debug("Payload = %s", api.payload)
        order.deserialize(api.payload)
        order.create()

        # Create a message to return
        app.logger.info("order with new id [%s] created!", order.id)
        message = order.serialize()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)

        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
@api.route("/orders/<int:order_id>/cancel")
@api.param("order_id", "The Order identifier")
class CancelOrderResource(Resource):
    """Cancel action on an Order"""

    @api.doc("cancel_orders")
    @api.response(404, "Order not found")
    @api.response(409, "Order cannot be cancelled")
    def put(self, order_id):
        """
        Cancel an Order

        This endpoint will cancel an Order
        """
        app.logger.info("Request to cancel order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Abort Cancellation if order has been delivered
        if order.status in (OrderStatus.DELIVERED, OrderStatus.RETURNED):
            abort(
                status.HTTP_409_CONFLICT,
                "Orders that have been delivered cannot be cancelled",
            )

        # Update from the json in the body of the request
        order.status = OrderStatus.CANCELLED
        order.update()

        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}/deliver
######################################################################
@api.route("/orders/<int:order_id>/deliver")
@api.param("order_id", "The Order identifier")
class DeliverOrderResource(Resource):
    """Deliver action on an Order"""

    @api.doc("deliver_orders")
    @api.response(404, "Order not found")
    @api.response(409, "Order cannot be delivered")
    def put(self, order_id):
        """deliver the Order that has been shipped"""
        app.logger.info("Request to deliver order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Orders with id {order_id} not found. Please enter a valid order id.",
            )

        # abort if invalid order status
        if order.status not in (OrderStatus.SHIPPING, OrderStatus.DELIVERED):
            abort(
                status.HTTP_409_CONFLICT,
                f"Orders in {order.status} cannot be delivered.",
            )

        order.status = OrderStatus.DELIVERED
        order.update()

        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}/packing
######################################################################
@api.route("/orders/<int:order_id>/packing")
@api.param("order_id", "The Order identifier")
class PackOrderResource(Resource):
    """Pack action on an Order"""

    @api.doc("pack_orders")
    @api.response(404, "Order not found")
    @api.response(409, "Order cannot be packed")
    def put(self, order_id):
        """Pack the Order that has not being shipped yet"""
        app.logger.info("Request to pack order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Orders with id {order_id} not found. Please enter a valid order id.",
            )

        # abort if invalid order status
        if order.status not in (OrderStatus.STARTED, OrderStatus.PACKING):
            abort(
                status.HTTP_409_CONFLICT,
                f"Orders that have been {order.status} cannot be set to PACKING ",
            )

        order.status = OrderStatus.PACKING
        order.update()

        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}/ship
######################################################################
@api.route("/orders/<int:order_id>/ship")
@api.param("order_id", "The Order identifier")
class ShipOrderResource(Resource):
    """Ship action on an Order"""

    @api.doc("ship_orders")
    @api.response(404, "Order not found")
    @api.response(409, "Order cannot be shipped")
    def put(self, order_id):
        """Ship all the items of the Order that have not being shipped yet"""
        app.logger.info("Request to ship order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        # abort if invalid order status
        if order.status not in [OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
            order.status = OrderStatus.SHIPPING
            order.update()
        else:
            abort(
                status.HTTP_409_CONFLICT,
                f"Order with id '{order_id}' has been DELIVERED/CANCELLED",
            )

        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Order
    GET /orders/{order_id}/items/{item_id} - Returns an Item with the id
    PUT /orders/{order_id}/items/{item_id} - Update an Item with the id
    DELETE /orders/{order_id}/items/{item_id} -  Deletes an Item with the id
    """

    ######################################################################
    # GET A SINGLE ITEM IN AN ORDER
    ######################################################################
    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """
        Get an Item

        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN ITEM
    ######################################################################
    @api.doc("update_items")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """
        Update an Item

        This endpoint will update an Item based the body that is posted
        """
        app.logger.info(
            "Request to update Item %s for Order id: %s", (item_id, order_id)
        )
        check_content_type("application/json")

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{item_id}' could not be found.",
            )

        # Update from the json in the body of the request
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        item.deserialize(data)
        item.id = item_id
        item.order_id = order_id
        item.update()

        return item.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE AN AN ITEM FROM AN ORDER
    ######################################################################
    @api.doc("delete_items")
    @api.response(204, "Item deleted")
    def delete(self, order_id, item_id):
        """
        Delete an Item

        This endpoint will delete an Item based the id specified in the path
        """
        app.logger.info(
            "Request to delete Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and delete it if it does
        item = Item.find(item_id)
        if item:
            item.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id}/items
######################################################################
@api.route("/orders/<int:order_id>/items", strict_slashes=False)
@api.param("order_id", "The Order identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Items"""

    ######################################################################
    # LIST ITEMS
    ######################################################################
    @api.doc("list_items")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """Returns all of the Items for an Order"""
        app.logger.info("Request for all Items for Order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        items = order.items
        args = item_args.parse_args()

        if args["product_id"]:
            product_id = int(args["product_id"])
            items = Item.find_by_product_id(order_id, product_id)
            if not items:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    "Please enter valid product id.",
                )
        elif args["name"]:
            items = Item.find_by_name(order_id, args["name"])

        results = [item.serialize() for item in items]
        return results, status.HTTP_200_OK

    ######################################################################
    # ADD AN ITEM TO AN ORDER
    ######################################################################
    @api.doc("create_items")
    @api.response(400, "The posted data was not valid")
    @api.expect(item_create_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Creates an item and adds item to an order

        Args:
            order_id ( integer )
        """
        app.logger.info("Adding an item to the order with order_id %s", order_id)
        check_content_type("application/json")

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not be found",
            )

        # Create an item from the json data
        item = Item()
        app.logger.debug("Payload = %s", api.payload)
        item.deserialize(api.payload)
        item.order_id = order_id
        item.create()

        location_url = api.url_for(
            ItemResource, order_id=order.id, item_id=item.id, _external=True
        )
        app.logger.info("Item with id %s created for order with %s", item.id, order.id)
        return (
            item.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Check to ensure system is up"""
    return jsonify(status=200, message="Response 200 OK"), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
