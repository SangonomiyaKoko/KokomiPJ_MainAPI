# Kokomi API

## 项目依赖

1. `fastapi`

   - 高性能的 Web 框架，用于构建 API，基于 Starlette 和 Pydantic

2. `uvicorn`

   - 轻量级、高性能的 ASGI 服务器，用于运行 FastAPI 应用

3. `aioredis`

   - 异步 Redis 客户端，支持与 Redis 数据库的异步交互

4. `aiomysql`

   - 异步 MySQL 客户端，支持与 MySQL 数据库的异步操作

5. `celery`

   - 异步任务队列，用于处理异步任务和分布式任务队列

6. `flower`

   - Celery 监控工具，通过 Web 界面实时监控 Celery 中的任务、队列、工作进程等信息。

7. `eventlet`

   - 支持并发编程的库，为 Celery 提供协程支持，实现更高的并发能力。

8. `redis`

   - 开源的内存数据结构存储，用于缓存、会话管理、任务队列等功能，与 Celery 一起用作消息代理。

9. `colorlog`

   - 格式化日志

10. `httpx`

    - 负责接口的网络请求

11. `dbutils`

    - 负责 Celery 的数据库同步任务

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

> 关于怎么配置虚拟环境这里就不展开

一. 进入虚拟环境

```bash
.venv/Scripts/activate
```

或者

```bash
activate
```

二. 启动 FastAPI

```bash
uvicorn app.main:app --log-level debug
```

浏览器打开 localhost:8080/docs 可以看到自动生成的接口文档页面

三. 启动 Celery

```bash
celery --app app.middlewares.celery:celery_app worker -P eventlet --loglevel=debug
```

四. 启动 Flower

```bash
celery --app app.middlewares.celery:celery_app flower --port=5555
```

浏览器打开 localhost:5555 可以看到 Flower 页面
