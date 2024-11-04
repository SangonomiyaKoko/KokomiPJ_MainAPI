# Redis 设计

## 数据库划分

1. db0 -> 负责业务上数据的缓存
2. db1 -> celery 的消息代理
3. db2 -> celery

### db0

#### Func1: 请求限流

key: rate_limit:{host}:{current_time}

通过固定窗口的方式，实现 ip 请求限流

#### Func2: 每日请求统计

key: api_calls:daily:{current_date}

统计每天的总体请求量和请求返回 ok 和 error 的数量

#### Func3: 过去 24h 请求量统计

key: api_calls:hourly:{current_hour}

通过过去 24h 每个小时的请求量
