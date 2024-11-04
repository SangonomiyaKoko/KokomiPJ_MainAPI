# Recent功能逻辑

## 功能原理

对于某个用户，如果启用了recent功能，则服务器会记录每天的数据，计算今日数据和昨日数据的差值就能获取到近期数据

其中，某一天的数据是按每天凌晨2点到第二天的凌晨2点来算（理想来说）

之所以是理想是因为不可能每个用户都能在2点这个时间段更新数据，可能会在0-2点区间内更新

之所以是凌晨2点是因为考虑到玩家的游戏习惯，喜欢将晚上玩的算入昨天的数据，尤其是玩的比较晚的玩家

> 对于不同的服务器的用户，储存时间是按服务器当地时间来统计，不同服务器所在的时区如下

注：不考虑冬夏令时的印象

- APAC: UTC+8
- EU: UTC+1
- NA: UTC-7
- RU: UTC+3
- CN: UTC+9

## 服务架构

服务器采用主+从的方式，用于缓解单一服务器对于大量用户的数据更新请求会出现更新时间较慢或者压力较大

子服务器通过从主服务器获取需要更新的用户，通过遍历用户的数据，更新主服务的user_info表，其中主服务器的更新进程发现user_info的表数据发生变动，更新时间大于recent的更新时间，则确定是有更新数据

![图片]

## 主要组件

主服务器：recent.db用于储存所有的用户

主服务器：user_info.db获取用户活跃数据

子服务器：每次从主服务读取1w个用户，更新数据

recent数据库：存储个人的recent数据

## 具体逻辑

### 子服务器更新逻辑

1.从主服务器的recent.db获取用户数据，获取某个服务器的用户数据

```sql
SELECT 
    recent.account_id,
    recent.region_id,
    recent.update_time,
    user.active_level,
    user.is_public,
    user.total_battles,
    user.last_battle_time
FROM 
    recent recent
INNER JOIN 
    user_info user
ON 
    user.account_id = recent.account_id
WHERE
    recent.region_id = %s
```

2.遍历这1w个用户，检查update_time和active_level，判断是否需要更新

> 其中服务器当地时间的22-2点为特殊时段，这个时间段内由于跨日需要新的文件

#### 非特殊时间段Active_Level对应的recent更新频率

| active_level | recent_update_time |
| ------------ | ------------------ |
| 0            | 8h                 |
| 1            | 8h                 |
| 2            | 1h                 |
| 3            | 2h                 |
| 4            | 4h                 |
| 5            | 4h                 |
| 6            | 4h                 |
| 7            | 6h                 |
| 8            | 6h                 |
| 9            | 8h                 |

#### 特殊时间段Active_Level对应的recent更新频率

| active_level | recent_update_time |
| ------------ | ------------------ |
| 0            | 2h                 |
| 1            | 2h                 |
| 2            | 20m                |
| 3            | 30m                |
| 4            | 40m                |
| 5            | 1h                 |
| 6            | 2h                 |
| 7            | 3h                 |
| 8            | 3h                 |
| 9            | 4h                 |

3.将数据更新到主服务的user_info.db表中

### 主服务器架构

基本功能同子服务器，是子服务器的容灾备份，防止子服务器出现宕机导致数据更新失败

在子服务器的基础上，加上数据更新写入的功能，发现user_info的更新时间大于recent，则触发recent数据的更新，写入recent的sqlite3的数据库

同时需要负责跨日更新时的数据复制功能，检查recent的上次更新时间，如果更新的日期-2h和当前的日期不同的话则将昨日的数据复制一份到当前的数据库，作为今天数据的初始数据
