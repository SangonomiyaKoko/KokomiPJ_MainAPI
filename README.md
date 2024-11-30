# Kokomi API

## 项目依赖

1. `fastapi`

   - 高性能的 Web 框架，用于构建 API，基于 Starlette 和 Pydantic

2. `uvicorn`

   - 轻量级、高性能的 ASGI 服务器，用于运行 FastAPI 应用

3. `aiomysql`

   - 异步 MySQL 客户端，支持与 MySQL 数据库的异步操作

4. `celery`

   - 异步任务队列，用于处理异步任务和分布式任务队列

5. `flower`

   - Celery 监控工具，通过 Web 界面实时监控 Celery 中的任务、队列、工作进程等信息。

6. `eventlet`

   - 支持并发编程的库，为 Celery 提供协程支持，实现更高的并发能力。

7. `redis`

   - 开源的内存数据结构存储，用于缓存、会话管理、任务队列等功能，与 Celery 一起用作消息代理。

8. `colorlog`

   - 格式化日志

9. `httpx`

   - 负责接口的网络请求

10. `dbutils`

    - 负责 Celery 的数据库同步任务

11. `brotli`
    - 数据压缩方法

dbutils

## 项目结构

```txt
kokomi_api_project/
├── app/
│   ├── __init__.py
│   ├── main.py        # 入口文件
│   ├── dependencies.py# 依赖
│   ├── apis/          # 不同平台的接口
│   │   ├── platfrom/      # 平台相关接口
│   │   ├── robot/         # 社交平台bot相关接口
│   │   ├── software/      # 桌面端应用相关
│   │   └── ...
│   ├── const/         # 用于常用的常量
│   │   ├── __init__.py
│   │   ├── game.py        # 游戏相关常量
│   │   ├── color.py       # 颜色相关常量
│   │   └── ...
│   ├── core/          # 核心文件
│   │   ├── __init__.py
│   │   ├── config.py      # 配置文件
│   │   ├── logger.py      # 日志配置
│   │   ├── secruity.py    # 接口安全相关
│   │   └── ...            # 其他核心功能
│   ├── db/            # 数据库相关配置
│   │   ├── __init__.py
│   │   ├── mysql.py       # MySQL数据库
│   │   ├── sqlite.py      # SQLite3数据库
│   │   └── ...
│   ├── json/          # json数据
│   │   └── ...
│   ├── log/           # log日志
│   │   ├── __init__.py
│   │   └── ...
│   ├── middleware/    # 中间件
│   │   ├── __init__.py
│   │   ├── celery.py      # celery配置
│   │   ├── redis.py       # redis配置
│   │   ├── rate_limiter.py#请求限流
│   │   └── ...
│   ├── models/        # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py        # user模型
│   │   ├── clan.py        # clan模型
│   │   └── ...
│   ├── network/       # 负责网络交互
│   │   ├── __init__.py
│   │   ├── api_base.py    # 基类
│   │   ├── api_basic.py   # 基础数据接口
│   │   ├── api_details.py # 详细数据接口
│   │   └── ...
│   ├── response/      # 返回值
│   │   ├── __init__.py
│   │   ├── response.py    # 接口返回值
│   │   └── ...
│   ├── routers/       # 路由配置
│   │   ├── __init__.py
│   │   └── ...
│   └── utils/         # 工具函数
│       ├── __init__.py
│       ├── utils.py
│       └── ...
├── docs/              # 技术文档
│   └── ...
├── migrations/        # 数据库迁移脚本
│   └── ...
├── tools/             # 其他工具
│   ├── clan               # 工会缓存更新
│   ├── user               # 用户缓存更新
│   ├── proxy              # 代理
│   ├── recent             # recent功能
│   ├── recents            # recents功能
│   └── ...
├── tests/             # 测试模块
│   └── ...
├── temp/              # 临时文件，存放测试日志和测试数据库
│   └── ...
├── .env                    # 环境变量文件
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明文件
```

## 启动步骤

### MySQL 配置

> 如果已有搭建好的 MySQL 数据库可直接跳过本篇

此处只介绍 Linux 环境下的配置方法，Windows 环境过于简单就不做介绍

以 `Ubuntu-24.04` 安装 `MySQL-8.0` 为例

#### 一. 安装 MySQL

```bash
sudo apt install mysql-server # 下载MySQL

mysql --version # 查看版本

sudo systemctl status mysql # 查看运行状态
```

### 二. 设置 root 密码(可选)

```bash
sudo mysql -u root # 使用root无密码登录
```

```sql
alter user 'root'@'localhost' identified with mysql_native_password by '123456'; -- 为root添加密码

exit; -- 退出mysql的命令行模式
```

### 三. 允许 root 远程登录(可选)

```bash
mysql -u root -p #使用root有密码登录
```

```sql
use mysql; -- 使用mysql数据库

update user set host='%' where user='root'; -- 允许root远程登录

flush privileges; -- 权限刷新

exit; -- 退出mysql的命令行模式
```

### 四. 允许其他 ip 远程登录(可选)

打开以下路径的文件: **/etc/mysql/mysql.conf.d/mysqld.cnf**

将文件内 `bind-address` 后的值修改为 `0.0.0.0` 即可允许其他 ip 登录 mysql

```bash
sudo systemctl restart mysql # 修改后需要重启
```

### 安装 Redis

> 如果已有搭建好的 Redis 数据库可直接跳过本篇

此处只介绍 Linux 环境下的配置方法，Windows 环境过于简单就不做介绍

以 `Ubuntu-24.04` 安装 `Redis-7.0` 为例

#### 一. 安装 Redis

```bash
sudo apt install redis # 下载Redis

sudo systemctl status redis-server  # 查看运行状态
```

#### 二. 配置 Redis 密码

打开以下路径内的文件: **/etc/redis/redis.conf**

点击 `Ctrl`+`F` 搜索 `requirepass` 找到以下行

> 在大概 1036 行附近，不推荐使用 vim 编辑

```txt
# requirepass foobared
```

去掉行前面的#并将 foobared 替换为你想要设置的密码

#### 三. 允许其他 ip 远程登录(可选)

打开以下路径内的文件: **/etc/redis/redis.conf**

点击 `Ctrl`+`F` 搜索 `bind` 找到以下行

> 在大概 70 行附近，应该不用搜索都能一眼看到

```txt
bind 127.0.0.1 ::1
```

将后面的值修改为 `* -::*`

```txt
# 或者根据自己的需求更改, 示例:
#
# bind 192.168.1.100 10.0.0.1     # listens on two specific IPv4 addresses
# bind 127.0.0.1 ::1              # listens on loopback IPv4 and IPv6
# bind * -::*                     # like the default, all available interfaces
```

### KokomiAPI 安装步骤

#### 一. 从 Github 下载最新的代码

```bash
git clone https://github.com/SangonomiyaKoko/KokomiPJ_API.git
```

> 没有 git 先安装 git

#### 二. 创建并激活虚拟环境

推荐的 Python 版本: `3.8.0`及以上

```bash
python -m venv venv

.venv/Scripts/activate
```

#### 三. 安装依赖

```bash
pip install -r requirements.txt # 安装python依赖
```

#### 四. 数据库配置

创建 `kokomi` 和 `ships` 数据库

执行 **migrations\create_db.sql** 文件创建数据表

#### 五. 配置.env 文件

创建 `.env` 文件, 并写入以下内容，根据自己的配置修改

```ini
# API configuration
API_HOST='127.0.0.1'
API_PORT=8080

# Mysql configuration
MYSQL_HOST='127.0.0.1'
MYSQL_PORT=3306
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = '123456'

# SQLite DB file pathw
SQLITE_PATH='F:\Kokomi_PJ_Api\temp\db'

# Redis configuration
REDIS_HOST='127.0.0.1'
REDIS_PORT=6379
REDIS_PASSWORD='123456'

# Proxy
USE_PROXY=0
```

#### 四. 启动 FastAPI

```bash
uvicorn app.main:app --log-level debug
```

浏览器打开 localhost:8080/docs 可以看到自动生成的接口文档页面

#### 五. 启动 Celery

```bash
celery --app app.middlewares.celery:celery_app worker -P eventlet --loglevel=debug
```

#### 六. 启动 Flower

```bash
celery --app app.middlewares.celery:celery_app flower --port=5555
```

浏览器打开 localhost:5555 可以看到 Flower 页面

#### 七. 更新代码

```bash
git pull origin main
```
