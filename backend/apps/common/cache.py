"""缓存封装：Redis 不可用时自动降级为直查数据库，业务永不因缓存故障中断。

- cache_or_compute(key, ttl, compute)：读缓存，未命中算一遍并写回
- invalidate(keys)：批量失效（容错）
"""
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


def cache_or_compute(key, ttl, compute):
    try:
        value = cache.get(key)
        if value is not None:
            return value
        value = compute()
        cache.set(key, value, ttl)
        return value
    except Exception:
        # Redis 挂掉/连接失败：降级直查，只记日志不抛错
        logger.warning('缓存不可用，降级直查: %s', key, exc_info=True)
        return compute()


def invalidate(*keys):
    try:
        cache.delete_many(list(keys))
    except Exception:
        logger.warning('缓存失效失败，忽略: %s', keys, exc_info=True)
