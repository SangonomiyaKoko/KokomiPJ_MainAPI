ip_whitelist = ['127.0.0.1']

    
def check_ip_whilelist(host: str) -> bool:
    "检查请求ip是否在白名单，如果在就跳过限速"
    if host in ip_whitelist:
        return True
    else:
        return False