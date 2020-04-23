Feature: The shopcart store service back-end
    As a Shopcart Owner
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts

Background:
    Given the following shopcarts
        | ID       | customer_id | item_id |
        | 2        | 456         | 123  |
        | 2        | 456         | 789  |
        | 2        | 456         | 808 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart REST API Service" in the title
    And I should not see "404 Not Found"