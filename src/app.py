import config # private data set
import telegram
import requests
import dateparser

import os.path
from os import path

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

def find_by_mvc(URL: str) -> list:

    results = []
    counter = 0

    print(f"create remote session...")

    drv = webdriver.Remote(
        command_executor=get_worker_url())

    print(f"session created")

    for mvc_code in config.mvc_to_process:

        drv.get(f"{URL}{mvc_code}")

        mvc_name = drv.find_elements(
            By.CLASS_NAME,"nav-item")[3].text.split(" - ")[0]

        mvc_name = f"({mvc_code}) {mvc_name}"

        try:
            drv.find_element(By.CLASS_NAME,"availableTimeslot")
        except Exception:
            print(f"({mvc_code}) {mvc_name} has no appointments")
            #uncomment in case you want to include in a result mvc with no appointments available 
            #results.append(f"{mvc_name} has no appointments")
            continue
        else:
            counter += 1
            time_slot = drv.find_elements(
                By.CLASS_NAME,"control-label")[1].text.replace("Time of Appointment for", "")

            message = f"{counter}. {time_slot}<a href=\"https://telegov.njportal.com/njmvc/AppointmentWizard/19/{mvc_code}\">{mvc_name}</a>"
            print(message)

            if config.apt_threshold >= dateparser.parse(time_slot):
               make_appointment(mvc_code, drv)

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
        bot.send_message(chat_id=chat_id, text=text,parse_mode="HTML")
    except Exception as e:
        print(f"Cant send. Error: \n {e}")

def send_pic_tg(image, chat_id=config.tg_group, token=config.tg_token):
    bot = telegram.Bot(token=token)
    try:
        bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'))
    except Exception as e:
        print(f"Cant send. Error: \n {e}")

def make_appointment(
    mvc_code,
    driver,
    firstName=config.apt_firstName,
    lastName=config.apt_lastName,
    email=config.apt_email,
    phone=config.apt_phone,
    driver_license=config.apt_driverlicense,
    make_appointment_url=config.make_appointment_url
    ):

    driver.get(f"{make_appointment_url}{mvc_code}")
    
    driver.find_elements(By.CLASS_NAME, "availableTimeslot")[0].click()
    driver.find_element(By.ID, "firstName").send_keys(firstName)
    driver.find_element(By.ID, "lastName").send_keys(lastName)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "phone").send_keys(phone)
    driver.find_element(By.ID, "driverLicense").send_keys(driver_license)
    driver.find_element(By.ID, "test").send_keys("Auto")
    driver.find_element(By.NAME, "Attest").click()
    driver.find_element(By.CLASS_NAME, "g-recaptcha").click()
    sleep(10)
    driver.save_screenshot("book_result.png")
    send_pic_tg("book_result.png")

def get_worker_url(worker_candidates=config.worker_candidates):

    for worker in worker_candidates:
        try:
            get = requests.get(f"http://{worker}:4444")
            if get.status_code == 200:
                return(f"http://{worker}:4444")
        except Exception:
                print(f"{worker} not a worker")
                continue
        return "no workers found"

##### MAIN FUNC ########

print(f"App starting")

while True:
    appointments_available = find_by_mvc(config.url)

    # Convert list into html
    html_msg = "\n".join([str(appointment) for appointment in appointments_available])
    
    if not html_msg:
        html_msg = "no appointments available atm"
    
    if html_msg == read_state():
        print("no changes since last check")
    else:
        send_tg(html_msg)

    write_state(html_msg)

    sleep(config.request_interval)
