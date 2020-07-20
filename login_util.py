import time
import json
from util import explicit_wait


def login(driver, login_url, main_url, account_id, email, pwd, cookies):
    if cookies:
        login_state = cookie_login(driver, main_url, cookies)
    else:
        login_state = 0

    if login_state == 0:
        driver.get(login_url)
        print('Login...')
        if driver.page_source.find('This site can’t be reached') > -1:
            login_state = 2
            print('Net error!')
            return login_state
        elif driver.page_source.find("This page isn’t working") > -1:
            login_state = 2
            print('Net error!')
            return login_state
        else:
            input_email_XP = '//input[@id="email"]'
            input_email_flag = explicit_wait(driver, "VOEL", [input_email_XP, "XPath"], 20, False)
            if input_email_flag:
                driver.find_element_by_xpath(input_email_XP).send_keys(email)
                time.sleep(1)
                driver.find_element_by_name("password").send_keys(pwd)
                time.sleep(1)
                driver.find_element_by_xpath("//form//button").click()
            login_success_XP = '//button[@aria-label="Messages"]'
            login_success_flag = explicit_wait(driver, "VOEL", [login_success_XP, "XPath"], 30, False)
            if login_success_flag:
                login_state = 11
                print('Account login successful!')
            else:
                reset_passwd_XP = '//button[@aria-label="Reset password"]'
                reset_passwd_flag = explicit_wait(driver, "VOEL", [reset_passwd_XP, "XPath"], 5, False)
                if reset_passwd_flag:
                    print('Error code: 9')
                    login_state = 9
                elif driver.page_source.find('Reset your password') > -1:
                    print('Error code: 9')
                    login_state = 9
                elif driver.page_source.find('The email you entered does not belong to any account.') > -1:
                    print('Error code: 66')
                    login_state = 66
                elif driver.page_source.find('Your account has been suspended') > -1:
                    print('Error code: 99')
                    login_state = 99
                else:
                    login_state = 0

    return login_state


def cookie_login(driver, main_url, cookies):
    driver.get(main_url)
    print('Cookies login...')

    try:
        cookies = json.loads(cookies)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(main_url)

    except Exception as e:
        print('The cookies is invalid. You are trying to login')
        login_state = 0
        
        return login_state

    login_success_XP = '//button[@aria-label="Messages"]'
    login_success_flag = explicit_wait(driver, "VOEL", [login_success_XP, "XPath"], 30, False)
    if login_success_flag:
        login_state = 1
        print('Account login successful!')
    else:
        login_state = 0

    return login_state


def get_coo(driver):
    cookies = driver.get_cookies()
    cookies = json.dumps(cookies)

    return cookies