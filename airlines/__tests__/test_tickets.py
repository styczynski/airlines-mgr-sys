from tests import *

class TestSeleniumUserTickets(unittest.TestCase):

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
    def test_add_remove_user_tickets(self):
        
        generateSampleData()


        FLIGHT_TEST_PERSON_NAME = 'ZZZZZZZZZZZZZZZZZ_TESTUSERNAME'

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
        ticketsRowsFirstTextOriginal = None
        ticketsRowsFirstTextInitial = None
        ticketsRowCount = len(ticketsRows)

        #
        # If there is at least one booked ticket
        # then we remove the first person to make a place for the test user
        #
        if ticketsRowCount > 0:
            ticketRow = ticketsRows[0]
            ticketsRowsFirstTextInitial = ticketsRows[0].text
            ticketsRowsFirstTextOriginal = ticketsRows[0].text

            cancelButton = ticketRow.find_elements_by_css_selector('.button')[0]
            cancelButton.click()

            time.sleep(3)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.url_contains('/flight-edit'))

            ticketsRowsBefore = ticketsRows
            ticketsTable = driver.find_element_by_class_name("tickets-table")
            ticketsRows = ticketsTable.find_elements_by_css_selector("tbody > tr")

            assert len(ticketsRows) > 0
            assert ticketsRows[0].text != ticketsRowsFirstTextOriginal

            ticketsRowCount = len(ticketsRows)
            ticketsRowsFirstTextOriginal = ticketsRows[0].text

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
        time.sleep(10)

        #
        # Now look at the modified flight page
        #
        ticketsTableAfterChange = driver.find_element_by_class_name("tickets-table")
        ticketsRowsAfterChange = ticketsTableAfterChange.find_elements_by_css_selector("tbody > tr")
        ticketsRowCountAfterChange = len(ticketsRowsAfterChange)
        ticketRowsTexts = [  ticketRow.get_attribute('innerHTML') for ticketRow in ticketsRowsAfterChange ]

        #
        # The count of passengers should have increased exactly by 1
        #
        assert ticketsRowsFirstTextInitial != ticketsRowsAfterChange[0].text

        #
        # Search for the newly added user
        # The list is sorted in decreasing order of surnames so he shall be at the first page
        #
        elementFound = False
        i = -1
        for ticketRow in ticketsRowsAfterChange:
            i = i + 1
            if FLIGHT_TEST_PERSON_NAME in ticketRowsTexts[i]:
                elementFound = True

                #
                # Cancel the flight of the test user
                #
                cancelButton = ticketRow.find_elements_by_css_selector('.button')[0]
                cancelButton.click()
                wait = WebDriverWait(driver, 10)
                wait.until(EC.url_contains('/flight-edit'))
                ticketsTableAfterRemoval = driver.find_element_by_class_name("tickets-table")
                ticketsRowsAfterRemoval = ticketsTableAfterRemoval.find_elements_by_css_selector("tbody > tr")
                ticketsRowCountAfterRemoval = len(ticketsRowsAfterRemoval)

                #
                # Now the cound of passengers should be as it was the first time
                #
                if ticketsRowsFirstTextOriginal == None:
                    assert ticketsRowCountAfterRemoval == 0
                else:
                    assert ticketsRowsAfterRemoval[0].text == ticketsRowsFirstTextOriginal

        #
        # The test user should be found
        #
        assert elementFound == True



        endTest(driver)
