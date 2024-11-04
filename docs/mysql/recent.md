# Kokomi 用户数据库设计

## Recent数据

### Table 1: Recent

用于存储启用recent功能的用户，用于遍历更新recent数据库

```sql
CREATE TABLE recent (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    class            INT          DEFAULT 30,     -- 最多保留多少天的数据
    query_time       INT          DEFAULT 0,      -- 该功能上次查询的时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id) -- 主键
);
```
