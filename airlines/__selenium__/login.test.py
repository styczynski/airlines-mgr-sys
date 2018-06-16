#
# Selenium test testing the following action flow:
#
#   -> login
#
#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests import startTest, endTest

driver = startTest()
endTest(driver)
