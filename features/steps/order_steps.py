######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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


# pylint: disable=function-redefined, missing-function-docstring, no-name-in-module
# flake8: noqa

"""
Order Steps

Steps file for orders.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html

"""

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following orders")
def step_impl(context):
    """Delete all Orders and load new ones"""

    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.base_url}/api/orders"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for order in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{order['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new orders
    for row in context.table:
        payload = {
            "customer_id": row["customer_id"],
            "order_date": row["order_date"],
            "status": row["status"],
            "shipping_address": row["shipping_address"],
            "payment_method": row["payment_method"],
            "shipping_cost": row["shipping_cost"],
            "expected_date": row["expected_date"],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED


# @given("the following items")
# def step_impl(context):
#     """Load all items to the first order"""
#     # Get the first order
#     rest_endpoint = f"{context.BASE_URL}/api/orders"
#     context.resp = requests.get(rest_endpoint)
#     assert context.resp.status_code == HTTP_200_OK
#     order = context.resp.json()[0]
#     items_route = f"{rest_endpoint}/{order['id']}/items"
#     # Add the new items in the table
#     for row in context.table:
#         payload = {
#             "id": row["id"],
#             "order_id": row["order_id"],
#             "product_id": row["product_id"],
#             "name": row["name"],
#             "quantity": row["quantity"],
#             "unit_price": row["unit_price"],
#             "total_price": row["total_price"],
#         }
#         context.resp = requests.post(items_route, json=payload)
#     assert context.resp.status_code == HTTP_201_CREATED
