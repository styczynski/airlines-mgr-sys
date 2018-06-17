from tests import *

class TestSeleniumDataSorting(unittest.TestCase):

    #
    # Selenium test testing the following action flow:
    #
    #   -> login
    #   -> go to flights view
    #   -> press plane registration column to sort it
    #   -> check if data is sorted
    #   -> press again
    #   -> check if data is sorted
    #
    #
    def test_sort_table_by_planes_reg(self):
        generateSampleData()

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

        columnPlaneRegSortHeader = driver.find_element_by_class_name("sort-by-plane-plate")
        columnPlaneRegSortHeader.click()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains('orderby=plane__reg_id&mode=desc'))

        flightsTable = driver.find_element_by_class_name("flights-table")
        flightsRows = flightsTable.find_elements_by_css_selector("tbody > tr")

        planeRegs = [
            row.find_elements_by_css_selector("td > code")[0].get_attribute('innerHTML') for row in flightsRows
        ]

        #
        # List of flights is sorted ASC
        #
        l = planeRegs
        assert (all(l[i] <= l[i+1] for i in range(len(l)-1)))


        columnPlaneRegSortHeader = driver.find_element_by_class_name("sort-by-plane-plate")
        columnPlaneRegSortHeader.click()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains('orderby=plane__reg_id&mode=asc'))

        flightsTable = driver.find_element_by_class_name("flights-table")
        flightsRows = flightsTable.find_elements_by_css_selector("tbody > tr")

        planeRegs = [
            row.find_elements_by_css_selector("td > code")[0].get_attribute('innerHTML') for row in flightsRows
        ]

        #
        # List of flights is sorted DESC
        #
        l = planeRegs
        assert (all(l[i] >= l[i+1] for i in range(len(l)-1)))
