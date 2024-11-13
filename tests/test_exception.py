import logging

def log_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"函数 {func.__name__} 执行出错: {e}")
            raise e
    return wrapper

@log_exception
def example_function(a, b):
    try:
        raise ValueError
    except Exception as e:
        logging.warning(f"在函数内部捕获到异常: {e}")
        # 如果希望继续抛出给装饰器处理，可以选择抛出
        raise e  # 这里将异常抛出给装饰器的 except 捕获
    finally:
        print(1)

# 外层调用
try:
    result = example_function(10, 0)
except Exception as e:
    print(f"外层捕获到异常: {type(e).__name__}")
