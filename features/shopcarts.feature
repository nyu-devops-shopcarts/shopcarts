Feature: The shopcart service back-end
    As a shopcart manager
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts

Background:
    Given the following shopcarts
        | ID       | customer_id | items |
        | 2        | 456         | True  |
        | 3        | 345         | True  |
        | 6        | 909         | False |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart REST API Service" in the title
    And I should not see "404 Not Found"