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
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

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
    clan_id          BIGINT       NOT NULL,     -- 11位的非连续数字
    -- 关于工会活跃的信息，用于工会排行榜功能
    is_active        TINYINT      DEFAULT -1,    -- 用于标记工会的有效性，-1表示新增，0表示无效，1表示有效
    season           TINYINT      DEFAULT 0,    -- 当前赛季代码 1-27
    public_rating    INT          DEFAULT 0,    -- 工会评分 1199 - 3000
    league           TINYINT      DEFAULT 0,    -- 段位 0紫金 1白金 2黄金 3白银 4青铜
    division         TINYINT      DEFAULT 0,    -- 分段 1 2 3
    division_rating  INT          DEFAULT 0,    -- 分段分数，示例：白金 1段 25分
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id), -- 索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);
```

### Table 3: Clan_Cache

用于存储工会的赛季数据

```sql
CREATE TABLE clan_cache (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       NOT NULL,     -- 11位的非连续数字
    -- 工会段位数据缓存，用于实现工会排行榜
    season           TINYINT      DEFAULT 0,    -- 当前赛季代码 1-27
    team_data_1      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的a队数据，具体格式在下面
    team_data_2      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的b队数据，具体格式在下面
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

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
