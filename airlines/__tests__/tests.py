#
# Utilities useful for Selenium tests and also if this module is launched as main
# then all available tests for Selenium are launched.
#
#
import django
from django.utils import timezone
import pytz
from django.core.exceptions import ValidationError
from django.db import transaction
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
from django.test import TransactionTestCase
import datetime

TEST_USER_LOGIN = 'adminuser'
TEST_USER_PASSWD = 'passwd123'

def getModels():
    django.setup()
    from airlines import validator
    from airlines import models
    return models

def generateSampleData():
    models = getModels()
    from airlines.datagenerator.planes import PlanesGenerator
    return PlanesGenerator(
        None,
        models.Plane,
        models.Flight,
        models.User,
        models.Worker,
        models.Crew,
        None
    )

def createSuperUser(login=None, passwd=None):
    django.setup()

    global TEST_USER_LOGIN
    global TEST_USER_PASSWD

    if not login:
        login = TEST_USER_LOGIN

    if not passwd:
        passwd = TEST_USER_PASSWD

    from django.contrib.auth.models import User
    try:
        User.objects.create_superuser(login, '', passwd)
    except:
        none = 1

def createTime(year=2018, month=8, day=14, hour=12, minute=15):
    d = datetime.date(year, month, day)
    t = datetime.time(hour, minute)
    return datetime.datetime.combine(d, t, tzinfo=pytz.UTC)

def createTestCrew(models, uniqueName, workersCount):
    capitainWorker = models.Worker(name='John'+uniqueName, surname='Adams'+uniqueName)
    capitainWorker.save()
    crew = models.Crew(capitain=capitainWorker)
    crew.save()
    for i in range(workersCount):
        worker = models.Worker(name='Basic', surname='Worker' + uniqueName + str(i), crew=crew)
        worker.save()
    crew.save()
    return crew

def createTestPlane(models, uniqueName, seatsCount=250):
    plane = models.Plane(reg_id='K313LCBA'+uniqueName, seats_count=seatsCount, service_start=createTime(year=1992))
    plane.save()
    return plane

def evaluateExpectationSimpleSaveToFailOrNot(objectClass, **props):
    try:
        with transaction.atomic():
            obj = objectClass(**props)
            obj.save()
            obj.delete()
    except ValidationError:
        return True

    # The transaction should throw ValidationError
    return False

def expectSimpleSaveToFail(objectClass, **props):
    assert evaluateExpectationSimpleSaveToFailOrNot(objectClass, **props)

def expectSimpleSaveToSucceed(objectClass, **props):
    assert not evaluateExpectationSimpleSaveToFailOrNot(objectClass, **props)



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


def loginTestUser(driver, login=None, passwd=None):
    global TEST_USER_LOGIN
    global TEST_USER_PASSWD

    if not login:
        login = TEST_USER_LOGIN

    if not passwd:
        passwd = TEST_USER_PASSWD

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

    userNameInput.send_keys(login)
    passwordInput.send_keys(passwd)
    loginButton.click()

    #
    # Wait for login redirection
    #
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains('/airlines'))


def startTest(login=None, passwd=None):
    createSuperUser()
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    loginTestUser(driver, login=login, passwd=passwd)
    return driver


def endTest(driver):
    driver.close()


if __name__ == '__main__':
    runTests()
    models = getModels()
    try:
        models.User.objects.all().delete()
        models.Worker.objects.all().delete()
        models.Flight.objects.all().delete()
        models.Crew.objects.all().delete()
        models.Plane.objects.all().delete()
    except:
        none = 1