#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MVC Bot
"""

from distutils.debug import DEBUG
import sys
import config # private data set
import telegram
import requests
import logging
import dateparser

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

def find_by_mvc(URL: str) -> list:

    results = []
    counter = 0

    logger.info("Creating remote session...")

    while True:
        try:
            drv = webdriver.Remote(command_executor=get_worker_url())
        except Exception:
            logger.error(f"An error has occurred during the session creation:\n {Exception}")
            logger.warning("Application is running in idle mode")
            sleep(30)
            continue
        break

    logger.info("session created")

    for mvc_code in config.mvc_to_process:

        if config.apt_type == 15:
            mvc_code = mvc_code - 81

        drv.get(f"{URL}/{config.apt_type}/{mvc_code}")

        mvc_name = drv.find_elements(
            By.CLASS_NAME, "nav-item")[3].text.split(" - ")[0]

        mvc_name = f"({mvc_code}) {mvc_name}"

        try:
            drv.find_element(By.CLASS_NAME, "availableTimeslot")
        except Exception:
            logger.info(f"({mvc_code}) {mvc_name} has no appointments")
            # uncomment in case you want to include in a result mvc with no appointments available 
            # results.append(f"{mvc_name} has no appointments")
            continue
        else:
            counter += 1
            time_slot = drv.find_elements(
                By.CLASS_NAME, "control-label")[1].text.replace("Time of Appointment for", "")

            message = f"{counter}. {time_slot}<a href=\"{URL}/{config.apt_type}/{mvc_code}\">{mvc_name}</a>"
            logger.info(message)

            if config.apt_threshold >= dateparser.parse(time_slot):
                make_appointment(config.apt_type, mvc_code, drv)

            results.append(message)

    drv.quit()
    return results


def write_state(text):
    f = open("state", "w")
    f.write(text)
    f.close()


def read_state():
    try:
        f = open("state", "r")
    except Exception as e:
        return f"File doesnt exist"
    return f.read()


def send_tg(text, chat_id=config.tg_group, token=config.tg_token):
    bot = telegram.Bot(token=token)
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Cant send. Error: \n {e}")


def send_pic_tg(image, chat_id=config.tg_group, token=config.tg_token):
    bot = telegram.Bot(token=token)
    try:
        bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'))
    except Exception as e:
        logger.error(f"Cant send. Error: \n {e}")


def make_appointment(
    apt_type,
    mvc_code,
    driver,
    firstName=config.apt_firstName,
    lastName=config.apt_lastName,
    email=config.apt_email,
    phone=config.apt_phone,
    driver_license=config.apt_driverlicense,
    birth_date=config.apt_birth_date,
    url=config.url
    ):

    driver.get(f"{url}{mvc_code}")

    driver.find_elements(By.CLASS_NAME, "availableTimeslot")[0].click()
    driver.find_element(By.ID, "firstName").send_keys(firstName)
    driver.find_element(By.ID, "lastName").send_keys(lastName)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "phone").send_keys(phone)

    if apt_type == 19:
        driver.find_element(By.ID, "driverLicense").send_keys(driver_license)
        driver.find_element(By.ID, "test").send_keys("Auto")
    elif apt_type == 15:
        driver.find_element(By.ID, "permitType").send_keys("Purchase an auto examination permit (Class D) (ages 17+)")
        driver.find_element(By.ID, "birthDate").send_keys(birth_date)

    driver.find_element(By.NAME, "Attest").click()
    driver.find_element(By.CLASS_NAME, "g-recaptcha").click()

    sleep(10)
    driver.save_screenshot("book_result.png")
    send_pic_tg("book_result.png")


def get_worker_url(worker_candidates=config.worker_candidates):
    result = ""
    while not result:
        logger.warning("Looking for selenium worker")
        for worker in worker_candidates:
            try:
                get = requests.get(f"http://{worker}:4444")
                if get.status_code == 200:
                    logger.warning(f"Worker found: http://{worker}:4444")
                    result = (f"http://{worker}:4444")
                    return result
            except Exception:
                logger.warning(f"{worker} not a worker")
                continue
        logger.warning("No available selenium workers has been found")
        logger.warning("Application is running in idle mode")

        sleep(5)

    return 1

##### MAIN FUNC ########


logger = logging.getLogger()
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '[%(asctime)s]:[%(module)s]:[%(lineno)s]:[%(levelname)s] %(message)s', '%d-%b-%y %H:%M:%S')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)

logger.info("App starting")

while True:

    appointments_available = find_by_mvc(config.url)

    # Convert list into html
    html_msg = "\n".join([str(appointment) for appointment in appointments_available])

    if not html_msg:
        html_msg = "no appointments available atm"
    
    if html_msg == read_state():
        logger.warning("no changes since last check")
    else:
        send_tg(html_msg)

    write_state(html_msg)

    sleep(config.request_interval)
