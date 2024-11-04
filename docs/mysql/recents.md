# Kokomi 用户数据库设计

## Recents数据

### Table 1: Recents

用于存储启用recents功能的用户，用于遍历更新recents数据库

```sql
CREATE TABLE recents (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    class            TINYINT      DEFAULT 0,      -- 表示是否为特殊用户
    proxy            TINYINT      DEFAULT 0,      -- 表示Recents代理服务器地址
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id) -- 主键
);
```
