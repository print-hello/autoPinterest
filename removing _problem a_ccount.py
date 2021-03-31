import configparser
from DBPools import OPMysql


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
conn = OPMysql(MYSQLINFO)


sql = 'SELECT * from account where state=5 and setting_num=6'
ccc = conn.op_select_all(sql)
for i in ccc:
	account_id = i['id']
	upload_web = i['upload_web']
	print(account_id, upload_web)

	sql = 'UPDATE account SET state=99, upload_web="-", upload_done=0, setting_num=1 WHERE id=%s'
	conn.op_commit(sql, account_id)

	sql = 'UPDATE upload_url set status=0 where url=%s'
	conn.op_commit(sql, upload_web)