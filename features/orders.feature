Feature: The order service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keey track of all my orders

    Background:
        Given the following orders:
            | ID          | Customer_id    |Order_Date    | Status     | Shipping_Address   | Total_Amount | Payment_Method  | Shipping_Cost  | Expected_Date   |
            | 8782        | 33             |2022-10-10    | SHIPPING   | old Road old City  | 80382        | credit card     | 20.2           | 2022-11-12      |
            | 8780        | null           |2014-01-05    | STARTED    | New Road New City	| 6907.53      | DEBIT           | 54.42          | 2024-02-05      |
        Given the following items:
            | ID          | Order ID       |Product ID    | Name       | Quantity           | Unit Price   | Total Price     |
            | 4098        | 8782           |25            | Phone      | 2                  | 1000         | 2000            |
            | 4099        | 8782           |30            | laptop     | 1	                | 6000         | 6000            |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Orders RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: List all Orders
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "SHIPPING" in the resultscc
        And I should see "STARTED" in the results
        And I should not see "PACKING" in the results