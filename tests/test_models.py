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
Test cases for Pet Model
Test cases can be run with:
    nosetests
    coverage report -m
While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_pets.py:TestPetModel
"""
import logging
import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Pet, DataValidationError, db
from service import app
from .factories import PetFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  P E T   M O D E L   T E S T   C A S E S
######################################################################
class TestPetModel(unittest.TestCase):
    """ Test Cases for Pet Model """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Pet.init_db(app)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_pet(self):
        """ Create a pet and assert that it exists """
        pet = Pet(name="fido", category="dog", available=True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "fido")
        self.assertEqual(pet.category, "dog")
        self.assertEqual(pet.available, True)
        pet = Pet(name="fido", category="dog", available=False)
        self.assertEqual(pet.available, False)

    def test_add_a_pet(self):
        """ Create a pet and add it to the database """
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = Pet(name="fido", category="dog", available=True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, None)
        pet.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(pet.id, 1)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)

    def test_update_a_pet(self):
        """ Update a Pet """
        pet = PetFactory()
        logging.debug(pet)
        pet.create()
        logging.debug(pet)
        self.assertEqual(pet.id, 1)
        # Change it an save it
        pet.category = "k9"
        original_id = pet.id
        pet.save()
        self.assertEqual(pet.id, original_id)
        self.assertEqual(pet.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].id, 1)
        self.assertEqual(pets[0].category, "k9")

    def test_delete_a_pet(self):
        """ Delete a Pet """
        pet = PetFactory()
        pet.create()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

    def test_serialize_a_pet(self):
        """ Test serialization of a Pet """
        pet = PetFactory()
        data = pet.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], pet.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], pet.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], pet.category)
        self.assertIn("available", data)
        self.assertEqual(data["available"], pet.available)

    def test_deserialize_a_pet(self):
        """ Test deserialization of a Pet """
        data = {"id": 1, "name": "kitty", "category": "cat", "available": True}
        pet = Pet()
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "kitty")
        self.assertEqual(pet.category, "cat")
        self.assertEqual(pet.available, True)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_find_pet(self):
        """ Find a Pet by ID """
        pets = PetFactory.create_batch(3)
        for pet in pets:
            pet.create()
        logging.debug(pets)
        # make sure they got saved
        self.assertEqual(len(Pet.all()), 3)
        # find the 2nd pet in the list
        pet = Pet.find(pets[1].id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, pets[1].id)
        self.assertEqual(pet.name, pets[1].name)
        self.assertEqual(pet.available, pets[1].available)

    def test_find_by_category(self):
        """ Find Pets by Category """
        Pet(name="fido", category="dog", available=True).create()
        Pet(name="kitty", category="cat", available=False).create()
        pets = Pet.find_by_category("cat")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "kitty")
        self.assertEqual(pets[0].available, False)

    def test_find_by_name(self):
        """ Find a Pet by Name """
        Pet(name="fido", category="dog", available=True).create()
        Pet(name="kitty", category="cat", available=False).create()
        pets = Pet.find_by_name("kitty")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "kitty")
        self.assertEqual(pets[0].available, False)

    def test_find_or_404_found(self):
        """ Find or return 404 found """
        pets = PetFactory.create_batch(3)
        for pet in pets:
            pet.create()

        pet = Pet.find_or_404(pets[1].id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, pets[1].id)
        self.assertEqual(pet.name, pets[1].name)
        self.assertEqual(pet.available, pets[1].available)

    def test_find_or_404_not_found(self):
        """ Find or return 404 NOT found """
        self.assertRaises(NotFound, Pet.find_or_404, 0)
