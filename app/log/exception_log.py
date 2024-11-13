import uuid
import traceback

import httpx
from pymysql.err import ProgrammingError
from aiomysql import MySQLError
from aioredis.exceptions import RedisError

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

def generate_error_id():
    return str(uuid.uuid4())

class ExceptionLogger:
    @staticmethod
    def handle_program_exception_async(func):
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
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_program_exception_sync(func):
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
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_database_exception_async(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except MySQLError as e:
                error_id = generate_error_id()
                traceback.print_exc()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = f'ERROR_{e.args[0]}',
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = str(e.args[1])
                )
                return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_file = __file__,
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_database_exception_sync(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except ProgrammingError as e:
                error_id = generate_error_id()
                traceback.print_exc()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.mysql,
                    error_name = f'ERROR_{e.args[0]}',
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = str(e.args[1])
                )
                return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
            except Exception as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.program,
                    error_name = str(type(e).__name__),
                    error_file = __file__,
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_cache_exception_async(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except RedisError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type =ExceptionType.redis,
                    error_name = str(type(e).__name__),
                    error_file = __file__,
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
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper
    
    @staticmethod
    def handle_network_exception_async(func):
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
                    error_file = __file__,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2001,'NetworkError',error_id)
            except httpx.ReadTimeout:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.read_timeout,
                    error_file = __file__,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2002,'NetworkError',error_id)
            except httpx.TimeoutException:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.request_timeout,
                    error_file = __file__,
                    error_args = str(args) + str(kwargs)
                )
                return JSONResponse.get_error_response(2003,'NetworkError',error_id)
            except httpx.HTTPStatusError as e:
                error_id = generate_error_id()
                write_error_info(
                    error_id = error_id,
                    error_type = ExceptionType.network,
                    error_name = NerworkExceptionName.network_error,
                    error_file = __file__,
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
                    error_file = __file__,
                    error_args = str(args) + str(kwargs),
                    error_info = traceback.format_exc()
                )
                return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        return wrapper