'''
Pinterest 操作
'''
import time
import datetime
import random
import win32api
import win32con
from urllib.parse import quote
from selenium.webdriver.common.action_chains import ActionChains

from util import explicit_wait
from util import write_txt_time
from util import get_current_url


def handle_pop_up(browser, logger):
    try:
        browser.find_element_by_xpath(
            "//span[text()='Female']").click()
        time.sleep(2)
    except:
        pass

    try:
        click_confirm = browser.switch_to.alert
        click_confirm.accept()
        time.sleep(2)
    except Exception as e:
        logger.info('No popovers to process, skip...')

    try:
        browser.find_element_by_xpath(
            '//div[@class="NuxPickerFooter"]//button').click()
        logger.info('Preference already selected')
        time.sleep(2)
    except Exception as e:
        logger.info('No need to select preference, skip...')

    try:
        browser.find_element_by_xpath(
            '//div[@class="ReactModalPortal"]//button[@aria-label="cancel"]').click()
        logger.info('Preference set')
        time.sleep(2)
    except Exception as e:
        logger.info('No preference Settings, skip...')

    try:
        browser.find_element_by_xpath(
            '//div[@class="ReactModalPortal"]//button').click()
        logger.info('Email has been confirmed')
        time.sleep(2)
    except Exception as e:
        logger.info('No need to confirm email, skip...')

    try:
        browser.find_element_by_xpath(
            "//div[@class='NagBase']/div/div[2]/button").click()
        logger.info('The renewal agreement has been accepted')
        time.sleep(2)
    except Exception as e:
        logger.info('No need to accept the update protocol, skip...')

    try:
        browser.find_element_by_xpath(
            '//button[@aria-label="Hide Checklist"]').click()
    except:
        pass


def upload_pic(browser, logger, conn, process_flag, current_time, account_id, username, upload_web, upload_pic_min, upload_pic_max):
    all_upload_num = random.randint(upload_pic_min, upload_pic_max)
    logger.info('Start uploading %s images...' % all_upload_num)
    upload_web_split = upload_web.split('.')
    upload_web_replace = upload_web_split[-2] + '.' + upload_web_split[-1]
    save_error = 0

    while True:
        table_name = None
        upload_flag = 1
        replace_domain = 0
        save_time = (datetime.datetime.utcnow() +
                     datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

        sql = 'SELECT * FROM upload_url where url=%s'
        result_1 = conn.op_select_one(sql, upload_web)
        if result_1:
            data_type = result_1['data_type']

            sql = 'SELECT * FROM database_relation WHERE data_type=%s'
            result_2 = conn.op_select_one(sql, data_type)
            if result_2:
                table_name = result_2['table_name']

        if table_name:

            sql = "SELECT COUNT(-1) AS allnum FROM %s WHERE id_of_saved='%s' AND save_time>='%s'" % (table_name, account_id, current_time)
            upload_num = conn.op_select_one(
                sql)['allnum']

            if upload_num < all_upload_num:
                random_time = random.randint(10, 30)
                time.sleep(random_time)

                if upload_web == 'original':
                    sql = 'SELECT * FROM pin_upload WHERE saved=0 and data_type=%s ORDER BY RAND() LIMIT 1'
                    result = conn.op_select_one(sql, upload_web)

                elif data_type == 'binding.domain.zhishuai.online':
                    sql = 'SELECT * FROM %s WHERE saved=0 and belong_web="%s" ORDER BY RAND() LIMIT 1' % (table_name, upload_web)
                    result = conn.op_select_one(sql)

                else:
                    replace_domain = 1

                    sql = 'SELECT * FROM %s WHERE saved=0 and data_type="%s" ORDER BY RAND() LIMIT 1' % (table_name, data_type)
                    result = conn.op_select_one(sql)

                if result:

                    upload_pic_path = result['savelink']
                    if replace_domain == 1:
                        upload_pic_path = upload_pic_path.replace('xxx.com', upload_web_replace)
                    upload_pic_board = result['saveboard']
                    upload_pic_id = result['id']
                    browser.get(upload_pic_path)

                    select_board_XP = "//div//h3[text()='%s']/../../../.." % upload_pic_board
                    select_board_XP_flag = explicit_wait(
                        browser, logger, "VOEL", [select_board_XP, "XPath"], 10, False)

                    if select_board_XP_flag:
                        select_board = browser.find_elements_by_xpath(select_board_XP)[-1]
                        browser.execute_script("arguments[0].scrollIntoView();", select_board)
                        for _ in range(2):
                            win32api.keybd_event(38, 0, 0, 0)
                            win32api.keybd_event(
                                38, 0, win32con.KEYEVENTF_KEYUP, 0)

                        time.sleep(3)

                        try:
                            (ActionChains(browser).move_to_element(select_board).click().perform())
                        except:
                            pass

                    else:
                        create_board_XP = "//a[contains(@href,'/board/create/')]"
                        create_board_XP_flag = explicit_wait(
                            browser, logger, "VOEL", [create_board_XP, "XPath"], 5, False)

                        if create_board_XP_flag:

                            create_board = browser.find_element_by_xpath(create_board_XP)
                            try:
                                (ActionChains(browser).move_to_element(create_board).click().perform())
                            except:
                                pass

                            input_board_name_XP = '//input[@id="boardNameInput"]'
                            input_board_name_flag = explicit_wait(
                                browser, logger, "VOEL", [input_board_name_XP, "XPath"], 10, False)
                            if input_board_name_flag:
                                time.sleep(2)
                                browser.find_element_by_xpath(
                                    input_board_name_XP).send_keys(upload_pic_board)

                                create_button = browser.find_element_by_xpath("//div[text()='Create']/..")
                                (ActionChains(browser).move_to_element(create_button).click().perform())

                        else:
                            logger.info('Image save failed, Element not found')
                            upload_flag = 0

                    if upload_flag == 1:
                        time.sleep(5)
                        current_url = get_current_url(browser)

                        # upload_pic_board_replace = upload_pic_board.lower().replace('amp;', '').replace(',', '').replace('&', '').split(' ')
                        # url_board_name = ''
                        # for i in upload_pic_board_replace:
                        #     if i:
                        #         if url_board_name:
                        #             url_board_name = url_board_name + '-' + i
                        #         else:
                        #             url_board_name = url_board_name + i

                        if username.lower() in current_url.lower():
                            logger.info('Image {} upload done!'.format(upload_pic_id))
                            write_txt_time()

                            sql = "UPDATE %s SET saved=1, id_of_saved='%s', save_time='%s' WHERE id='%s'" % (table_name, account_id, save_time, upload_pic_id)
                            conn.op_commit(sql)

                        else:
                            save_error += 1
                            if save_error > 3:
                                sql = "UPDATE account SET upload_done=4 WHERE id=%s"
                                conn.op_commit(sql, account_id)

                                break


                else:
                    sql = "UPDATE account SET upload_done=9 WHERE id=%s"
                    conn.op_commit(sql, account_id)
                    logger.info('There is no data on this domain!')
                    write_txt_time()
                    break


            else:
                logger.info('Enough pictures have been uploaded for today!')
                write_txt_time()
                break
    time.sleep(2)


# Random browse
def random_browsing(browser,
                    logger,
                    conn,
                    homefeed_url,
                    account_id,
                    process_flag,
                    save_pic_control,
                    browsing_pic_min,
                    browsing_pic_max,
                    board_name='like'):

    random_browsing_num = random.randint(
        browsing_pic_min, browsing_pic_max)
    logger.info('Start random browsing:', random_browsing_num, 'time')
    for i in range(random_browsing_num):

        web_pin_arr_XP = '//div[@data-grid-item="true"]'
        web_pin_arr_flag = explicit_wait(
            browser, logger, "VOEL", [web_pin_arr_XP, "XPath"], 10, False)
        if web_pin_arr_flag:

            web_pin_arr = browser.find_elements_by_xpath(web_pin_arr_XP)
            click_num = random.randint(1, 8)
            web_pin_num = 1
            for web_pin_one in web_pin_arr:
                if web_pin_num == click_num:
                    time.sleep(3)
                    web_pin_one.click()
                    logger.info('Start the', i + 1, 'browsing')
                    time.sleep(5)

                    try:
                        close_AD_page(browser)
                    except Exception as e:
                        if save_pic_control == 1 and (i + 1) % 2 == 0:
                            save_pic(browser, conn, homefeed_url,
                                     account_id, process_flag, send_keys=0)

                    win32api.keybd_event(27, 0, 0, 0)
                    win32api.keybd_event(
                        27, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(3)

                    win32api.keybd_event(35, 0, 0, 0)
                    win32api.keybd_event(
                        35, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(5)
                    break
                else:
                    web_pin_num += 1

                write_txt_time()
        else:
            process_flag = 0


def close_AD_page(browser, logger):
    windows = browser.window_handles
    # Gets the new page handle
    browser.switch_to.window(windows[1])
    browser.close()
    logger.info('Close the AD page')
    time.sleep(1)
    # go back to the original interface
    browser.switch_to.window(windows[0])
    time.sleep(1)


# save a picture
def save_pic(browser, logger, conn, homefeed_url, account_id, process_flag, board_name='like', belong=2, pin_pic_url=False, send_keys=1):

    add_time = (datetime.datetime.utcnow() +
                datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    if not pin_pic_url:
        pin_pic_XP = "//body/div[@id='__PWS_ROOT__']/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/a/div/div/div/img[1]"
        pin_pic_flag = explicit_wait(
            browser, logger, "VOEL", [pin_pic_XP, "XPath"], 3, False)
        if pin_pic_flag:
            pin_pic_url = browser.find_element_by_xpath(
                pin_pic_XP).get_attribute('src')

    saved_XP = "//span[contains(text(),'Saved to')]"
    saved_flag = explicit_wait(browser, logger, "VOEL", [saved_XP, "XPath"], 5, False)
    if saved_flag:
        logger.info('The picture has been saved.')
    else:
        if belong == 2:
            sql = 'SELECT * FROM other_pin_history WHERE pin_pic_url=%s AND id=%s'
        elif belong == 1:
            sql = 'SELECT * FROM pin_history WHERE pin_pic_url=%s AND id=%s'
        result = conn.op_select_one(sql, (pin_pic_url, account_id))
        if result:
            logger.info('The picture has been saved.')
        else:
            board_select_XP = '//button[@data-test-id="PinBetterSaveDropdown"]'
            board_select_flag = explicit_wait(
                browser, logger, "VOEL", [board_select_XP, "XPath"], 10, False)
            if board_select_flag:
                board_select = browser.find_element_by_xpath(board_select_XP)
                (ActionChains(browser)
                 .move_to_element(board_select)
                 .click()
                 .perform())

                input_board_XP = '//input[@id="pickerSearchField"]'
                input_board_flag = explicit_wait(
                    browser, logger, "VOEL", [input_board_XP, "XPath"], 10, False)
                if input_board_flag:
                    browser.find_element_by_xpath(
                        input_board_XP).send_keys(board_name)
                    time.sleep(5)

                    try:
                        choice_board = browser.find_elements_by_xpath(
                            '//div[@data-test-id="boardWithoutSection"]//div[text()="%s"]' % board_name)
                        (ActionChains(browser)
                         .move_to_element(choice_board[0])
                         .click()
                         .perform())
                        time.sleep(2)
                    except Exception as e:
                        create_XP = '//div[@data-test-id="create-board"]/div'
                        create_flag = explicit_wait(
                            browser, logger, "VOEL", [create_XP, "XPath"], 10, False)
                        if create_flag:
                            browser.find_element_by_xpath(create_XP).click()

                            process_flag = input_board_text(browser, board_name, 1, send_keys)

                    if process_flag == 1:
                        if belong == 2:
                            sql = 'INSERT INTO other_pin_history (account_id, pin_pic_url, add_time) VALUES (%s, %s, %s)'
                        elif belong == 1:
                            sql = 'INSERT INTO pin_history (account_id, pin_pic_url, add_time) VALUES (%s, %s, %s)'

                        conn.op_commit(
                            sql, (account_id, pin_pic_url, add_time))
                    else:
                        browser.get(homefeed_url)

        write_txt_time()


def create_board(browser, logger, conn, homefeed_url, account_id, create_board_num):
    sql = "SELECT home_page FROM account WHERE id=%s"
    result = conn.op_select_one(sql, account_id)
    if result:
        boards_page = result['home_page'] + 'boards'
        sql = "SELECT board_name FROM board_template ORDER BY RAND() LIMIT %s"
        results = conn.op_select_all(sql, create_board_num)
        for board_echo in results:
            cr_bo_success = 1
            board_name = board_echo['board_name']
            logger.info('Boardname', board_name)

            browser.get(boards_page)
            # 个人账号按钮
            display_add_XP = "//body//div[@id='__PWS_ROOT__']//div//div//div[3]//div[2]//div[1]//div[1]//button[1]"
            display_add_flag = explicit_wait(
                browser, logger, "VOEL", [display_add_XP, "XPath"], 30, False)
            if display_add_flag:

                browser.find_element_by_xpath(display_add_XP).click()
                create_button_XP = '//div[@data-test-id="Create board"]'
                create_button_flag = explicit_wait(
                    browser, logger, "VOEL", [create_button_XP, "XPath"], 30, False)

                if create_button_flag:
                    browser.find_element_by_xpath(create_button_XP).click()
                else:
                    cr_bo_success = 0
            else:
                # 商业账号按钮
                try:
                    browser.find_element_by_xpath(
                        "//body/div[@id='__PWS_ROOT__']/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]").click()
                except:
                    cr_bo_success = 0

            if cr_bo_success == 1:
                cr_bo_success = input_board_text(
                    browser, board_name, cr_bo_success)
                try:
                    browser.find_element_by_xpath('//button[@aria-label="Done"]').click()
                    time.sleep(1)
                except:
                    pass

            if cr_bo_success == 1:
                sql = "UPDATE account SET created_boards=created_boards+1 WHERE id=%s"
                conn.op_commit(sql, account_id)

            write_txt_time()

        browser.get(homefeed_url)


def input_board_text(browser, logger, board_name, cr_bo_success, send_keys=1):
    input_board_XP = '//input[@id="boardEditName"]'
    input_board_flag = explicit_wait(
        browser, logger, "VOEL", [input_board_XP, "XPath"], 15, False)
    if input_board_flag:
        time.sleep(3)

        if send_keys == 1:
            browser.find_element_by_xpath(
                input_board_XP).send_keys(board_name)
            time.sleep(1)

        create_button = browser.find_element_by_xpath(
            "//button/div[contains(text(),'Create')]")
        (ActionChains(browser)
         .move_to_element(create_button)
         .click()
         .perform())

        create_error_XP = '//*[starts-with(text(), "Could not save board")]'
        create_error_flag = explicit_wait(
            browser, logger, "VOEL", [create_error_XP, "XPath"], 5, False)
        if create_error_flag:
            logger.info('Board already existed!')
            cr_bo_success = 0
    else:
        cr_bo_success = 0

    return cr_bo_success


def click_our_pin(browser,
                  logger,
                  conn,
                  homefeed_url,
                  process_flag,
                  current_time,
                  scroll_num,
                  pin_self_count,
                  search_words_count,
                  account_id):
    logger.info('Start searching for our images')
    sql = "SELECT count(-1) AS allnum FROM pin_history WHERE account_id=%s AND add_time>=%s"
    pin_count = conn.op_select_one(sql, (account_id, current_time))['allnum']
    if pin_count < int(pin_self_count):
        sql = "SELECT web_url FROM website_url WHERE status=1"
        results = conn.op_select_all(sql)
        http_in_sql_list = []
        for res in results:
            http_in_sql = res['web_url']
            http_in_sql_list.append(http_in_sql)
        sql = "SELECT * FROM search_words WHERE word_type=1 ORDER BY RAND() LIMIT %s"
        key_wrods = conn.op_select_all(sql, search_words_count)
        if key_wrods:
            browser.get(homefeed_url)
            time.sleep(5)
            for key_wrod in key_wrods:
                search_key_words = key_wrod['word']
                board_name = key_wrod['boards']
                board_name_encode = quote(board_name, 'utf-8')
                search_url = """https://www.pinterest.com/search/pins/?q={}&rs=typed""".format(board_name_encode)
                board_name_split = board_name.split(' ')
                for _ in board_name_split:
                    search_url += "&term_meta[]={}%7Ctyped".format(_.strip())
                # 个人号搜索键
                # input_search_XP = '//input[@name="searchBoxInput"]'
                # input_search_flag = explicit_wait(
                #     browser, "VOEL", [input_search_XP, "XPath"], 10, False)
                # if not input_search_flag:
                    # 商业号搜索键
                #     input_search_XP = "//div[@id='searchBoxContainer']//button"

                # browser.find_element_by_xpath(input_search_XP).click()
                # time.sleep(1)
                for _ in range(scroll_num):
                    web_pin_arr_XP = '//div[@data-grid-item="true"]'
                    web_pin_arr_flag = explicit_wait(
                        browser, logger, "VOEL", [web_pin_arr_XP, "XPath"], 10, False)
                    if web_pin_arr_flag:
                        web_pin_arr = browser.find_elements_by_xpath(
                            web_pin_arr_XP)
                        for web_pin_one in web_pin_arr:
                            try:
                                ActionChains(browser).move_to_element(
                                    web_pin_one).perform()
                                time.sleep(3)
                                write_txt_time()
                            except:
                                pass
                            try:
                                web_pin_XP = '//a[@class="GestaltTouchableFocus"]/div/div[2]/div[1]'
                                web_pin_flag = explicit_wait(
                                    browser, logger, "VOEL", [web_pin_XP, "XPath"], 3, False)
                                if web_pin_flag:
                                    web_pin_url = browser.find_element_by_xpath(
                                        web_pin_XP).text
                                    if web_pin_url in http_in_sql_list:
                                        time.sleep(1)
                                        pin_pic_url = web_pin_one.find_element_by_xpath(
                                            './/div[@data-test-id="pinrep-image"]//img').get_attribute('src')
                                        save_pic(
                                            browser, conn, homefeed_url, account_id, process_flag, board_name, 1, pin_pic_url)
                                        sql = "SELECT count(-1) AS allnum FROM pin_history WHERE account_id=%s AND add_time>=%s"
                                        pin_count = conn.op_select_one(
                                            sql, (account_id, current_time))['allnum']
                            except:
                                pass

                            if pin_count >= int(pin_self_count):
                                break

                            write_txt_time()

                    if pin_count >= int(pin_self_count):
                        break
                    else:
                        win32api.keybd_event(35, 0, 0, 0)
                        win32api.keybd_event(
                            35, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(5)

                if pin_count >= int(pin_self_count):
                    break

                write_txt_time()

    else:
        logger.info('Saved enough!')


def follow(browser, logger, conn, homefeed_url, account_id, follow_num, current_time):
    sql = 'SELECT * FROM main_promotion_account WHERE account_id=%s'
    is_exist = conn.op_select_one(sql, account_id)
    if not is_exist:
        sql = 'SELECT COUNT(1) AS all_count FROM follow_history WHERE follow_id=%s AND followed_time=%s'
        follow_count = conn.op_select_one(sql, (account_id, current_time))['all_count']
        if follow_count < follow_num:
            sql = 'SELECT user_id, follow_id FROM follow_history WHERE follow_id=%s AND user_id IN (SELECT account_id FROM main_promotion_account)'
            results1 = conn.op_select_all(sql, account_id)
            user_in_history_lst = []
            if results1:

                for r1 in results1:
                    user_id = r1['user_id']
                    user_in_history_lst.append(user_id)

            sql = 'SELECT account_id FROM main_promotion_account WHERE status=1'
            results2 = conn.op_select_all(sql)
            if results2:
                main_promotion_account_lst = []

                for r2 in results2:
                    main_promotion_account_id = r2['account_id']
                    main_promotion_account_lst.append(main_promotion_account_id)
            # 删除已经follow的推广账户id，获得剩余未follow的推广账户id
            if user_in_history_lst:
                for del_id in user_in_history_lst:
                    main_promotion_account_lst.remove(del_id)
            if main_promotion_account_lst:
                if len(main_promotion_account_lst) >= follow_num: 
                    follow_lst = random.sample(main_promotion_account_lst, follow_num)
                else:
                    follow_lst = main_promotion_account_lst
                logger.info('Turn on the follow function, count:', len(follow_lst))

                for follow_id in follow_lst:
                    sql = 'SELECT account_home_url FROM main_promotion_account WHERE account_id=%s'
                    res_follow_url = conn.op_select_one(sql, follow_id)
                    if res_follow_url:
                        follow_url = res_follow_url['account_home_url']                  
                        try:
                            browser.get(follow_url)
                        except:
                            pass
                        follow_XP = "//div[@id='__PWS_ROOT__']//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//button"
                        follow_flag = explicit_wait(
                            browser, logger, "VOEL", [follow_XP, "XPath"], 15, False)
                        if follow_flag:
                            follow_state = follow_flag.find_element_by_xpath(
                                './div').text
                            if follow_state == 'Follow':

                                try:
                                    browser.find_element_by_xpath(
                                        follow_XP).click()
                                    time.sleep(1)
                                except:
                                    pass
                        else:

                            try:
                                follow_state = browser.find_element_by_xpath(
                                    "//div[@id='__PWS_ROOT__']//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//button/div").text
                                if follow_state == 'Follow':
                                    browser.find_element_by_xpath(
                                        "//div[@id='__PWS_ROOT__']//div//div//div//div//div//div//div//div//div//div//div//div//div//div//div//button").click()
                                    time.sleep(1)
                            except:
                                pass
                        sql = 'INSERT INTO follow_history (user_id, follow_id, followed_time) VALUES (%s, %s, %s)'
                        conn.op_commit(sql, (follow_id, account_id, current_time))

                        write_txt_time()

                browser.get(homefeed_url)

            else:
                logger.info('There are no more accounts that need to be followed')
        else:
            logger.info('Today we have followed!')

    else:
        logger.info('Is promotion account, Ban follow!')