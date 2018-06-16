#
# Utilities useful for Selenium tests and also if this module is launched as main
# then all available tests for Selenium are launched.
#
#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import unittest
import sys
from subprocess import Popen
import glob
import os
import inspect
import shutil
import time

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


def runTests():
    print('[i] Will now launch tests')
    processes = []
    processes.append(Popen('python -m xmlrunner discover -s airlines/__tests__ -p "test_*.py"', shell=True))
    for process in processes:
        process.wait()

    # Copy the xmp files
    glob_path = os.path.join(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
        '..',
        '..',
        '*.xml'
    )
    dest_path = os.path.join(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
        '..',
        '..',
        'test-results'
    )

    shutil.rmtree(os.path.abspath(dest_path))
    time.sleep(0.1)

    destDirCreated = True
    try:
        os.mkdir(os.path.abspath(dest_path))
    except:
        # Nothing meaningful
        destDirCreated = False

    print(glob_path)

    htmlReportSource = ""

    for file in glob.glob(glob_path):
        obj_src = os.path.abspath(file)
        obj_dest = os.path.abspath(os.path.join(
            dest_path,
            'tests.xml'
        ))
        obj_dest_html = os.path.abspath(os.path.join(
            dest_path,
            'tests.html'
        ))

        print(obj_src + ' -> '+obj_dest)

        shutil.copy(obj_src, obj_dest)
        os.unlink(obj_src)

        processes = []
        processes.append(Popen('python -m junit2htmlreport  "'+obj_dest+'"  "'+obj_dest_html+'"', shell=True))
        for process in processes:
            process.wait()

        contents = ""
        with open(obj_dest_html) as f:
            contents = f.read()
            contents = contents.split('<body>')[1].split('</body>')[0]

        htmlReportSource = htmlReportSource + contents


    obj_dest_html = os.path.abspath(os.path.join(
        dest_path,
        'tests.html'
    ))
    outf = open(obj_dest_html, 'w')
    outf.write(htmlReportSource)
    outf.close()


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
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    loginTestUser(driver)
    return driver


def endTest(driver):
    driver.close()


if __name__ == '__main__':
    runTests()
