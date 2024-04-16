from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert(message in context.driver.title)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert(text_string not in element.text)

@when('I set the "{field_name}" to "{value}"')
def step_impl(context, field_name, value):
    field_id = field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, field_id)
    
    if field_name == "Status":
        select = Select(element)
        select.select_by_visible_text(value)
    else:
        element.clear()
        element.send_keys(value)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(' ', '-') + '-btn'
    context.driver.find_element(By.ID, button_id).click()
    context.driver.save_screenshot('home_page.png')

@then('I should see the message "{message}"')
def step_impl(context, message):
    print("Current text in 'flash_message':", context.driver.find_element(By.ID, 'flash_message').text)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert(found)


@when('I copy the "{field_name}" field')
def step_impl(context, field_name):
    field_id = field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, field_id)
    context.clipboard = element.get_attribute('value')

@then('I should see "{value}" in the "{field_name}" field')
def step_impl(context, value, field_name):
    field_id = field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, field_id)
    actual_value = element.get_attribute('value')
    print(f"Actual value of {field_name}: {actual_value}")
    assert actual_value == value

@when('I calculate and set the "Total Price" based on quantity and unit price')
def step_impl(context):
    quantity = float(context.driver.find_element(By.ID, 'quantity').get_attribute('value'))
    unit_price = float(context.driver.find_element(By.ID, 'unit_price').get_attribute('value'))
    total_price = quantity * unit_price
    context.driver.find_element(By.ID, 'total_price').clear()
    context.driver.find_element(By.ID, 'total_price').send_keys(total_price)

@then('I should see the calculated "Total Price" in the "Total Price" field')
def step_impl(context):
    expected_total_price = context.driver.find_element(By.ID, 'total_price').get_attribute('value')
    quantity = float(context.driver.find_element(By.ID, 'quantity').get_attribute('value'))
    unit_price = float(context.driver.find_element(By.ID, 'unit_price').get_attribute('value'))
    calculated_total_price = str(quantity * unit_price)
    assert calculated_total_price == expected_total_price, f"Expected total price to be {calculated_total_price}, but got {expected_total_price}"