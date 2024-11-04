# Kokomi 用户数据库设计

## UserClan 数据

### Table 2: User_Clan

中间表，用于存储用户和工会的对应关系

```sql
CREATE TABLE user_clan (
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,     -- 1-11位的非连续数字
    clan_id          BIGINT       DEFAULT NULL, -- 11位的非连续数字
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 唯一索引

    INDEX idx_cid (clan_id) -- 非唯一索引
);
```
