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


def allocation():
	sql = 'SELECT * from upload_url where status=0'
	all_domains = conn.op_select_all(sql)
	if all_domains:
		for i in all_domains:
			domain = i['url']
			# domain = 'original'
			print(domain)
			sql = 'UPDATE account set upload_web=%s, upload_done=1, setting_num=6 where state=1 and upload_done=0 and upload_web="-" order by rand() limit 1'
			conn.op_commit(sql, domain)

			sql = 'UPDATE upload_url set status=1 where url=%s'
			conn.op_commit(sql, domain)


if __name__ == '__main__':
	allocation()