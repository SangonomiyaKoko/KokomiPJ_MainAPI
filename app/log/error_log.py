import os

from app.utils import TimeFormat
from app.core import EnvConfig

config = EnvConfig.get_config()
log_path = config.LOG_PATH

def write_error_info(
    error_id: str,
    error_type: str,
    error_name: str,
    error_args: str = None,
    error_info: str = None
):
    now_day = TimeFormat.get_today()
    form_time = TimeFormat.get_form_time()
    with open(os.path.join(log_path, f'{now_day}.txt'), "a", encoding="utf-8") as f:
        f.write('-------------------------------------------------------------------------------------------------------------\n')
        f.write(f">Platform:     API\n")
        f.write(f">Error ID:     {error_id}\n")
        f.write(f">Error Type:   {error_type}\n")
        f.write(f">Error Name:   {error_name}\n")
        f.write(f">Error Time:   {form_time}\n")
        f.write(f">Error Info:   \n{error_args}\n{error_info}\n")
        f.write('-------------------------------------------------------------------------------------------------------------\n')
    f.close()