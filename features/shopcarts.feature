Feature: The shopcart store service back-end
    As a Shopcart Owner
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts

Background:
    Given the following shopcarts
        | ID       | customer_id |
        | 1        | 123         |
        | 2        | 456         |
        | 3        | 789         |

Scenario: Query A ShopCart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "123" in the results
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "shopcart_id" field should be empty
    And the "customer_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see "123" in the "customer_id" field

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "123" in the results
    And I should see "456" in the results
    And I should see "789" in the results

Scenario: Update a Shopcart
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "123" in the results
    And I should see "456" in the results
    And I should see "789" in the results
    When I copy the "shopcart_id" field
    And I set the "customer_id" to "9999"
    And I press the "Update" button
    When I press the "Clear" button
    And I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see "9999" in the "customer_id" field

Scenario: Create a ShopCart
    When I visit the "Home Page"
    And I set the "customer_id" to "909"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    Then the "shopcart_id" field should be empty
    And the "customer_id" field should be empty
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see "909" in the "customer_id" field

Scenario: Delete a ShopCart
    When I visit the "Home Page"
    And I press the "Search" button
    And I copy the "shopcart_id" field
    And I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"


Scenario: Delete all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "123" in the results
    And I should see "456" in the results
    And I should see "789" in the results
    When I press the "Delete-All" button
    Then I should see the message "All Shopcarts have been Deleted!"
    When I press the "Search" button
    Then I should not see "123" in the results
    And I should not see "456" in the results
    And I should not see "789" in the results


