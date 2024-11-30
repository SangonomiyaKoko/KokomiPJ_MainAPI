import uuid
import traceback

import httpx
import aiomysql
import pymysql
import sqlite3
import redis

from .error_log import write_error_info
from app.response import JSONResponse

class ExceptionType:
    program = 'program'
    mysql = 'MySQL'
    network = 'Network'
    redis = 'Redis'

class NerworkExceptionName:
    connect_timeout = 'ConnectTimeout'
    read_timeout = 'ReadTimeout'
    request_timeout = 'RequestTimeout'
    network_error = 'NetworkError'
    connect_error = 'ConnectError'
    read_error = 'ReadError'

class DatabaseExceptionName:
    programming_error = 'ProgrammingError'
    operational_error = 'OperationalError'
    integrity_error = 'IntegrityError'
    database_error = 'DatabaseError'

def generate_error_id():
    return str(uuid.uuid4())

class ExceptionLogger:
    @staticmethod
    def handle_program_exception_async(func):
        "负责异步程序异常信息的捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_program_exception_sync(func):
        "负责同步程序异常信息的捕获"
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_database_exception_async(func):
        "负责异步数据库 aiomysql 的异常捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except aiomysql.ProgrammingError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.programming_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3001,'DatabaseError',error_id)
            except aiomysql.OperationalError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.operational_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3002,'DatabaseError',error_id)
            except aiomysql.IntegrityError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.integrity_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3003,'DatabaseError',error_id)
            except aiomysql.DatabaseError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.database_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_database_exception_sync(func):
        "负责同步数据库 pymysql 和 sqlite3 的异常捕获"
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except pymysql.err.ProgrammingError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.programming_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3001,'DatabaseError',error_id)
            except pymysql.err.OperationalError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.operational_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3002,'DatabaseError',error_id)
            except pymysql.err.IntegrityError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.integrity_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3003,'DatabaseError',error_id)
            except pymysql.err.DatabaseError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.database_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
            except sqlite3.ProgrammingError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.programming_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3001,'DatabaseError',error_id)
            except sqlite3.OperationalError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.operational_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3002,'DatabaseError',error_id)
            except sqlite3.IntegrityError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.integrity_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3003,'DatabaseError',error_id)
            except sqlite3.DatabaseError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = DatabaseExceptionName.database_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'ERROR_{e.args[0]}\n' + str(e.args[1]) + f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_cache_exception_async(func):
        "负责缓存 Redis 的异常捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except redis.RedisError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.redis,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = f'\n{traceback.format_exc()}'
                )
                return JSONResponse.get_error_response(4000,'RedisError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_network_exception_async(func):
        "负责异步网络请求 httpx 的异常捕获"
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except httpx.ConnectTimeout:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.connect_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2001,'NetworkError',error_id)
            except httpx.ReadTimeout:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.read_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2002,'NetworkError',error_id)
            except httpx.TimeoutException:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.request_timeout,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2003,'NetworkError',error_id)
            except httpx.ConnectError:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.connect_error,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2004,'NetworkError',error_id)
            except httpx.ReadError:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.read_error,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2005,'NetworkError',error_id)
            except httpx.HTTPStatusError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.network_error,
                    error_args = str(args) + str(kwargs),
                    error_info = f'StatusCode: {e.response.status_code}'
                )
                return JSONResponse.get_error_response(2000,'NetworkError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper