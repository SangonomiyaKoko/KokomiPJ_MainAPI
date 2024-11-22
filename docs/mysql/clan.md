# Kokomi 用户数据库设计

## Clan 数据

### Table 1: Clan_Basic

用于存储工会的基本信息

```sql
CREATE TABLE clan_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       NOT NULL UNIQUE,     -- 11位的非连续数字
    region_id        TINYINT      NOT NULL,
    -- 工会基础信息数据: tag league
    tag              VARCHAR(5)   NOT NULL,     -- 最大5个字符，编码：utf-8
    league           TINYINT      DEFAULT 5,    -- 当前段位 0紫金 1白金 2黄金 3白银 4青铜 5无
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_tag (tag), -- 索引

    UNIQUE INDEX idx_rid_cid (region_id, clan_id) -- 索引
);
```

### Table 2: Clan_Info

用于存储工会的赛季数据

```sql
CREATE TABLE clan_info (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       NOT NULL,     -- 10位的非连续数字
    -- 关于工会活跃的信息，用于工会排行榜功能
    is_active        TINYINT      DEFAULT 0,    -- 用于标记工会的有效性，0表示无效，1表示有效
    season           TINYINT      DEFAULT 0,    -- 当前赛季代码 1-30+
    public_rating    INT          DEFAULT 1100, -- 工会评分 1199 - 3000+  1100表示无数据
    league           TINYINT      DEFAULT 4,    -- 段位 0紫金 1白金 2黄金 3白银 4青铜
    division         TINYINT      DEFAULT 2,    -- 分段 1 2 3
    division_rating  INT          DEFAULT 0,    -- 分段分数，示例：白金 1段 25分
    last_battle_at   INT          DEFAULT 0,    -- 上次战斗结束时间，用于判断是否有更新数据
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id), -- 索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);
```

### Table 3: Clan_Users

用于存储用户和工会的对应关系

```sql
CREATE TABLE clan_users (
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       DEFAULT NULL,   -- 10位的非连续数字 none表示无工会
    -- 记录工会内玩家
    hash_value       CHAR(64)     DEFAULT NULL, -- 缓存数据的哈希值
    users_data       BLOB         DEFAULT NULL, -- 压缩处理后的缓存数据
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id) -- 非唯一索引
);
```

### Table 4: Clan_History

记录工会用户的进出

```sql
CREATE TABLE clan_history (
    id               INT          AUTO_INCREMENT,
    -- 记录某个用户进入或者离开某个工会
    account_id       BIGINT       NOT NULL,       -- 1-10位的非连续数字
    clan_id          BIGINT       NOT NULL,       -- 10位的非连续数字
    action_type      TINYINT      NOT NULL,       -- 表示行为 1表示离开 2表示进入
    -- 记录数据创建的时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_aid (account_id), -- 索引

    UNIQUE INDEX idx_cid (clan_id) -- 唯一索引
);
```

### Table 5: Clan_Cache

用于存储工会的赛季数据

```sql
CREATE TABLE clan_season (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       NOT NULL,     -- 11位的非连续数字
    -- 工会段位数据缓存，用于实现工会排行榜
    season           TINYINT      DEFAULT 0,    -- 当前赛季代码 1-27
    last_battle_at   INT          DEFAULT 0,    -- 上次战斗结束时间，用于判断是否有更新数据
    team_data_1      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的a队数据
    team_data_2      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的b队数据
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id), -- 索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);
```

```python
# 工会队伍的当前赛季的详细数据
team_data_1 = {
    'battles_count': 15,
    'wins_count': 4,
    'league': 4,
    'division': 3,
    'division_rating': 14,
    'public_rating': 1014,
    'stage': None
}
team_data_2 = {
    'battles_count': 33,
    'wins_count': 21,
    'league': 3,
    'division': 1,
    'division_rating': 99,
    'public_rating': 1599,
    'stage': {
        'type': 'promotion',    # 晋级赛/保级赛
        'progress': ['victory', 'defeat']    # 结果 victory/defeat
    }
}
```

### Table 6: Clan_Battle

用于存储工会的赛季数据

```sql
CREATE TABLE clan_battle_s27 (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    -- 对局相关信息和ID
    battle_time      INT          NOT NULL,     -- 战斗时间
    clan_id          BIGINT       NOT NULL,     -- 10位的非连续数字
    region_id        TINYINT      NOT NULL,     -- 服务器id
    team_number      TINYINT      NOT NULL,     -- 队伍id
    -- 对局结果
    battle_result    VARCHAR(10)  NOT NULL,     -- 对局结果 胜利或者时报
    battle_rating    INT          DEFAULT NULL, -- 对局分数 如果是晋级赛则会显示为0
    battle_stage     VARCHAR(10)  DEFAULT NULL, -- 对局结果 仅对于stage有效
    -- 对局结算的数据
    league           TINYINT      NOT NULL,     -- 段位 0紫金 1白金 2黄金 3白银 4青铜
    division         TINYINT      NOT NULL,     -- 分段 1 2 3
    division_rating  INT          NOT NULL,     -- 分段分数，示例：白金 1段 25分
    public_rating    INT          NOT NULL,     -- 工会评分 1199 - 3000
    stage_type       VARCHAR(10)  DEFAULT NULL, -- 晋级赛/保级赛 默认为Null
    stage_progress   VARCHAR(50)  DEFAULT NULL, -- 晋级赛/保级赛的当前结果
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 因为数据不会更新，所以不需要updated_at，只需要created_at

    PRIMARY KEY (id), -- 主键

    INDEX idx_cid (battle_time) -- 索引
);
```
