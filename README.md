# Kokomi API

## 项目依赖

1. **`fastapi`**

   - **用途**：FastAPI 是一个现代、高性能的 Web 框架，用于快速构建 API，特别适用于构建高性能的 RESTful API 服务。
   - **特点**：
     - 基于 Python 类型提示，自动生成 API 文档。
     - 内置支持异步操作，适合处理高并发请求。
     - 基于 Starlette（用于 Web 服务器）和 Pydantic（用于数据验证）构建，提供强大的数据验证、序列化功能。

2. **`uvicorn`**

   - **用途**：Uvicorn 是一个轻量级、高性能的 ASGI 服务器，用于运行 FastAPI 应用。
   - **特点**：
     - 完全支持异步框架，能够处理 WebSocket 等协议。
     - 高性能，基于 `uvloop` 和 `httptools` 构建，能够承载高并发负载。
     - 提供热重载和调试模式，适用于开发和生产环境。

3. **`aiomysql`**

   - **用途**：`aiomysql` 是一个异步 MySQL 客户端，允许与 MySQL 数据库进行异步操作。
   - **特点**：
     - 提供异步查询接口，能在 FastAPI 中实现高效的数据库操作。
     - 基于 `asyncio` 构建，与 Python 的异步机制兼容。
     - 支持事务和连接池等高级功能，适用于高并发的数据库操作。

4. **`celery`**

   - **用途**：Celery 是一个强大的异步任务队列框架，用于处理异步任务和分布式任务队列。
   - **特点**：
     - 支持任务调度、延迟任务和周期性任务。
     - 支持分布式环境，可以在多台机器上运行并行任务。
     - 可以与多种消息代理（如 Redis、RabbitMQ）集成，适用于任务队列和消息传递。

5. **`flower`**

   - **用途**：Flower 是一个实时监控 Celery 任务的工具，提供 Web 界面来查看任务状态、队列、工作进程等信息。
   - **特点**：
     - 实时显示任务的执行状态、执行时间和结果。
     - 支持任务重试、撤销等操作。
     - 提供用户认证功能，支持远程监控。

6. **`eventlet`**

   - **用途**：Eventlet 是一个支持并发编程的 Python 库，主要用于为 Celery 提供协程支持。
   - **特点**：
     - 通过协程实现高并发，能够有效处理大量 I/O 密集型操作。
     - 在 Celery 中作为协程池使用，提升任务的并发处理能力。
     - 支持绿色线程，能显著提高 I/O 操作的性能。

7. **`redis`**

   - **用途**：Redis 是一个开源的内存数据结构存储，广泛用于缓存、会话管理和任务队列等场景。
   - **特点**：
     - 作为 Celery 的消息代理，负责任务队列的存储与分发。
     - 作为缓存层，提供高效的内存存储，降低数据库负载。

8. **`colorlog`**

   - **用途**：`colorlog` 是一个格式化日志的 Python 库，用于为日志添加颜色，使日志输出更具可读性。
   - **特点**：
     - 提供多种日志格式，支持根据日志级别为日志文本添加不同颜色。
     - 可以与 Python 内置的 `logging` 模块结合使用，方便配置日志输出格式。
     - 在开发和生产环境中均能提高日志的可读性，帮助快速定位问题。

9. **`httpx`**

   - **用途**：`httpx` 是一个支持 HTTP/1.1 和 HTTP/2 的异步网络请求库。
   - **特点**：
     - 提供同步和异步 API，支持 HTTP 请求的异步发起，适合高并发环境。
     - 支持请求超时、重试机制和连接池等功能。
     - 在 FastAPI 中常用于发起外部 API 请求或进行 Web 数据抓取。

10. **`dbutils`**

    - **用途**：`dbutils` 是一个用于 Celery 的数据库同步任务工具，简化了数据库任务的执行和管理。
    - **特点**：
      - 提供与数据库的同步接口，支持连接池、事务等功能。
      - 用于在 Celery 任务中执行数据库操作，简化数据库与任务调度的集成。
      - 支持不同类型的数据库操作，如增、删、改、查等，提升任务执行效率。

11. **`brotli`**

    - **用途**：`brotli` 是一种数据压缩算法，用于提高数据传输效率。
    - **特点**：
      - 压缩率高，适用于 Web 服务和 HTTP 请求的压缩。
      - 在 HTTP 响应中使用 Brotli 压缩可以显著减小传输数据量，提高带宽利用率。
      - 适合用于静态资源的压缩，尤其是在需要快速响应的 API 中。

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

activate
# 或者
.venv/Scripts/activate
# 或者
source venv/bin/activate
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
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

浏览器打开 localhost:8080/docs 可以看到自动生成的接口文档页面

#### 五. 启动 Celery

> Linux环境可能需要 `sudo apt install celery`

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
