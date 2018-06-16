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
