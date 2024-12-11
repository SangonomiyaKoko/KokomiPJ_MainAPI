# Kokomi 用户数据库设计

## Bot User绑定数据

```sql
CREATE TABLE bot_user_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    platform         VARCHAR(10)  NOT NULL,     -- 11位的非连续数字
    user_id          VARCHAR(50)  NOT NULL,
    -- 工会基础信息数据: tag league
    region_id        TINYINT      NOT NULL,     -- 是否是特殊用户，0不是，1是
    account_id       INT          NOT NULL,     -- 特殊用户的过期时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_pid (platform, user_id) -- 索引
);
```
