'''
Author: Vinter Wang
Email: vinterhello@gmail.com
'''
import os
import time
import socket
import sqlite3
import datetime
import subprocess
import configparser
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
from selenium import webdriver

from DBPools import OPMysql

from login_util import login_user

from util import get_user_link
from util import write_txt_time
from util import wait_port_opening

from opration_util import random_browsing
from opration_util import click_our_pin
from opration_util import handle_pop_up
from opration_util import create_board
from opration_util import upload_pic
from opration_util import follow

from gen_lpm_conf import generate_configuration
from gen_lpm_conf import delete_port

from browser import set_selenium_local_session
from browser import close_browser


profile = 'config.ini'
profile_info = configparser.ConfigParser()
profile_info.read(profile, encoding='utf-8')
pro_info_items = dict(profile_info.items('pinterest'))

MYSQLINFO = {
    "host": pro_info_items['host'],
    "user": pro_info_items['user'],
    "password": pro_info_items['password'],
    "db": pro_info_items['db'],
    "port": 3306,
    "charset": 'utf8mb4'
}


class Pinterest():
    def __init__(self):
        super(Pinterest, self).__init__()
        self.conn = None
        self.logger = None
        self.hostname = socket.gethostname()
        self.current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
        self.login_url = 'https://www.pinterest.com/login/?referrer=home_page/'
        self.home_url = 'https://www.pinterest.com/homefeed/'
        self.main_url = 'https://www.pinterest.com/'
        self.browser = None
        self.proxy_type = 0
        self.account_id = 0
        self.email = None
        self.username = None
        self.password = None
        self.port = 0
        self.host_ip = None
        self.proxy_ip = None
        self.zone = None
        self.customer = None
        self.customer_pwd = None
        self.upload_web = None
        self.upload_done = 0
        self.cookies = None
        self.agent = None
        self.success_num = 0
        self.config_id = 0
        self.click_our_pin_control = 0

        # Try to locate the home element. If there is off, you don't need to do all kinds of pop-ups

        # Steps and params to control
        self.upload_pic_control = 0
        self.upload_pic_min = 0
        self.upload_pic_max = 0
        self.random_browsing_control = 0
        self.browsing_pic_min = 0
        self.browsing_pic_max = 0
        self.get_user_name = 0
        self.create_board_num = 0
        self.save_pic_control = 0
        self.follow_num = 0
        self.pin_self_count = 0
        self.created_boards = 0
        self.search_words_count = 0
        self.scroll_num = 0

    def action(self):
        while True:
            process_flag = True
            if self.success_num > 10:
                os.system('shutdown -r')
                self.logger.info('Clear cache')
                time.sleep(9999)
            write_txt_time()
            self.conn = OPMysql(MYSQLINFO)
            self.get_account_count()
            self.get_account()
            self.logger = self.get_pinbot_logger(False, True)
            self.logger.info("Start account processing...")
            self.logger.info('Host Name: {}'.format(self.hostname))
            self.logger.info('ID: {}'.format(self.account_id))
            self.logger.info('Port: {}'.format(self.port))
            if self.account_id > 0:
                self.get_config()
                self.success_num += 1
                process_flag = wait_port_opening(self.logger, process_flag)
                if process_flag:
                    gen_port_status_code = generate_configuration(self.conn, self.host_ip, self.port, self.proxy_ip, self.zone, self.customer, self.customer_pwd)
                    if gen_port_status_code != 200:
                        process_flag = False
                else:
                    self.logger.info('Wait more than 60 seconds for the port to be ready, attempt to restart machine!')
                    os.system('shutdown -r')
                    time.sleep(9999)

                write_txt_time()
                if process_flag:
                    self.browser = set_selenium_local_session(
                        self.host_ip,
                        self.port,
                        False,
                        None,
                        25,
                        self.logger
                    )

                    login_state = login_user(
                        self.browser, self.logger, self.conn, self.proxy_ip, self.login_url, self.main_url, self.account_id, self.email, self.username, self.password, self.cookies)
                    write_txt_time()
                    time.sleep(1)
                    if login_state == 1 or login_state == 11:
                        sql = "UPDATE account SET state=1, action_time=%s, proxy_err_times=0 WHERE id=%s"
                        self.conn.op_commit(sql, (self.current_time, self.account_id))
                        if login_state == 11:
                            cookies = get_coo(self.browser)
                            sql = 'UPDATE account SET cookies=%s WHERE id=%s'
                            self.conn.op_commit(sql, (cookies, self.account_id))
                        self.browser.get(self.home_url)
                        write_txt_time()
                        time.sleep(5)
                        # handle_pop_up(self.browser)
                    else:
                        if login_state == 2:
                            # sql = 'UPDATE account set proxy_err_times=proxy_err_times+1 where id=%s'
                            # self.conn.op_commit(sql, self.account_id)
                            # sql = 'SELECT proxy_err_times FROM account WHERE id=%s'
                            # r_error = self.conn.op_select_one(sql, self.account_id)
                            # if r_error:
                            #     proxy_err_times = r_error['proxy_err_times']
                    #     if int(proxy_err_times) >= 4:
                            sql = 'UPDATE port_info SET state=2 WHERE port=%s'
                            self.conn.op_commit(sql, self.port)

                            sql = 'UPDATE account SET state=2, action_computer="-" WHERE id=%s'
                            self.conn.op_commit(sql, self.account_id)

                        else:

                            sql = 'UPDATE account SET state=%s, login_times=login_times+1, action_computer="-" WHERE id=%s'
                            # sql = 'UPDATE account SET state=%s, login_times=login_times+1 WHERE id=%s'
                            self.conn.op_commit(sql, (login_state, self.account_id))
                            process_flag = False
                            self.logger.info('Login false! will exit the browser!')

                        close_browser(self.browser, self.logger)
                        time.sleep(5)

                        self.conn.dispose()
                        delete_port(self.port, self.host_ip)
                        write_txt_time()

                        continue

                if process_flag:
                    
                    if self.get_user_name == 1 and self.username == '-':
                        self.logger.info('Get username!')
                        self.username = get_user_link(self.browser, self.logger, self.conn, self.account_id)
                        # save_home_url(self.browser, self.logger, self.conn, self.account_id)

                    # if self.create_board_num > 0 and self.created_boards < self.create_board_num:
                    #     self.logger.info('Start create board')
                    #     create_board(self.browser, self.logger, self.conn, self.home_url, self.account_id, self.create_board_num)

                    # if self.follow_num > 0:
                    #     follow(self.browser, self.logger, self.conn, self.home_url, self.account_id, self.follow_num, self.current_time)

                    # if self.random_browsing_control == 1:
                    #     random_browsing(
                    #         self.browser, self.logger, self.conn, self.home_url, self.account_id, process_flag, self.save_pic_control, self.browsing_pic_min, self.browsing_pic_max)
                    
                    # if self.click_our_pin_control == 1:
                    #     click_our_pin(self.browser, self.logger, self.conn, self.home_url, process_flag, self.current_time, self.scroll_num, self.pin_self_count, self.search_words_count, self.account_id)

                    if self.upload_done == 1 and self.upload_web != '-' and self.upload_pic_control == 1:
                        upload_pic(self.browser, self.logger, self.conn, process_flag, self.current_time, self.account_id, self.username, self.upload_web, self.upload_pic_min, self.upload_pic_max)

                    self.logger.info('End of account processing...')
                    time.sleep(3)
                    close_browser(self.browser, self.logger)
                    sql = 'UPDATE account SET login_times=0, job_done=1, action_computer="-" WHERE id=%s'
                    self.conn.op_commit(sql, self.account_id)
                    self.conn.dispose()
                    delete_port(self.port, self.host_ip)
                    write_txt_time()
                    time.sleep(10)
            else:
                self.logger.info('Not data! The system will reboot in 30 minutes...')
                write_txt_time()
                os.system('shutdown -s -t 5')

                break

    def get_pinbot_logger(self, save_logs: bool, show_logs: bool, log_handler=None):
        logger = logging.getLogger(self.email)
        logger.setLevel(logging.DEBUG)
        # log name and format
        general_log = "general.log"

        extra = {"username": self.email}
        logger_formatter = logging.Formatter(
            "%(levelname)s [%(asctime)s] [%(username)s]  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        if save_logs is True:
            file_handler = logging.FileHandler(general_log)
            # log rotation, 5 logs with 10MB size each one
            file_handler = RotatingFileHandler(
                general_log, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)

            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

        # add custom user handler if given
        if log_handler:
            logger.addHandler(log_handler)

        if show_logs is True:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logger_formatter)
            logger.addHandler(console_handler)

        logger = logging.LoggerAdapter(logger, extra)

        return logger

    # Access to the account
    def get_account(self):
        if self.hostname == 'v-PC':
            self.host_ip = '127.0.0.1'
            sql = 'SELECT * FROM account WHERE id=5441'
            result = self.conn.op_select_one(sql)
            self.get_account_info(result)
        else:
            sql = 'SELECT * from virtual_machine_info where v_name="proxy"'
            machine_info = self.conn.op_select_one(sql)
            if machine_info:
                self.host_ip = machine_info['host_ip']
            sql = "SELECT * FROM account WHERE action_computer=%s AND job_done=0 AND state=1 AND setting_num=6 AND login_times<3 ORDER BY action_time ASC LIMIT 1"
            result = self.conn.op_select_one(sql, self.hostname)

            if result:
                self.get_account_info(result)
            else:
                sql = "SELECT * FROM account WHERE action_computer='-' AND job_done=0 AND state=1 AND setting_num=6 AND login_times<3 ORDER BY action_time ASC limit 1"
                result = self.conn.op_select_one(sql)

                if result:
                    self.get_account_info(result)

                    sql = "UPDATE account SET action_computer=%s WHERE id=%s"
                    self.conn.op_commit(sql, (self.hostname, self.account_id))
                    write_txt_time()

    def get_account_info(self, result):
        self.account_id = result["id"]
        self.email = result["email"]
        self.password = result["pw"]
        self.port = result['port']
        self.username = result['username']
        self.upload_web = result['upload_web']
        self.upload_done = result['upload_done']
        self.cookies = result['cookies']
        self.created_boards = result['created_boards']
        self.config_id = result['setting_num']
        self.agent = result['agent']

        sql = 'SELECT ip FROM port_info WHERE port=%s'
        port_res = self.conn.op_select_one(sql, self.port)
        if port_res:
            self.proxy_ip = port_res['ip']
            sql = 'SELECT * FROM proxy_account_info WHERE id=1'
            lpm_info = self.conn.op_select_one(sql)
            if lpm_info:
                self.zone = lpm_info['zone']
                self.customer = lpm_info['customer']
                self.customer_pwd = lpm_info['customer_pwd']

        if not self.agent:
            sql = 'SELECT * FROM user_agent WHERE terminal="computer" ORDER BY RAND() LIMIT 1'
            agent_in_sql = self.conn.op_select_one(sql)
            if agent_in_sql:
                self.agent = agent_in_sql['user_agent']
                agent_id = agent_in_sql['Id']
                sql = 'UPDATE account SET agent=%s WHERE id=%s'
                self.conn.op_commit(sql, (self.agent, self.account_id))

    # 浏览器初始化配置
    def re_driver(self):
        execute_path = os.path.abspath('.')
        webdriver_path = os.path.join(execute_path, 'boot', 'geckodriver.exe')
        user_data_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        cookies_file_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'default', 'Cookies')
        # 尝试关闭已经打开的浏览器进程
        try:
            os.popen('taskkill /f /im chrome.exe')
        except:
            pass

        # 清除cookies
        try:
            sql = 'DROP table cookies'
            sqlite_conn = sqlite3.connect("cookies")
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(sql)
        except:
            pass
        options = webdriver.ChromeOptions()
        # options.add_argument('--incognito') # 无痕模式
        options.add_experimental_option('useAutomationExtension', False) # 躲避网站检测webdriver
        options.add_experimental_option("excludeSwitches", ['enable-automation']) # 关闭chrome正受到自动测试软件的控制的提示

        # window.navigator.webdriver
        # 躲避网站检测webdriver
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")

        options.add_argument('--disable-gpu') # 规避bug
        options.add_argument('blink-settings=imagesEnabled=false') # 不加载图片, 提升速度
        options.add_argument('--no-sandbox') # 以最高权限运行
        options.add_argument('--disable-popup-blocking') # 禁止弹窗
        # options.add_argument('user-data-dir=%s' % user_data_path) # 使用浏览器配置文件  
        options.add_argument('user-agent=%s' % self.agent)
        if self.hostname != 'DESKTOP-KHDQKRQ':
            options.add_argument(
                "--proxy-server=http://%s:%d" % (self.host_ip, self.port))

        self.browser = webdriver.Chrome(executable_path=webdriver_path, options=options)
        # self.logger.info(driver.execute_script("return navigator.userAgent;")) # UA设置是否成功
        # 躲避网站检测webdriver, 此方法暂时弃用, 因为这会导致不一致
        # self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #   "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #       get: () => undefined
        #     })
        #   """
        # })
        self.browser.maximize_window()

    def get_account_count(self):
        sql = 'SELECT * FROM account_count WHERE id=1'
        result = self.conn.op_select_one(sql)
        if result:
            all_count = result['all_count']
            real_time_num = result['real_time_num']
            max_error_num = result['max_error_num']
            last_update_time = result['last_update_time']
            if str(last_update_time) < self.current_time:
                sql = 'SELECT state, COUNT(1) AS status_count FROM account GROUP BY state'
                all_status = self.conn.op_select_all(sql)
                if all_status:
                    status_0 = status_1 = status_2 = status_9 = status_66 = status_99 = 0
                    for status in all_status:
                        if int(status['state']) == 0:
                            status_0 = status['status_count']
                        if int(status['state']) == 1:
                            status_1 = status['status_count']
                        if int(status['state']) == 2:
                            status_2 = status['status_count']
                        if int(status['state']) == 9:
                            status_9 = status['status_count']
                        if int(status['state']) == 66:
                            status_66 = status['status_count']
                        if int(status['state']) == 99:
                            status_99 = status['status_count']
                    sql = 'INSERT INTO account_status_statistics (status_0, status_1, status_2, status_9, status_66, status_99, up_time) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                    self.conn.op_commit(sql, (
                        status_0, status_1, status_2,  status_9, status_66, status_99, self.current_time))
                recovery_mode = 'UPDATE account SET state=1 WHERE state=0'
                self.conn.op_commit(recovery_mode)
                recovery_job = 'UPDATE account SET job_done=0 WHERE state=1'
                self.conn.op_commit(recovery_job)
                recovery_proxy_state = 'UPDATE account set state=1 WHERE state=2 and proxy_err_times<4'
                self.conn.op_commit(recovery_proxy_state)
                sql = '''UPDATE account_count SET last_update_time=%s, all_count=
                    (SELECT COUNT(1) FROM account WHERE state=1), 
                    real_time_num=(SELECT count(1) FROM account WHERE state=1) WHERE id=1'''
                self.conn.op_commit(sql, self.current_time)
            else:
                sql = 'UPDATE account_count SET real_time_num=(SELECT count(1) FROM account WHERE state=1) WHERE id=1'
                self.conn.op_commit(sql)

        if all_count - real_time_num > max_error_num:
            self.logger.info('Too many account errors today to suspend operations!')
            self.logger.info('The maximum error limit of {} accounts has been exceeded!'.format(max_error_num))
            os.system('shutdown -r -t 1800')
            time.sleep(9999)

    def get_config(self):
        self.logger.info('Run configuration: {}'.format(self.config_id))
        sql = 'SELECT * FROM configuration WHERE id=%s'
        result = self.conn.op_select_one(sql, self.config_id)
        if result:
            self.random_browsing_control = result['random_browsing_control']
            self.browsing_pic_min = result['bro_pic_min']
            self.browsing_pic_max = result['bro_pic_max']
            self.get_user_name = result['get_user_name']
            self.save_pic_control = result['save_pic_control']
            self.follow_num = result['follow_num']
            self.pin_self_count = result['pin_self_count']
            self.create_board_num = result['create_board_num']
            self.search_words_count = result['search_words_count']
            self.scroll_num = result['scroll_num']
            self.click_our_pin_control = result['click_our_pin_control']
            self.upload_pic_control = result['upload_pic_control']
            self.upload_pic_min = result['upload_pic_min']
            self.upload_pic_max = result['upload_pic_max']


if __name__ == '__main__':
    go = Pinterest()
    go.action()