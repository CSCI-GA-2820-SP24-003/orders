Feature: The Order service back-end
    As a Order Manager
    I need a RESTful order service
    So that I can keep track of all orders

Background:
    Given the following orders
        | customer_id | order_date | status   | shipping_address | total_amount | payment_method | shipping_cost | expected_date | order_notes |
        | 123         | 2022-06-16 | STARTED  | fake address      | 1            | CREDIT         | 10            | 2022-06-20    | Some notes |
        | 456         | 2022-07-01 | SHIPPING | real address      | 100.50       | DEBIT          | 5.99          | 2022-07-05    | Special notes |
    Given the following items:
        |product_id    | name       | quantity           | unit_price   | total_price     |description      |
        |25            | Phone      | 2                  | 1000         | 2000            |it's a phone     |
        |30            | Laptop     | 1	                 | 6000         | 6000            |it's a laptop    |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer ID" to "1234"
    And I set the "Order Date" to "06-15-2022"
    And I set the "Status" to "Started"
    And I set the "Shipping Address" to "fakefake address"
    And I set the "Total Amount" to "2"
    And I set the "Payment Method" to "CREDIT"
    And I set the "Shipping Cost" to "20"
    And I set the "Expected Date" to "06-22-2022"
    And I set the "Order Notes" to "None"
    And I press the "Create" button
    Then I should see the message "Success"
    And I save the "Order Id" field as "order_id"
    When I copy the "Order Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1234" in the "Customer ID" field
    And I should see "2022-06-15" in the "Order Date" field
    And I should see "STARTED" in the "Status" field
    And I should see "fakefake address" in the "Shipping Address" field
    And I should see "2" in the "Total Amount" field
    And I should see "CREDIT" in the "Payment Method" field
    And I should see "20" in the "Shipping Cost" field
    And I should see "2022-06-22" in the "Expected Date" field
    And I should see "None" in the "Order Notes" field


Scenario: Create an Item
    When I visit the "Home Page"
    And I set the "Item Order ID" to "{order_id}"
    And I set the "Product ID" to "100"
    And I set the "Name" to "Ruler"
    And I set the "Quantity" to "10"
    And I set the "Unit Price" to "29.99"
    And I calculate and set the "Total Price" based on quantity and unit price
    And I set the "Description" to "None"
    And I press the "Create Item" button
    Then I should see the message "Success"
    When I copy the "Item ID" field
    And I press the "Retrieve Item" button
    Then I should see the message "Success"
    And I should see "100" in the "Product ID" field
    And I should see "Ruler" in the "Name" field
    And I should see "10" in the "Quantity" field
    And I should see "29.99" in the "Unit Price" field
    And I should see the calculated "Total Price" in the "Total Price" field
    And I should see "None" in the "Description" field

    Scenario: List all Orders
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "SHIPPING" in the "Order" results
        And I should see "STARTED" in the "Order" results
        And I should not see "PACKING" in the "Order" results

    Scenario: List Items
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear Item" button
        Then the "Item ID" field should be empty
        When I copy the "Order ID" field
        And I press the "Clear" button
        And I paste the "Item Order ID" field
        And I press the "Search Item" button
        Then I should see the message "Success"
        And I should see "Phone" in the "Item" results
        And I should see "Laptop" in the "Item" results
