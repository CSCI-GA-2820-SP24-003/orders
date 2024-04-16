Feature: The Order service back-end
    As a Order Manager
    I need a RESTful order service
    So that I can keep track of all orders

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer ID" to "123"
    And I set the "Order Date" to "06-16-2022"
    And I set the "Status" to "Started"
    And I set the "Shipping Address" to "fake address"
    And I set the "Total Amount" to "1"
    And I set the "Payment Method" to "CREDIT"
    And I set the "Shipping Cost" to "10"
    And I set the "Expected Date" to "06-20-2022"
    And I set the "Order Notes" to "None"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Order Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "123" in the "Customer ID" field
    And I should see "2022-06-16" in the "Order Date" field
    And I should see "STARTED" in the "Status" field
    And I should see "fake address" in the "Shipping Address" field
    And I should see "1" in the "Total Amount" field
    And I should see "CREDIT" in the "Payment Method" field
    And I should see "10" in the "Shipping Cost" field
    And I should see "2022-06-20" in the "Expected Date" field
    And I should see "None" in the "Order Notes" field


Scenario: Create an Item
    When I visit the "Home Page"
    And I set the "Item Order ID" to "1050"
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
    And I should see "1050" in the "Item Order ID" field
    And I should see "100" in the "Product ID" field
    And I should see "Ruler" in the "Name" field
    And I should see "10" in the "Quantity" field
    And I should see "29.99" in the "Unit Price" field
    And I should see the calculated "Total Price" in the "Total Price" field
    And I should see "None" in the "Description" field
