# Kokomi 用户数据库设计

## User 数据

### Table 1: User_Basic

用于存储用户的基础信息

```sql
CREATE TABLE user_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL UNIQUE,    -- 1-11位的非连续数字
    region_id        TINYINT      NOT NULL,
    -- 用户基础信息数据: name
    username         VARCHAR(25)  NOT NULL,    -- 最大25个字符，编码：utf-8
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_username (username), -- 索引

    UNIQUE INDEX idx_rid_aid (region_id, account_id) -- 索引
)
```

### Table 2: User_Info

用于存储用户的基本信息

```sql
CREATE TABLE user_info (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,     -- 1-11位的非连续数字
    -- 关于用户活跃的信息，用于recent/recents/用户排行榜功能
    is_active        TINYINT      DEFAULT -1,   -- 用于标记用户的有效性，-1表示新增，0表示无效，1表示有效
    active_level     TINYINT      DEFAULT 0,    -- 人为设置的用户活跃的等级
    is_public        TINYINT      DEFAULT 0,    -- 用户是否隐藏战绩，0表示隐藏，1表示公开
    total_battles    INT          DEFAULT 0,    -- 用户总场次
    last_battle_time INT          DEFAULT 0,    -- 用户最后战斗时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);
```

#### 活跃数据对应的 Active_Level

| is_plblic | total_battles | last_battle_time | active_level | decs     |
| --------- | ------------- | ---------------- | ------------ | -------- |
| 0         | -             | -                | 0            | 隐藏战绩 |
| 1         | 0             | 0                | 1            | 无数据   |
| 1         | -             | [0, 1d]          | 2            | 活跃     |
| 1         | -             | [1d, 3d]         | 3            | -        |
| 1         | -             | [3d, 7d]         | 4            | -        |
| 1         | -             | [7d, 1m]         | 5            | -        |
| 1         | -             | [1m, 3m]         | 6            | -        |
| 1         | -             | [3m, 6m]         | 7            | -        |
| 1         | -             | [6m, 1y]         | 8            | -        |
| 1         | -             | [1y, + ]         | 9            | 不活跃   |

### Table 3: User_Cache

用于用户缓存相关的数据

```sql
CREATE TABLE user_cache (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,     -- 1-11位的非连续数字
    -- 记录用户缓存的数据和更新时间
    cache_data       INT          DEFAULT -1,   -- 数据条目的数量,-1表示新增用户
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);
```

#### Active_Level 对应的 Cache 更新频率

| active_level | cache_update_time |
| ------------ | ----------------- |
| 0            | 10d               |
| 1            | 20d               |
| 2            | 1d                |
| 3            | 3d                |
| 4            | 5d                |
| 5            | 7d                |
| 6            | 10d               |
| 7            | 14d               |
| 8            | 20d               |
| 9            | 25d               |

### Table 4：Cache

用于记录用户中所有的 ship_id 的数据

如果需要计算服务器数据就只用遍历数据库将所有数据相加

如果需要计算船只排行榜只用筛选出有效数据计算排行榜

```sql
CREATE TABLE user_details (
    -- 用户基本信息
    ship_id          BIGINT       NOT NULL,
    account_id       BIGINT       NOT NULL,
    -- 具体数据
    battles_count    INT          NULL,
    wins             INT          NULL,
    damage_dealt     BIGINT       NULL,
    frags            INT          NULL,
    exp              BIGINT       NULL,
    survived         INT          NULL,
    scouting_damage  BIGINT       NULL,
    art_agro         BIGINT       NULL,
    planes_killed    INT          NULL,
    -- Record
    max_exp          INT          NULL,
    max_damage_dealt INT          NULL,
    max_frags        INT          NULL,
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (ship_id, account_id), -- 主键

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);
```
