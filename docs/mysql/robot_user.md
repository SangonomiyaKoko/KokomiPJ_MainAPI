# Kokomi 用户数据库设计

## Bot User绑定数据

```sql
CREATE TABLE bot_user_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    platform         VARCHAR(10)  NOT NULL,     -- 平台
    user_id          VARCHAR(50)  NOT NULL,     -- 用户id
    -- 绑定信息
    region_id        TINYINT      NOT NULL,     -- 服务器id
    account_id       INT          NOT NULL,     -- 用户ID
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_pid (platform, user_id) -- 索引
);
```
