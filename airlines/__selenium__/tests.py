#
# Utilities useful for Selenium tests and also if this module is launched as main
# then all available tests for Selenium are launched.
#
#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from subprocess import Popen
import glob
import os
import inspect

TEST_USER_LOGIN = 'piotr'
TEST_USER_PASSWD = 'admin123'


def runAllTests():
    glob_path = os.path.join(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
        '*.test.py'
    )
    print('Will search the following directiories for Selenium tests:')
    print(glob_path)
    tests = glob.glob(glob_path)
    print('The following Selenium tests will be run:')
    print(tests)
    processes = []
    for test in tests:
        processes.append(Popen('python %s' % test, shell=True))

    for process in processes:
        process.wait()


def loginTestUser(driver):
    global TEST_USER_LOGIN
    global TEST_USER_PASSWD

    driver.get("http://localhost:8000/airlines/flights")

    #
    # Title is correct
    #
    assert "Airlines manager" in driver.title

    #
    # Try to find login button on the page
    #
    loginButton = driver.find_element_by_class_name("loginButton")
    loginButton.click()

    #
    # Redirecting to login page
    #
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains('/login'))

    #
    # Fill login fields with test user credentials
    #
    userNameInput = driver.find_element_by_name('username')
    passwordInput = driver.find_element_by_name('password')
    loginButton = driver.find_element_by_class_name('submitLoginButton')

    userNameInput.send_keys('piotr')
    passwordInput.send_keys('admin123')
    loginButton.click()

    #
    # Wait for login redirection
    #
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains('/airlines'))


def startTest():
    driver = webdriver.Chrome()
    loginTestUser(driver)
    return driver


def endTest(driver):
    driver.close()


if __name__ == '__main__':
    runAllTests()
