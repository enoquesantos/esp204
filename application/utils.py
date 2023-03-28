import os
from os.path import abspath, dirname

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured


def get_env(var_name, default_value=None, is_bool=False):
    try:
        value = os.environ.get(var_name)
        if is_bool:
            if str(value).lower() == 'true':
                return True
            elif str(value).lower() == 'false':
                return False
            return default_value
        if value is None:
            return default_value
        return value
    except KeyError:
        error_msg = "set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


def create_file(file_name: str, content: str):
    dir_path = os.path.dirname(file_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_name, mode='w') as f:
        f.write(content)


if os.environ.get('ENV_LOADED') == None:
    # initialize environment variables only once

    os.environ.setdefault('ENV_LOADED', '1')

    dotenv_path = '/home/es204/.env'
    dotenv_path = dotenv_path if os.path.exists(dotenv_path) else dirname(abspath(__file__)) + '/.env'

    load_dotenv(dotenv_path)
