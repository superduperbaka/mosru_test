from enum import Enum

from pydantic import BaseSettings, Field, validator


class RabbitMQSettings(BaseSettings):
    host: str = Field(..., env='RABBIT_HOST')
    port: int = Field(env='RABBIT_PORT', default=5672)
    v_host: str = Field(..., env='RABBIT_VHOST')
    user: str = Field(..., env='RABBIT_USER')
    password: str = Field(..., env='RABBIT_PASSWORD')
    task_queue: str = Field(env='RABBIT_TASK_QUEUE', default='task_queue')


class WorkerSettings(BaseSettings):
    url: str = Field(..., env='WORKER_TEST_URL', description='url address for message handling')
    num_workers: int = Field(env='WORKER_NUM', default=1, description='number async jobs in worker')


class _LogLevel(int, Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class MiscSettings(BaseSettings):
    log_level: _LogLevel = Field(env='LOG_LEVEL', default=10)

    @validator('log_level', pre=True)
    def to_int(cls, v: str):
        return int(v)
