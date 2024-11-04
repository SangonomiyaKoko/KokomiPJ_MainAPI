# Kokomi 用户数据库设计

## APP User数据

### Table 1: User_basic

```sql
CREATE TABLE app_user_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    email            VARCHAR(255) NOT NULL UNIQUE,     -- 11位的非连续数字
    password_hasd    VARCHAR(255) NOT NULL,
    -- 工会基础信息数据: tag league
    nickname         VARCHAR(10)  DEFAULT NULL,
    is_premium       TINYINT      DEFAULT 0,           -- 是否是特殊用户，0不是，1是
    expired_at       INT          DEFAULT 0,           -- 特殊用户的过期时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_tag (tag), -- 索引

    UNIQUE INDEX idx_rid_cid (region_id, clan_id) -- 索引
)
```
