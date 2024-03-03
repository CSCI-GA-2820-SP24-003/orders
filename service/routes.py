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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application

from service.models import Order
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0",
            # Todo: Uncomment the next line when GET /orders is implemented
            # paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


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

    app.logger.info("Returning order: %s", order.name)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Creates a Order

    This endpoint will create a Order based the data in the body that is posted
    """
    app.logger.info("Request to create a order")
    check_content_type("application/json")

    order = Order()
    order.deserialize(request.get_json())
    order.create()
    message = order.serialize()
    location_url = url_for("get_orders", order_id=order.id, _external=True)

    app.logger.info("Order with ID: %d created.", order.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


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
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for Order list")
    orders = []

    orders = Order.all()

    # Return as an array of dictionaries
    results = [order.serialize() for order in orders]

    return jsonify(results), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
