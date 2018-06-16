from tests import *


#
# Helper function to setup one driver
#
def setupDriverForChangingCrew(flightIndex):
    driver = startTest()

    #
    # Find page with flights
    #
    driver.get("http://localhost:8000/airlines/crews-panel")

    #
    # Wait for javascript to load data by AJAX request
    #
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".crews-table > tbody > tr > td"))
    )

    #
    # Find table with flights
    #
    flightsTable = driver.find_element_by_class_name("crews-table")
    flightsRows = flightsTable.find_elements_by_css_selector("tbody > tr")
    assert len(flightsRows) > flightIndex

    #
    # Click to expand row
    #
    flightsRows[flightIndex].click()

    #
    # Wait for javascript to update expanded row
    #
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".content-expanded"))
    )
    time.sleep(5)

    #
    # Find expanded row with details
    #
    expandedRow = driver.find_element_by_class_name("content-expanded")

    #
    # Find and click edit button
    #
    crewChangeButton = expandedRow.find_elements_by_css_selector(".button-crew")
    assert len(crewChangeButton) == 1

    crewChangeButton[0].click()

    #
    # Wait for edit box to appear
    #
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".edit-box"))
    )

    #
    # Find input for changing crews
    #
    crewEditBox = driver.find_element_by_class_name("edit-box")
    crewInputBox = crewEditBox.find_element_by_name("crew")

    #
    # Type something into the crew input box
    #
    crewInputBox.send_keys("a")

    #
    # Wait for rendering of input box suggestions
    #
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".input-suggestions > li"))
    )

    #
    # Retrieve list of suggestions
    #
    suggestionsNodes = driver.find_elements_by_css_selector(".input-suggestions > li")
    suggestions = [node.find_elements_by_css_selector("code")[0].text for node in suggestionsNodes]

    return {
        'suggestions': suggestions,
        'suggestionsNodes': suggestionsNodes,
        'driver': driver
    }


class TestSeleniumCrews(unittest.TestCase):

    #
    # Selenium test testing the following action flow:
    #
    #   -> login
    #   -> change tab to crews assign tab
    #   -> expand first flight row
    #   -> press edit button
    #   -> land on flight edition page
    #
    #
    def test_edit_button(self):
        driver = startTest()

        #
        # Find page with flights
        #
        driver.get("http://localhost:8000/airlines/crews-panel")

        #
        # Wait for javascript to load data by AJAX request
        #
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".crews-table > tbody > tr > td"))
        )

        #
        # Find table with flights
        #
        flightsTable = driver.find_element_by_class_name("crews-table")
        flightsRows = flightsTable.find_elements_by_css_selector("tbody > tr")
        assert len(flightsRows) > 0

        #
        # Click to expand row
        #
        flightsRows[0].click()

        #
        # Wait for javascript to update expanded row
        #
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".content-expanded"))
        )
        time.sleep(1)

        #
        # Find expanded row with details
        #
        expandedRow = driver.find_element_by_class_name("content-expanded")

        #
        # Find and click edit button
        #
        editButton = expandedRow.find_elements_by_css_selector(".button-edit")
        assert len(editButton) == 1

        editButton[0].click()

        #
        # You should be redirected to flight edition page
        #
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains('/flight-edit'))

        endTest(driver)

    #
    # Selenium test testing the following action flow:
    #
    #   -> login
    #   -> change tab to crews assign tab
    #   -> expand first flight row
    #   -> press change crew button
    #   -> Type 'a'
    #   -> Select crew (one in one window and other in the second)
    #   -> Pres the crew row to change it
    #
    #
    def test_concurrently_assign_crews(self):
        #
        # Start two drivers to perform concurrent changes
        #
        driverSetup1 = setupDriverForChangingCrew(0)
        driverSetup2 = setupDriverForChangingCrew(0)

        #
        # Two list of suggestions should be identical
        #
        assert set(driverSetup1['suggestions']) == set(driverSetup2['suggestions'])

        #
        # Click to change the crew in both drivers
        #
        driverSetup1['suggestionsNodes'][0].click()
        driverSetup2['suggestionsNodes'][1].click()

        endTest(driverSetup1['driver'])
        endTest(driverSetup2['driver'])