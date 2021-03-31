import json
import requests


def generate_configuration(conn, host_ip, port, proxy_ip, zone, customer, customer_pwd):
    delete_port(port, host_ip)
    lpm_conf = {}
    lpm_conf["proxy"] = {}
    # lpm_conf["proxy"]["proxy_type"] = "persist"
    lpm_conf["proxy"]["multiply"] = 0
    lpm_conf["proxy"]["multiply_users"] = False
    lpm_conf["proxy"]["ssl"] = False
    lpm_conf["proxy"]["secure_proxy"] = True
    lpm_conf["proxy"]["keep_alive"] = True
    lpm_conf["proxy"]["proxy"] = "zproxy.lum-superproxy.io"
    lpm_conf["proxy"]["proxy_port"] = 22225
    lpm_conf["proxy"]["proxy_connection_type"] = "https"
    lpm_conf["proxy"]["proxy_retry"] = 2
    lpm_conf["proxy"]["insecure"] = False
    lpm_conf["proxy"]["session"] = True
    lpm_conf["proxy"]["sticky_ip"] = False
    lpm_conf["proxy"]["pool_size"] = 1
    lpm_conf["proxy"]["rotate_session"] = False
    lpm_conf["proxy"]["throttle"] = 0
    lpm_conf["proxy"]["route_err"] = "pass_dyn"
    lpm_conf["proxy"]["override_headers"] = True
    lpm_conf["proxy"]["debug"] = "full"
    lpm_conf["proxy"]["port"] = port
    lpm_conf["proxy"]["ip"] = proxy_ip
    lpm_conf["proxy"]["customer"] = customer
    lpm_conf["proxy"]["password"] = customer_pwd
    lpm_conf["proxy"]["zone"] = zone
    # 成功状态码：200
    r_post_conf = requests.post("http://%s:22999/api/proxies" % host_ip, json=lpm_conf)
    # print(r_post_conf.status_code)

    return r_post_conf.status_code


def delete_port(port, host_ip):
    # 成功状态码：204
    try:
        r_del_port = requests.delete('http://%s:22999/api/proxies/%s' % (host_ip, str(port)))
        # print(r_del_port.status_code)
    except:
        pass