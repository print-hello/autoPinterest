import os
import re
import time
import requests
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

from time_util import sleep
from time_util import sleep_actual

from xpath import read_xpath


def explicit_wait(browser, logger, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH 
                   if find_method == "XPath" 
                   else By.CSS_SELECTOR 
                   if find_method == "CSS" 
                   else By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "PFL":
        ec_name = "page fully loaded"
        condition = lambda browser: browser.execute_script(
            "return document.readyState"
        ) in ["complete" or "loaded"]

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(browser, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            logger.info(
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


def wait_port_opening(logger, process_flag):
    opening_times = 1
    while True:
        port_status = get_port_status()
        if port_status:
            logger.info('Port ready!')
            break
        else:
            logger.info('Port not ready, waiting...')
            sleep(10)
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


def web_address_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be
    navigated and if it is different, it does navigate"""
    current_url = get_current_url(browser)
    total_timeouts = 0
    page_type = None  # file or directory

    # remove slashes at the end to compare efficiently
    if current_url is not None and current_url.endswith("/"):
        current_url = current_url[:-1]

    if link.endswith("/"):
        link = link[:-1]
        page_type = "dir"  # slash at the end is a directory

    new_navigation = current_url != link

    if current_url is None or new_navigation:
        link = link + "/" if page_type == "dir" else link  # directory links
        # navigate faster

        while True:
            try:
                browser.get(link)
                # update server calls
                # update_activity(browser, state=None)
                sleep(2)
                break

            except TimeoutException as exc:
                if total_timeouts >= 7:
                    raise TimeoutException(
                        "Retried {} times to GET '{}' webpage "
                        "but failed out of a timeout!\n\t{}".format(
                            total_timeouts,
                            str(link).encode("utf-8"),
                            str(exc).encode("utf-8"),
                        )
                    )
                total_timeouts += 1
                sleep(2)


def reload_webpage(browser):
    """ Reload the current webpage """
    browser.execute_script("location.reload()")
    # update_activity(browser, state=None)
    sleep(2)

    return True


def check_authorization(browser, email, method, logger, notify=True):
    """ Check if user is NOW logged in """
    if notify is True:
        logger.info("Checking if '{}' is logged in...".format(email))

    # different methods can be added in future
    if method == "activity counts":

        # navigate to owner's profile page only if it is on an unusual page
        current_url = get_current_url(browser)
        if (
            not current_url
            or "https://www.pinterest.com" not in current_url
            # or "https://www.pinterest.com/graphql/" in current_url
        ):
            profile_link = "https://www.pinterest.com"
            web_address_navigator(browser, profile_link)

        nav = browser.find_elements_by_xpath("//nav/div[@data-test-id='footer']")
        if len(nav) == 0:

            login_state = 0

            if notify is True:
                logger.info("--> '{}' is not logged in!\n".format(email))

            return login_state

        else:

            login_state = 1

    return login_state


def get_current_url(browser):
    """ Get URL of the loaded webpage """
    try:
        current_url = browser.execute_script("return window.location.href")

    except WebDriverException:
        try:
            current_url = browser.current_url

        except WebDriverException:
            current_url = None

    return current_url


def get_user_link(browser, logger, conn, account_id):
    """ Gets the followers & following counts of a given user """

    user_name = None

    try:
        user_name = browser.find_elements_by_xpath(
            "//nav/div[@data-test-id='footer']/div/div/div/div/a")[-1].get_attribute("href")    

    except NoSuchElementException:
        try:
            browser.execute_script("location.reload()")

            user_name = browser.find_elements_by_xpath(
                "//nav/div[@data-test-id='footer']/div/div/div/div/a")[-1].get_attribute("href")

        except WebDriverException:
            logger.error(
                "Error occurred during getting the user link "
            )
            user_name = None

    if user_name:
        user_name = user_name.rstrip('/').split('/')[-1]
        sql = 'UPDATE account SET username=%s WHERE id=%s'
        conn.op_commit(sql, (user_name, account_id))

    return user_name