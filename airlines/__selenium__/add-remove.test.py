#
# Selenium test testing the following action flow:
#
#   -> login
#   -> select first flight on list
#   -> see passenger list
#   -> add test user
#   -> see passenger list
#   -> seeremove test user
#   -> see passenger list
#
#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests import startTest, endTest

FLIGHT_TEST_PERSON_NAME = 'ZZZZZZZZZZZZZZZZ_TESTUSERNAME'

driver = startTest()

#
# Find page with flights
#
driver.get("http://localhost:8000/airlines/flights")

#
# Find flights table rows on the page
#
flightsTable = driver.find_element_by_class_name("flights-table")
flightsRows = flightsTable.find_elements_by_css_selector("tbody > tr")

#
# Flights table has at least one flight row
#
assert len(flightsRows) > 0

#
# Click the first flight row
#
flightsRows[0].click()

wait = WebDriverWait(driver, 10)
wait.until(EC.url_contains('/flight-edit'))

#
# Find table with booked tickets
#
ticketsTable = driver.find_element_by_class_name("tickets-table")
ticketsRows = ticketsTable.find_elements_by_css_selector("tbody > tr")
ticketsRowCount = len(ticketsRows)

#
# If there is at least one booked ticket
# then we remove the first person to make a place for the test user
#
if ticketsRowCount > 0:
    cancelButton = ticketsRows[0].find_elements_by_css_selector('button.small')[0]
    cancelButton.click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains('/flight-edit'))
    ticketsTable = driver.find_element_by_class_name("tickets-table")
    ticketsRows = ticketsTable.find_elements_by_css_selector("tbody > tr")

    assert len(ticketsRows) == ticketsRowCount - 1
    ticketsRowCount = len(ticketsRows)

#
# Find the "Add new user" button then click it and wait for flight edition page
#
addNewPassangerButton = driver.find_element_by_class_name("addNewPassangerButton")
addNewPassangerButton.click()

wait = WebDriverWait(driver, 10)
wait.until(EC.url_contains('/flight-add-user-flight'))

#
# Enter new passenger name and surname
#
userNameInput = driver.find_element_by_name('user_name')
userSurnameInput = driver.find_element_by_name('user_surname')

userNameInput.send_keys(FLIGHT_TEST_PERSON_NAME)
userSurnameInput.send_keys(FLIGHT_TEST_PERSON_NAME)

#
# Save passenger details
#
userSubmitButton = driver.find_element_by_class_name('submitAddUser')
userSubmitButton.click()

wait = WebDriverWait(driver, 10)
wait.until(EC.url_contains('/flight-edit'))

#
# Now look at the modified flight page
#
ticketsTableAfterChange = driver.find_element_by_class_name("tickets-table")
ticketsRowsAfterChange = ticketsTableAfterChange.find_elements_by_css_selector("tbody > tr")
ticketsRowCountAfterChange = len(ticketsRowsAfterChange)

#
# The count of passengers should have increased exactly by 1
#
assert ticketsRowCountAfterChange == ticketsRowCount + 1

#
# Search for the newly added user
# The list is sorted in decreasing order of surnames so he shall be at the first page
#
elementFound = False
for ticketRow in ticketsRowsAfterChange:
    if FLIGHT_TEST_PERSON_NAME in ticketRow.get_attribute('innerHTML'):
        elementFound = True

        #
        # Cancel the flight of the test user
        #
        cancelButton = ticketRow.find_elements_by_css_selector('button.small')[0]
        cancelButton.click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains('/flight-edit'))
        ticketsTableAfterRemoval = driver.find_element_by_class_name("tickets-table")
        ticketsRowsAfterRemoval = ticketsTableAfterRemoval.find_elements_by_css_selector("tbody > tr")
        ticketsRowCountAfterRemoval = len(ticketsRowsAfterRemoval)

        #
        # Now the cound of passengers should be as it was the first time
        #
        assert ticketsRowCountAfterRemoval == ticketsRowCount

#
# The test user should be found
#
assert elementFound == True

endTest(driver)
