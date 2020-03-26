# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Test Factory to make fake objects for testing
"""
import factory
from datetime import datetime
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyFloat
from service.models import ShopCart, CartItem

class CartItemFactory(factory.Factory):
    """ Creates fake CartItems """

    class Meta:
        model = CartItem

    id = factory.Sequence(lambda n: n)
    shopcart_id = factory.Sequence(lambda n: n)
    item_name = FuzzyChoice(choices=["pants", "shirt", "shoes"])
    sku = FuzzyChoice(choices=["1A3B", "2A94", "4PT3", "4DW2", "00A2","0992", "112A", "APC1"])
    quantity = FuzzyInteger(0, 50, step=1)
    price = FuzzyFloat(0.5, 100.5)


class ShopCartFactory(factory.Factory):
    """ Creates fake ShopCarts """

    class Meta:
        model = ShopCart

    id = factory.Sequence(lambda n: n)
    customer_id = FuzzyInteger(0, 1000, step=1)
    