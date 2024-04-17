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

from flask import request, url_for, abort
from flask import current_app as app  # Import Flask application

from service.models import Order, Item
from service.models.order import OrderStatus
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# READ A ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order

    This endpoint will return a Order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)

    order = Order.find(order_id)
    if not order:
        error(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    app.logger.info("Returning order: %s", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
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
# LIST ALL ORDERS
######################################################################
# flake8: noqa: C901
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all Orders within a date range and total amount range if specified, sorted by order date or total amount."""
    app.logger.info("Request for Order list")

    app.logger.info(f"request.url : {request.url}")

    start_date_str = request.args.get("order-start")
    end_date_str = request.args.get("order-end")
    total_min = request.args.get("total-min", default=0.0)
    total_max = request.args.get("total-max", default=math.inf)
    customer_id = request.args.get("customer-id")
    order_status = request.args.get("status")
    app.logger.info(status)
    sort_by = request.args.get("sort_by", default="order_date")

    # try:
    query = Order.query

    if order_status:
        query = query.filter(Order.status == order_status)

    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        query = query.filter(Order.order_date >= start_date)

    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        query = query.filter(Order.order_date <= end_date)

    if total_min is not None and total_max is not None:
        try:
            total_min = float(total_min)
            total_max = float(total_max)
            query = query.filter(Order.total_amount.between(total_min, total_max))
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Please enter valid minimum and maximum values. They should be decimal values.",
            )
    if customer_id is not None:
        try:
            customer_id = [int(customer_id)]
        except (TypeError, ValueError):
            # print(f"inside second try----------------- {customer_id}")
            try:
                customer_id = customer_id.split(",")
                customer_id = [int(c_id) for c_id in customer_id]
            except (TypeError, ValueError):
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"{customer_id} is not a valid customer_id. Please enter an integer.",
                )

        query = query.filter(Order.customer_id.in_(customer_id))
        # print(query)
        query_results = query.all()
        # print(f"----------------- {query_results}----------------- ")

        if not query_results:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"{customer_id} is not a valid customer_id. Please enter an integer.",
            )

    if sort_by == "order_date":
        query = query.order_by(Order.order_date.desc())
    elif sort_by == "total_amount":
        query = query.order_by(Order.total_amount.desc())

    orders = query.all()
    app.logger.info(orders)
    return jsonify([order.serialize() for order in orders]), status.HTTP_200_OK


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # Create the order
    order = Order()
    app.logger.info(request.get_json())
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()
    location_url = url_for("get_orders", order_id=order.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")
    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update from the json in the body of the request

    # app.logger.info(f"request{request.get_json()}")

    order.deserialize(request.get_json())
    order.id = order_id
    order.update()
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# CANCEL AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """
    Cancel an Order

    This endpoint will cancel an Order
    """
    app.logger.info("Request to cancel order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Abort Cancellation if order has been delivered
    if order.status in (OrderStatus.DELIVERED, OrderStatus.RETURNED):
        abort(
            status.HTTP_409_CONFLICT,
            "Orders that have been delivered cannot be cancelled",
        )

    # Update from the json in the body of the request
    order.status = OrderStatus.CANCELLED
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# PACK AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/packing", methods=["PUT"])
def pack_orders(order_id):
    """Pack the Order that has not being shipped yet"""
    app.logger.info("Request to pack order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Orders with id {order_id} not found. Please enter a valid order id.",
        )

    # abort if invalid order status
    # print(order.status)
    if order.status not in (OrderStatus.STARTED, OrderStatus.PACKING):
        abort(
            status.HTTP_409_CONFLICT,
            f"Orders that have been {order.status} cannot be set to PACKING ",
        )

    order.status = OrderStatus.PACKING
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELIVER AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/deliver", methods=["PUT"])
def deliver_orders(order_id):
    """deliver the Order that has been shipped"""
    app.logger.info("Request to deliver order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Orders with id {order_id} not found. Please enter a valid order id.",
        )

    # abort if invalid order status
    # print(order.status)
    if order.status not in (OrderStatus.SHIPPING, OrderStatus.DELIVERED):
        abort(
            status.HTTP_409_CONFLICT,
            f"Orders in {order.status} cannot be delivered.",
        )

    order.status = OrderStatus.DELIVERED
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# GET A SINGLE ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_items(order_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info("Request to retrieve Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based the id specified in the path
    """
    app.logger.info("Request to delete Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# ADD AN ITEM TO AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_item(order_id):
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
    item.deserialize(request.get_json())
    item.order_id = order_id

    order.items.append(item)
    order.update()
    item.update()

    location_url = url_for(
        "add_item", order_id=order.id, item_id=item.id, _external=True
    )
    app.logger.info("Item with id %s created for order with %s", item.id, order.id)
    return (
        jsonify(item.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ITEMS BY NAME
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """Returns all of the Items for an Order"""
    app.logger.info("Request for all Items for Order with id: %s", order_id)

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    items = order.items

    product_id = request.args.get("product_id")
    item_name = request.args.get("name")

    if product_id:
        product_id = int(product_id)
        items = Item.find_by_product_id(product_id)
        if not items:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Please enter valid product id.",
            )
    elif item_name:
        items = Item.find_by_name(order_id, item_name)

    results = [item.serialize() for item in items]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_items(order_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based the body that is posted
    """
    app.logger.info("Request to update Item %s for Order id: %s", (item_id, order_id))
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# SHIP AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/ship", methods=["PUT"])
def ship_orders(order_id):
    """Ship all the items of the Order that have not being shipped yet"""
    app.logger.info("Request to ship order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # print(order.status)
    if order.status not in [OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
        order.status = OrderStatus.SHIPPING
        order.update()
    else:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Order with id '{order_id}' has been DELIVERED/CANCELLED",
        )

    return jsonify(order.serialize()), status.HTTP_200_OK


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
