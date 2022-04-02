import datetime
import argparse

import selenium.common.exceptions
from dateutil import parser
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Set up commandline arguments
help_text = "This selenium bot allows you to register for classes on the Case Western SIS portal right at 7:00 AM."

args_parser = argparse.ArgumentParser(description=help_text)
args_parser.add_argument('--time', '-t', help="set time to register at, formatted as hh:mm in military (24 hour) time")
args = args_parser.parse_args()

# Time to register at
registration_time = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=7))

if args.time:
    registration_time = parser.parse(args.time)

# If the time passed has already passed for the current day, then we want to
# register at that time but on the next day
if registration_time <= datetime.datetime.now():
    registration_time += datetime.timedelta(days=1)

usernameStr = input("Please enter your Case ID (abc123): ")
passwordStr = getpass("Please enter your password: ")

# Start the Selenium WebDriver
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)
browser.get('https://sis.case.edu/psc/P92SCWR_3/EMPLOYEE/SA/c/SSR_STUDENT_FL.SSR_MD_SP_FL.GBL'
            '?Action=U&MD=Y&GMenu=SSR_STUDENT_FL&GComp=SSR_START_PAGE_FL&GPage=SSR_START_PAGE_FL'
            '&scname=CS_SSR_MANAGE_CLASSES_NAV&AJAXTransfer=y&ICAJAXTrf=true&ICMDListSlideout=true')

# Wait for and get username field
WebDriverWait(browser, 10).until(lambda d: d.find_element(By.ID, 'userid'))
username = browser.find_element(By.ID, 'userid')
username.send_keys(usernameStr)
password = browser.find_element(By.ID, 'pwd')
password.send_keys(passwordStr)

signInButton = browser.find_element(By.CLASS_NAME, 'btn-primary')
signInButton.click()

try:
    WebDriverWait(browser, 5).until(lambda d: d.find_element(By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$3'))
except selenium.common.exceptions.TimeoutException:
    print("Authentication details incorrect or server took too long to respond. Please try again later.")
    exit(-1)

WebDriverWait(browser, 5).until(lambda d: d.find_element(By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$3'))
shoppingCartButton = browser.find_element(By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$3')
shoppingCartButton.click()

WebDriverWait(browser, 10).until(lambda d: d.find_element(By.ID, 'DERIVED_SSR_FL_SSR_ENROLL_FL'))
enrollButton = browser.find_element(By.ID, 'DERIVED_SSR_FL_SSR_ENROLL_FL')

input("Please check all the classes that you want to register for. Then press ENTER.")

# Wait until it's time
while True:
    curr_time = datetime.datetime.now()
    time = "Waiting... " + curr_time.strftime('%H:%M:%S')
    print(time, end="\r")

    try:
        alert = browser.switch_to.alert
        alert.accept()
    except:
        pass

    if curr_time >= registration_time:
        print("Executing class registration.")
        enrollButton.click()
        print("Successfully registered.")
        WebDriverWait(browser, 10000)
        break

input("Click ENTER to exit.")
