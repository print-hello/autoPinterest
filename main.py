'''
Author: Vinter Wang
Email: printhello@163.com
'''
import os
import time
import socket
import sqlite3
import datetime
import logging.config
from selenium import webdriver

from DBPools import OPMysql

from login_util import login
from login_util import get_coo

from util import write_txt_time
from util import wait_port_opening

from opration_util import random_browsing
from opration_util import save_home_url
from opration_util import click_our_pin
from opration_util import handle_pop_up
from opration_util import create_board
from opration_util import upload_pic
from opration_util import follow

from gen_lpm_conf import generate_configuration
from gen_lpm_conf import delete_port


MYSQLINFO = {
    "host": 'localhost',
    "user": 'pinterest',
    "passwd": '******',
    "db": 'pinterest',
    "port": 3306,
    "charset": 'utf8mb4'
}


class Pinterest():
    def __init__(self):
        super(Pinterest, self).__init__()
        self.conn = OPMysql(MYSQLINFO)
        logging.config.fileConfig('logging.conf')
        self.logs = logging.getLogger()
        email = logging.handlers.SMTPHandler(("smtp.163.com", 25), 'sendlogging@163.com',
                                             ['printhello@163.com'],
                                             "Logging from pinterest",
                                             credentials=(
                                                 'sendlogging@163.com', 'sendlogtome1121'),
                                             )
        self.logs.addHandler(email)
        self.hostname = socket.gethostname()
        self.current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
        self.login_url = 'https://www.pinterest.com/login/?referrer=home_page'
        self.home_url = 'https://www.pinterest.com/homefeed/'
        self.main_url = 'https://www.pinterest.com/'
        self.driver = None
        self.proxy_type = 0
        self.account_id = 0
        self.email = None
        self.pwd = None
        self.port = 0
        self.host_ip = None
        self.proxy_ip = None
        self.zone = None
        self.customer = None
        self.customer_pwd = None
        self.upload_web = None
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
        self.save_home_url_control = 0
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
            if self.success_num > 4:
                os.system('shutdown -r')
                print('Clear cache')
                time.sleep(9999)
            write_txt_time()
            print('Host Name:', self.hostname)
            self.get_account_count()
            self.get_account()
            if self.account_id > 0:
                self.get_config()
                self.success_num += 1
                process_flag = wait_port_opening(process_flag)
                if process_flag:
                    gen_port_status_code = generate_configuration(self.conn, self.port, self.proxy_ip, self.zone, self.customer, self.customer_pwd)
                    if gen_port_status_code != 200:
                        process_flag = False
                else:
                    print('Wait more than 60 seconds for the port to be ready, attempt to restart machine!')
                    os.system('shutdown -r')
                    time.sleep(9999)
                write_txt_time()
                if process_flag:
                    self.re_driver()
                    login_state = login(
                        self.driver, self.login_url, self.main_url, self.account_id, self.email, self.pwd, self.cookies)
                    time.sleep(1)
                    if login_state == 1 or login_state == 11:
                        sql = "UPDATE account SET state=1, action_time=%s, proxy_err_times=0 WHERE id=%s"
                        self.conn.op_commit(sql, (self.current_time, self.account_id))
                        if login_state == 11:
                            cookies = get_coo(self.driver)
                            sql = 'UPDATE account SET cookies=%s WHERE id=%s'
                            self.conn.op_commit(sql, (cookies, self.account_id))
                        self.driver.get(self.home_url)
                        time.sleep(5)
                        handle_pop_up(self.driver)
                    else:
                        if login_state == 2:
                            sql = 'UPDATE account set proxy_err_times=proxy_err_times+1 where id=%s'
                            self.conn.op_commit(sql, self.account_id)
                            sql = 'SELECT proxy_err_times FROM account WHERE id=%s'
                            r_error = self.op_select_one(sql, self.account_id)
                            if r_error:
                                proxy_err_times = r_error['proxy_err_times']
                                if proxy_err_times >= 4:
                                    sql = 'UPDATE port_info SET state=2 WHERE port=%s'
                                    conn.op_commit(sql, self.port)

                        sql = 'UPDATE account SET state=%s, login_times=login_times+1, action_computer="-" WHERE id=%s'     
                        self.conn.op_commit(sql, (login_state, self.account_id))
                        process_flag = False
                        print('Account log-in failure, will exit the browser!')
                        try:
                            self.driver.quit()
                        except:
                            pass
                        time.sleep(5)
                        continue

                if process_flag:
                    
                    if self.save_home_url_control == 1:
                        print('Save home page!')
                        save_home_url(self.driver, self.conn, self.account_id)

                    if self.create_board_num > 0 and self.created_boards < self.create_board_num:
                        print('Start create board')
                        create_board(self.driver, self.conn, self.home_url, self.account_id, self.create_board_num)

                    if self.follow_num > 0:
                        follow(self.driver, self.conn, self.home_url, self.account_id, self.follow_num, self.current_time)

                    if self.random_browsing_control == 1:
                        random_browsing(
                            self.driver, self.conn, self.home_url, self.account_id, process_flag, self.save_pic_control, self.browsing_pic_min, self.browsing_pic_max)
                    
                    if self.click_our_pin_control == 1:
                        click_our_pin(self.driver, self.conn, self.home_url, process_flag, self.current_time, self.scroll_num, self.pin_self_count, self.search_words_count, self.account_id)

                    if self.upload_web != '-' and self.upload_pic_control == 1:
                        upload_pic(self.driver, self.conn, process_flag, self.current_time, self.account_id, self.upload_web, self.upload_pic_min, self.upload_pic_max)

                    print('End of account processing...')
                    time.sleep(3)
                    self.driver.quit()
                    sql = 'UPDATE account SET login_times=0, action_computer="-" WHERE id=%s'
                    self.conn.op_commit(sql, self.account_id)
                    self.conn.dispose()
                    delete_port(self.port)
                    write_txt_time()
                    time.sleep(10)
            else:
                print('Not data! The system will reboot in 30 minutes...')
                write_txt_time()
                os.system('shutdown -r -t 1800')
                time.sleep(1800)
                break

    # Access to the account
    def get_account(self):
        if self.hostname == 'v-PC':
            sql = 'SELECT * FROM account WHERE id=5420'
            result = self.conn.op_select_one(sql)
            self.get_account_info(result)
        else:
            sql = 'SELECT * from virtual_machine_info where v_name=%s'
            machine_info = self.conn.op_select_one(sql, self.hostname[:2])
            if machine_info:
                self.host_ip = machine_info['host_ip']
                sql = "SELECT * FROM account WHERE action_computer=%s AND action_time<%s AND state=1 AND login_times<4 ORDER BY action_time ASC LIMIT 1"
                result = self.conn.op_select_one(sql, (self.hostname, self.current_time))

                if result:
                    self.get_account_info(result)
                else:
                    sql = "SELECT * FROM account WHERE action_computer='-' AND action_time<%s AND state=1 AND login_times<4 ORDER BY action_time ASC limit 1"
                    result = self.conn.op_select_one(sql, self.current_time)

                    if result:
                        self.get_account_info(result)

                        sql = "UPDATE account SET action_computer=%s WHERE id=%s"
                        self.conn.op_commit(sql, (self.hostname, self.account_id))
                        write_txt_time()
                    else:
                        print('Not Data!')

    def get_account_info(self, result):
        self.proxy_type = result['proxy_type']
        self.account_id = result["id"]
        self.email = result["email"]
        self.pwd = result["pw"]
        self.port = result['port']
        self.upload_web = result['upload_web']
        self.cookies = result['cookies']
        self.created_boards = result['created_boards']
        self.config_id = result['setting_num']
        self.agent = result['agent']

        sql = 'SELECT ip FROM port_info WHERE port=%s'
        port_res = self.conn.op_select_one(sql, self.port)
        if port_res:
            self.proxy_ip = port_res['ip']
            sql = 'SELECT * FROM proxy_account_info WHERE id=2'
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

        print("Start account processing..." + '\n' + "ID:",
              self.account_id, "Email:", self.email)

    # 浏览器初始化配置
    def re_driver(self):
        execute_path = os.path.abspath('.')
        webdriver_path = os.path.join(execute_path, 'boot', 'chromedriver.exe')
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
            sqlite_conn = sqlite3.connect(cookies)
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
        # options.add_argument('user-data-dir=%s' % user_data_path)
        options.add_argument('user-agent=%s' % self.agent)
        options.add_argument(
            "--proxy-server=http://%s:%d" % ('127.0.0.1', self.port))

        self.driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        # print(driver.execute_script("return navigator.userAgent;")) # UA设置是否成功
        # 躲避网站检测webdriver, 此方法暂时弃用, 因为这会导致不一致
        # self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #   "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #       get: () => undefined
        #     })
        #   """
        # })
        self.driver.maximize_window()

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
            print('Too many account errors today to suspend operations!')
            self.logs.error('The maximum error limit of %d accounts has been exceeded!' % max_error_num, exc_info=True)
            os.system('shutdown -r -t 1800')
            time.sleep(9999)

    def get_config(self):
        print('Run configuration:', self.config_id)
        sql = 'SELECT * FROM configuration WHERE id=%s'
        result = self.conn.op_select_one(sql, self.config_id)
        if result:
            self.random_browsing_control = result['random_browsing_control']
            self.browsing_pic_min = result['bro_pic_min']
            self.browsing_pic_max = result['bro_pic_max']
            self.save_home_url_control = result['save_home_page']
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