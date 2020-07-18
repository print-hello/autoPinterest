import os
import re
import time
import requests
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def explicit_wait(driver, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(driver, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            print(
                "Timed out with failure while explicitly waiting until {}!\n"
                .format(ec_name))
        return False

    return result


def get_port_status():
    # 判断失误状况：端口号未加双引号find "22999"
    p = subprocess.Popen('cmd.exe /c' + r'netstat -ano -p tcp | find "22999" >nul 2>nul && echo 22999 opend || echo 22999 closed',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline = p.stdout.readline()
    while curline != b'':
        curlines = str(curline).replace('\\r\\n', '')
        curline = p.stdout.readline()
    p.wait()
    if curlines == "b'22999 closed'":
        return False
    else:
        return True


def wait_port_opening(process_flag):
    opening_times = 1
    while True:
        port_status = get_port_status()
        if port_status:
            print('Port ready!')
            break
        else:
            print('Port not ready, waiting...')
            time.sleep(10)
            opening_times += 1

        if opening_times > 6:
            process_flag = False
            break 
    return process_flag


def write_txt_time():
    time_hour = int(time.strftime('%H', time.localtime(time.time()))) * 3600
    time_min = int(time.strftime('%M', time.localtime(time.time()))) * 60
    time_sec = int(time.strftime('%S', time.localtime(time.time())))
    time_str = str(time_hour + time_min + time_sec)
    with open(os.path.join(os.path.abspath('.'), 'boot', 'config_time.txt'), 'w', encoding='utf-8') as fp:
        fp.write(time_str)