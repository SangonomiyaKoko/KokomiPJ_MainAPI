# Kokomi 用户数据库设计

## Recent 数据

### Table 1: Recent

用于存储启用 recent 功能的用户，用于遍历更新 recent 数据库

```sql
CREATE TABLE recent (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    recent_class     INT          DEFAULT 30,     -- 最多保留多少天的数据
    last_query_at    TIMESTAMP    DEFAULT NULL,   -- 该功能上次查询的时间
    last_update_at   TIMESTAMP    DEFAULT NULL,   -- 数据库上次更新时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id), -- 主键

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);
```
