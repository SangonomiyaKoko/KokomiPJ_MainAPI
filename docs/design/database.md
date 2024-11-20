# 数据库相关设计

```python
函数格式

@ExceptionLogger.handle_database_exception_async # 用于捕获数据库相关异常
async def get_something(params: Any) -> ResponseDict:
    '''这里写函数的注释

    这里写函数的处理逻辑

    参数:
        - params：参数说明

    返回:
        - ResponseDict: 返回值格式
    '''

    # 从数据库连接池中获取连接和游标
    conn: Connection = await MysqlConnection.get_connection()
    cur: Cursor = await conn.cursor()
    try:
        # 返回的数据list或者dict
        data = [] / {}
        # 执行sql语句
        await cur.execute(
            "SELECT * FROM table;",
            [params]
        )
        # 获取数据
        rows = await cur.fetchall() / fetchone()
        for row in rows:
            # 对获取到的数据进行处理
            data.append(user)
        # 返回数据
        return JSONResponse.get_success_response(data)
    except Exception as e:
        # 数据库回滚
        await conn.rollback()
        # 抛出异常
        raise e
    finally:
        # 释放资源，关闭游标和将连接返还给连接池
        await cur.close()
        await MysqlConnection.release_connection(conn)
```
