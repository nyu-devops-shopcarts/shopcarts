"""
Shopcart Steps
Steps file for shopcarts.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))

@given(u'the following items')
def step_impl(context):
    """ Delete all items and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/shopcarts/clear', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/shopcarts/items'
    for row in context.table:
        data = {
            "id": row['id'],
            "shopcart_id": row['shopcart_id'],
            "item_name": row['item_name'],
            "sku": row['sku'],
            "quantity": row['quantity'],
            "price": row['price']
            }

        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when(u'I visit the "Cart page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then(u'I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)