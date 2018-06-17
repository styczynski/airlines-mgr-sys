from tests import *

class TestSeleniumAuthorize(unittest.TestCase):

    #
    # Selenium test testing the following action flow:
    #
    #   -> login
    #
    #
    def test_user_login(self):
        driver = startTest()
        endTest(driver)

    def test_non_existing_user(self):
        driver = startTest(login='nonexisting', passwd='useristhat')

        #
        # Wait for message to appear
        #
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".errorlist"))
        )

        #
        # Extract "bad login" message and comapare it with the expected one
        #
        errorMessage = driver.find_elements_by_css_selector(".errorlist > li")
        assert len(errorMessage) == 1

        errorMessageText = errorMessage[0].get_attribute('innerHTML')
        assert errorMessageText == "Please enter a correct username and password. Note that both fields may be case-sensitive."