CREATE TABLE region (
    region_id      TINYINT        NOT NULL,
    region_str     VARCHAR(5)     NOT NULL,

    PRIMARY KEY (region_id)
);

INSERT INTO region 
    (region_id, region_str) 
VALUES
    (1, "asia"), (2, "eu"), (3, "na"), (4, "ru"), (5, "cn");

CREATE TABLE user_basic (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL UNIQUE,    -- 1-11位的非连续数字
    region_id        TINYINT      NOT NULL,
    -- 用户基础信息数据: name
    username         VARCHAR(25)  NOT NULL,    -- 最大25个字符，编码：utf-8
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_username (username), -- 索引

    UNIQUE INDEX idx_rid_aid (region_id, account_id), -- 索引

    FOREIGN KEY (region_id) REFERENCES region(region_id) ON DELETE CASCADE -- 外键
);

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

    UNIQUE INDEX idx_rid_cid (region_id, clan_id), -- 索引

    FOREIGN KEY (region_id) REFERENCES region(region_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE user_info (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,     -- 1-11位的非连续数字
    -- 关于用户活跃的信息，用于recent/recents/用户排行榜功能
    is_active        TINYINT      DEFAULT 0,    -- 用于标记用户的有效性，0表示无效，1表示有效
    active_level     TINYINT      DEFAULT 0,    -- 人为设置的用户活跃的等级
    is_public        TINYINT      DEFAULT 0,    -- 用户是否隐藏战绩，0表示隐藏，1表示公开
    total_battles    INT          DEFAULT 0,    -- 用户总场次
    last_battle_at   TIMESTAMP    DEFAULT NULL, -- 用户最后战斗时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE user_clan (
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,       -- 1-10位的非连续数字
    clan_id          BIGINT       DEFAULT NULL,   -- 10位的非连续数字 none表示无工会
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 唯一索引

    INDEX idx_cid (clan_id), -- 非唯一索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE, -- 外键
    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE user_history (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,    -- 1-11位的非连续数字
    -- 用户历史名称的记录
    username         VARCHAR(25)  NOT NULL,     -- 最大25个字符，编码：utf-8
    start_time       TIMESTAMP    NOT NULL,     -- 使用该名称的开始时间
    end_time         TIMESTAMP    NOT NULL,     -- 使用该名称的结束时间
    -- 记录数据创建的时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    INDEX idx_aid (account_id), -- 索引

    INDEX idx_username (username), -- 索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE user_ships (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    account_id       BIGINT       NOT NULL,     -- 1-11位的非连续数字
    -- 记录用户缓存的数据和更新时间
    battles_count    INT          DEFAULT NULL, -- 总战斗场次
    hash_value       CHAR(64)     DEFAULT NULL, -- 缓存数据的哈希值
    ships_data       BLOB         DEFAULT NULL, -- 压缩处理后的缓存数据
    -- 记录数据创建的时间和更新时间略
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_aid (account_id), -- 索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);

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
    last_battle_at   TIMESTAMP    DEFAULT NULL, -- 上次战斗结束时间，用于判断是否有更新数据
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id), -- 索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);

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

    UNIQUE INDEX idx_cid (clan_id), -- 非唯一索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);

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

    UNIQUE INDEX idx_cid (clan_id), -- 唯一索引

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE, -- 外键

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE clan_season (
    -- 相关id
    id               INT          AUTO_INCREMENT,
    clan_id          BIGINT       NOT NULL,     -- 11位的非连续数字
    -- 工会段位数据缓存，用于实现工会排行榜
    season           TINYINT      DEFAULT 0,    -- 当前赛季代码 1-27
    last_battle_at   TIMESTAMP    DEFAULT NULL, -- 上次战斗结束时间，用于判断是否有更新数据
    team_data_1      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的a队数据
    team_data_2      VARCHAR(255) DEFAULT NULL, -- 存储当前赛季的b队数据
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id), -- 主键

    UNIQUE INDEX idx_cid (clan_id), -- 索引

    FOREIGN KEY (clan_id) REFERENCES clan_basic(clan_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE recent (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    recent_class     INT          DEFAULT 30,     -- 最多保留多少天的数据
    last_query_at    TIMESTAMP    DEFAULT NULL,   -- 该功能上次查询的时间
    last_update_at   TIMESTAMP    DEFAULT NULL,   -- 数据库上次更新时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id), -- 主键

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);

CREATE TABLE recents (
    -- 相关id
    account_id       BIGINT       NOT NULL,
    region_id        TINYINT      NOT NULL,
    -- 用户配置
    proxy            TINYINT      DEFAULT 0,      -- 表示Recents代理服务器地址
    recents_class    TINYINT      DEFAULT 0,      -- 表示是否为特殊用户
    last_query_at    TIMESTAMP    DEFAULT 0,      -- 该功能上次查询的时间
    last_update_at   TIMESTAMP    DEFAULT 0,      -- 数据库上次更新时间
    -- 记录数据创建的时间和更新时间
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (region_id, account_id), -- 主键

    FOREIGN KEY (account_id) REFERENCES user_basic(account_id) ON DELETE CASCADE -- 外键
);