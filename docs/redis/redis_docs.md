# Redis设计

## 数据库划分

1. db0 -> 负责业务上数据的缓存
2. db1 -> celery的消息代理
3. db2 -> celery

### db0

#### Func1: 请求限流

key: rate_limit:{host}:{current_time}

通过固定窗口的方式，实现ip请求限流
