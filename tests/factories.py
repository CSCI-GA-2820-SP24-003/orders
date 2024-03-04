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
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyDecimal, FuzzyInteger
from service.models import Order, Item
from service.models.order import OrderStatus


class OrderFactory(factory.Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = None
    order_date = FuzzyDate(date(2008, 1, 1))
    status = FuzzyChoice(choices=[OrderStatus.STARTED, OrderStatus.PACKING, OrderStatus.SHIPPING])
    shipping_address = factory.Faker("address")
    total_amount = FuzzyDecimal(0.5, 9999.99)
    payment_method = FuzzyChoice(choices=["CREDIT", "DEBIT", "COD"])
    shipping_cost = FuzzyDecimal(0.5, 99.99)
    expected_date = FuzzyDate(date(2009, 1, 1))
    order_notes = factory.Faker("sentence", nb_words=4)

    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = factory.Sequence(lambda n: n)
    order_id = None
    product_id = None
    name = FuzzyChoice(choices=["ruler", "drill", "hammer"])
    quantity = FuzzyInteger(1, 99)
    unit_price = FuzzyDecimal(0.5, 999.99)
    total_price = FuzzyDecimal(0.5, 9999.99)
    description = factory.Faker("sentence", nb_words=6)
    order = factory.SubFactory(OrderFactory)
