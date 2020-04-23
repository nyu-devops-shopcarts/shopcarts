Feature: The shopcart service back-end
    As a customer with a shopcart
    I need a RESTful catalog service
    So that I can keep track of all the itmems in my shopcarts

Background:
    Given the following items
        |  id  | shopcart_id| item_name | sku   | quantity | price |
        |  345 | 1          | Shirt     | 1000  | 1        | 9.99  |
        |  789 | 2          | Shoe      | 150   | 2        | 22.99 |
        |  123 | 3          | Pants     | 450   | 1        | 15.87 |

Scenario: The server is running
    When I visit the "Cart page"
    Then I should see "SHOPCART REST API Service" in the title
    And I should not see "404 Not Found"