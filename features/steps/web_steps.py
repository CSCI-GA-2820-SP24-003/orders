from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{field_name}" to "{value}"')
def step_impl(context, field_name, value):
    field_id = field_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, field_id)

    if "{order_id}" in value:
        order_id = context.scenario_data.get("order_id")
        if order_id is not None:
            value = value.format(order_id=order_id)
        else:
            raise ValueError("order_id not found in scenario_data")

    if field_name == "Status":
        select = Select(element)
        select.select_by_visible_text(value)
    else:
        element.clear()
        element.send_keys(value)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "-") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    print(
        "Current text in 'flash_message':",
        context.driver.find_element(By.ID, "flash_message").text,
    )
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@when('I copy the "{field_name}" field')
def step_impl(context, field_name):
    field_id = field_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, field_id)
    context.clipboard = element.get_attribute("value")


@then('I should see "{value}" in the "{field_name}" field')
def step_impl(context, value, field_name):
    field_id = field_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, field_id)
    actual_value = element.get_attribute("value")
    # print(f"Actual value of {field_name}: {actual_value}")
    assert actual_value == value


@when('I calculate and set the "Total Price" based on quantity and unit price')
def step_impl(context):
    quantity = float(
        context.driver.find_element(By.ID, "quantity").get_attribute("value")
    )
    unit_price = float(
        context.driver.find_element(By.ID, "unit_price").get_attribute("value")
    )
    total_price = quantity * unit_price
    context.driver.find_element(By.ID, "total_price").clear()
    context.driver.find_element(By.ID, "total_price").send_keys(total_price)


@then('I should see the calculated "Total Price" in the "Total Price" field')
def step_impl(context):
    expected_total_price = context.driver.find_element(
        By.ID, "total_price"
    ).get_attribute("value")
    quantity = float(
        context.driver.find_element(By.ID, "quantity").get_attribute("value")
    )
    unit_price = float(
        context.driver.find_element(By.ID, "unit_price").get_attribute("value")
    )
    calculated_total_price = str(quantity * unit_price)
    assert (
        calculated_total_price == expected_total_price
    ), f"Expected total price to be {calculated_total_price}, but got {expected_total_price}"


@then('I save the "{field_name}" field as "{variable_name}"')
def step_impl(context, field_name, variable_name):
    field_id = field_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, field_id)
    context.scenario_data[variable_name] = element.get_attribute("value")


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
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "orders_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='order_name'
# We can then lowercase the name and prefix with order_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
