from DBPools import OPMysql


MYSQLINFO = {
    "host": 'localhost',
    "user": 'pinterest',
    "passwd": '******',
    "db": 'pinterest',
    "port": 3306,
    "charset": 'utf8mb4'
}
conn = OPMysql(MYSQLINFO)


def update_ip_table():
    ip_file = str(input('输入IP文件名（包含文件后缀名）：'))
    ip_list = []
    with open(ip_file, 'r', encoding='utf-8') as fp:
        while True:
            line = fp.readline()
            ip = line.split('-')[-1].split(':')[0]
            print(ip)

            if ip:
                ip_a = ip.split('.')[0]
                ip_b = ip.split('.')[1]
                ip_c = ip.split('.')[2]
                try:
                    sql = 'INSERT INTO ips (ip, a_segment, b_segment, c_segment) VALUES (%s, %s, %s, %s)'
                    conn.op_commit(sql, (ip, ip_a, ip_b, ip_c))

                except:
                    pass
            else:
                break
    print('End')

    # 读取port_info表对ip库使用过的ip进行标记
    sql = 'SELECT ip FROM port_info'
    results = conn.op_select_all(sql)
    if results:
        print('标记中...')
        for port in results:
            port_ip = port['ip']
            sql = 'SELECT ip FROM ips WHERE ip=%s'
            result = conn.op_select_one(sql, port_ip)
            if result:
                sql = 'UPDATE ips SET used=1 WHERE ip=%s'
                conn.op_commit(sql, port_ip)
            else:
                sql = 'UPDATE port_info SET state=2 WHERE ip=%s'
                conn.op_commit(sql, port_ip)

        change_error_port()


def change_error_port():
    sql = 'SELECT * FROM port_info WHERE state=2'
    results = conn.op_select_all(sql)
    if results:
        for i in results:
            port = i['port']
            port_ip = i['ip']
            change_ip(port, port_ip)   


def change_ip(port, port_ip):
    old_ip = port_ip
    old_ip_a = old_ip.split('.')[0]
    old_ip_b = old_ip.split('.')[1]
    old_ip_c = old_ip.split('.')[2]

    sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s AND b_segment=%s AND c_segment=%s ORDER BY RAND() LIMIT 1'
    get_new_ip = conn.op_select_one(
        sql, (old_ip_a, old_ip_b, old_ip_c))
    if get_new_ip:
        update_db(get_new_ip, port, old_ip)

    else:
        print('已无更多对应C段IP, 获取同B段IP！')
        sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s AND b_segment=%s ORDER BY RAND() LIMIT 1'
        get_new_ip = conn.op_select_one(sql, (old_ip_a, old_ip_b))
        if get_new_ip:
            update_db(get_new_ip, port, old_ip)

        else:
            print('已无更多对应B段IP, 获取同A段IP！')
            sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s ORDER BY RAND() LIMIT 1'
            get_new_ip = conn.op_select_one(sql, old_ip_a)
            if get_new_ip:
                update_db(get_new_ip, port, old_ip)

            else:
                print('已无更多对应A段IP, 获取随机IP！')
                sql = 'SELECT * FROM ips WHERE used=0 ORDER BY RAND() LIMIT 1'
                get_new_ip = conn.op_select_one(sql)
                if get_new_ip:
                    update_db(get_new_ip, port, old_ip)


def update_db(get_new_ip, port, old_ip):
    new_ip = get_new_ip['ip']
    sql = 'UPDATE port_info set ip=%s, state=1 where port=%s'
    conn.op_commit(sql, (new_ip, port))

    print('Old IP:', old_ip, '--->', 'New IP:', new_ip)
    sql = 'UPDATE ips SET used=1 WHERE ip=%s'
    conn.op_commit(sql, new_ip)

    try:
        sql = 'UPDATE ips SET used=2 WHERE ip=%s'
        conn.op_commit(sql, old_ip)
    except:
        pass

    try:
        sql = 'UPDATE account SET state=1, proxy_err_times=0 WHERE port=%s'
        conn.op_commit(sql, port)
    except:
        pass


def judge_module(num_str):
    print('已选择', num_str)
    ack = str(input('按y确认！'))
    if ack.lower() == 'y'.lower():
        print('正在执行', num_str)
        if num_str == '1：更新IP库':
            update_ip_table()
        elif num_str == '2：添加端口':
            pass
        elif num_str == '3：更换异常端口IP':
            change_error_port()
    else:
        print('指令错误')


if __name__ == '__main__':
    num_str_1 = '1：更新IP库'
    num_str_2 = '2：添加端口'
    num_str_3 = '3：更换异常端口IP'
    print('选择操作：')
    print('-------------------')
    print(num_str_1)
    print(num_str_2)
    print(num_str_3)
    print('-------------------')
    num = int(input('输入编号：'))
    if num == 1:
        judge_module(num_str_1)

    elif num == 2:
        judge_module(num_str_2)

    elif num == 3:
        judge_module(num_str_3)

    else:
        print('编号输入错误！')