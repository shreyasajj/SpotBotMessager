class BaseConfig:
    API_PREFIX = '/api'
    TESTING = False
    DEBUG = False


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    CELERY_BROKER = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'


class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'
    CELERY_BROKER = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'


class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    # make celery execute tasks synchronously in the same process
    CELERY_ALWAYS_EAGER = True
