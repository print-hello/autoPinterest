import time
import json
import random

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from util import explicit_wait
from util import reload_webpage
from util import web_address_navigator
from util import check_authorization
from util import get_current_url
from time_util import sleep

from xpath import read_xpath


def login_user(browser, logger, conn, proxy_ip, login_url, main_url, account_id, email, username, password, cookies):

    if not check_browser(browser, logger, proxy_ip):
        login_state = 2

        return login_state

    web_address_navigator(browser, login_url)

    current_url = get_current_url(browser)
    if 'www.pinterest.com' not in current_url:
        cookies = False

    cookie_loaded = None
    login_state = None

    if cookies:
        try:
            for cookie in json.loads(cookies):
                if "sameSite" in cookie and cookie["sameSite"] == "None":
                    cookie["sameSite"] = "Strict"

                browser.add_cookie(cookie)

            cookie_loaded = True
            logger.info("- Cookie for user '{}' loaded...".format(email))

            # force refresh after cookie load or check_authorization() will FAIL
            reload_webpage(browser)

            # cookie has been LOADED, so the user SHOULD be logged in
            login_state = check_authorization(
                browser, email, "activity counts", logger, False
            )

        except:

            login_state = 0

    if login_state == 1 and cookie_loaded:

        logger.info("Logged in successfully!")
        login_state = 1
        return login_state

    # if user is still not logged in, then there is an issue with the cookie
    # so go create a new cookie.
    if cookie_loaded:
        logger.info(
            "- Issue with cookie for user '{}'. Creating new cookie...".format(email)
        )

        # Error could be faced due to "<button class="sqdOP L3NKy y3zKF"
        # type="button"> Cookie could not be loaded" or similar.
        # Session displayed we are in, but then a failure for the first
        # `login_elem` like the element is no longer attached to the DOM.
        # Saw this issue when session hasn't been used for a while; wich means
        # "expiry" values in cookie are outdated.
        try:
            # Since having issues with the cookie a new one can be generated,
            # if cookie cannot be created or deleted stop execution.
            logger.info("- Deleting browser cookies...")
            browser.delete_all_cookies()
            browser.refresh()
            time.sleep(random.randint(3, 5))

        except Exception as e:
            # NF: start
            if isinstance(e, WebDriverException):
                logger.exception(
                    "Error occurred while deleting cookies from web browser!\n\t{}".format(
                        str(e).encode("utf-8")
                    )
                )
            login_state = 3

            return login_state
            # NF: end

    web_address_navigator(browser, login_url)

    input_username_XP = read_xpath(login_user.__name__, "input_username_XP")
    explicit_wait(browser, logger, "VOEL", [input_username_XP, "XPath"], 35)

    # user
    input_username = browser.find_element_by_xpath(input_username_XP)

    (
        ActionChains(browser)
        .move_to_element(input_username)
        .click()
        .send_keys(email)
        .perform()
    )

    input_password = browser.find_elements_by_xpath(
        read_xpath(login_user.__name__, "input_password")
    )

    if not isinstance(password, str):
        password = str(password)

    (
        ActionChains(browser)
        .move_to_element(input_password[0])
        .click()
        .send_keys(password)
        .perform()
    )

    sleep(1)

    (
        ActionChains(browser)
        .move_to_element(input_password[0])
        .click()
        .send_keys(Keys.ENTER)
        .perform()
    )

    sleep(3)

    # check for wrong username or password message, and show it to the user
    try:
        error_alert = browser.find_element_by_xpath(
            "//*[contains(text(), 'The password you entered is incorrect')]"
        )
        logger.warn(error_alert.text)
        login_state = 4

        return login_state
    except NoSuchElementException:
        pass

    try:
        error_alert = browser.find_element_by_xpath(
            "//*[contains(text(), 'Safe mode alert')]"
        )
        logger.warn(error_alert.text)
        login_state = 5

        return login_state
    except NoSuchElementException:
        pass

    try:
        error_alert = browser.find_element_by_xpath(
            "//*[contains(text(), 'Your account has been suspended.')]"
        )
        logger.warn(error_alert.text)
        login_state = 99

        return login_state
    except NoSuchElementException:
        pass

    try:
        error_alert = browser.find_element_by_xpath(
            "//*[contains(text(), 'Want fresh ideas in your feed')]"
        )
        logger.warn(error_alert.text)

        reload_webpage(browser)


    except NoSuchElementException:
        pass

    explicit_wait(browser, logger, "PFL", [], 5)

    # Check if user is logged-in (If there's two 'nav' elements)
    nav = browser.find_elements_by_xpath(read_xpath(login_user.__name__, "nav"))
    if len(nav) == 1:
        logger.info("Logged in successfully!")
        login_state = 1
        # create cookie for username and save it
        cookies_list = browser.get_cookies()

        for cookie in cookies_list:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"

        cookies_list = json.dumps(cookies_list)
        sql = 'UPDATE account SET cookies=%s WHERE id=%s'
        conn.op_commit(sql, (cookies_list, account_id))

        return login_state

    else:
        login_state = 0

        return login_state


def check_browser(browser, logger, proxy_ip):

    try:
        logger.info("-- Connection Checklist [1/2] (Internet Connection Status)")
        browser.get("view-source:https://ip4.seeip.org/geoip")
        pre = browser.find_element_by_tag_name("pre").text
        current_ip_info = json.loads(pre)
        if (
            proxy_ip is not None
            and proxy_ip != current_ip_info["ip"]
        ):
            logger.info("- Proxy is set, but it's not working properly")
            logger.info(
                '- Expected Proxy IP is "{}", and the current IP is "{}"'.format(
                    proxy_ip, current_ip_info["ip"]
                )
            )
            logger.info("- Try again or disable the Proxy Address on your setup")
            logger.info("- Aborting connection...")
            return False
        else:
            logger.info("- Internet Connection Status: ok")
            logger.info(
                '- Current IP is "{}" and it\'s from "{}/{}"'.format(
                    current_ip_info["ip"],
                    current_ip_info["country"],
                    current_ip_info["country_code"],
                )
            )

    except Exception:
        logger.info("- Internet Connection Status: error")

        return False

    # check if hide-selenium extension is running
    logger.info("-- Connection Checklist [2/2] (Hide Selenium Extension)")
    webdriver = browser.execute_script("return window.navigator.webdriver")
    logger.info("- window.navigator.webdriver response: {}".format(webdriver))
    if webdriver:
        logger.info("- Hide Selenium Extension: error")
    else:
        logger.info("- Hide Selenium Extension: ok")

    return True