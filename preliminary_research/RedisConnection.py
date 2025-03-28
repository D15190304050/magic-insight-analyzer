import logging

import redis
from Configuration import Configuration

logger = logging.getLogger()

config = Configuration.get_instance()

def run_test():
    # 创建 Redis 连接池（可选）
    pool = redis.ConnectionPool(host=config.redis_host,
                                port=config.redis_port,
                                db=config.redis_db)

    # 使用连接池连接到 Redis 服务
    r = redis.Redis(connection_pool=pool)

    # 或者直接连接到 Redis 服务
    # r = redis.Redis(host='localhost', port=6379, db=0)

    # 测试连接
    logger.info(r.ping())  # 如果返回 True，则表示成功连接

    # 设置一个键值对
    r.set('mykey', 'Hello World')

    # 获取键值对
    value = r.get('mykey')
    logger.info(value)  # 输出: b'Hello World'

    # 向名为 'myset' 的 Set 添加元素
    r.sadd('myset', 'item1')
    r.sadd('myset', 'item2')
    r.sadd('myset', 'item3')

    # 检查元素是否在 Set 中
    logger.info(r.sismember('myset', 'item1'))  # 输出: True
    logger.info(r.sismember('myset', 'item4'))  # 输出: False

    # 获取 'myset' 中的所有元素
    items = r.smembers('myset')
    logger.info(items)  # 输出: {b'item1', b'item2', b'item3'}

    # 从 'myset' 中删除元素
    r.srem('myset', 'item2')
    logger.info(r.smembers('myset'))  # 输出: {b'item1', b'item3'}

    # 向名为 'mylist' 的 List 添加元素
    r.lpush('mylist', 'item1')
    r.lpush('mylist', 'item2')
    r.rpush('mylist', 'item3')
    r.rpush('mylist', 'item4')

    # 获取 'mylist' 中的所有元素
    items = r.lrange('mylist', 0, -1)
    logger.info(items)  # 输出: [b'item2', b'item1', b'item3', b'item4']

    # 获取 'mylist' 中部分元素
    items = r.lrange('mylist', 0, 2)  # 获取前三个元素
    logger.info(items)  # 输出: [b'item2', b'item1', b'item3']

    # 从 'mylist' 中删除元素
    logger.info(r.lpop('mylist'))  # 删除第一个元素
    logger.info(r.rpop('mylist'))  # 删除最后一个元素
    items = r.lrange('mylist', 0, -1)
    logger.info(items)  # 输出: [b'item1', b'item3']