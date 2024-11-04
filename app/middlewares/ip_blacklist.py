ip_blacklist = []


def check_ip_blacklist(host: str) -> bool:
    "检查请求ip是否在黑名单"
    if host in ip_blacklist:
        return True
    else:
        return False