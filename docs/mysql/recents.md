# Kokomi 用户数据库设计

## Recents 数据

### Table 1: Recents

用于存储启用 recents 功能的用户，用于遍历更新 recents 数据库

```sql
CREATE TABLE recents (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    proxy            TINYINT      DEFAULT 0,      -- 表示Recents代理服务器地址
    recents_class    TINYINT      DEFAULT 0,      -- 表示是否为特殊用户
    last_query_time  INT          DEFAULT 0,      -- 该功能上次查询的时间
    last_update_time INT          DEFAULT 0,      -- 数据库上次更新时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id) -- 主键
);
```
