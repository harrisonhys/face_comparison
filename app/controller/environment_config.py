from decouple import config
from functools import lru_cache

class EnvironmentConfig:
    @staticmethod
    @lru_cache(maxsize=None)  # Tidak ada batasan ukuran cache
    def get_env_value(key, default=None):
        return config(key, default=default)
    