# redis_learning.py
import redis
from base import config_gen as cfg


class RedisClient:
    def __init__(self, db=1):
        """
        初始化Redis客户端
        :param db: 数据库编号，默认为1
        """
        self.client = redis.Redis(
            host=cfg.REDIS.HOST,
            port=cfg.REDIS.PORT,
            password=cfg.REDIS.PASSWORD,
            db=db,
            decode_responses=True  # 设置返回结果为字符串
        )

    def ping(self):
        """测试连接"""
        return self.client.ping()

    # ==================== 字符串操作 ====================
    def set_string(self, key, value, ex=None):
        """
        设置字符串键值对
        :param key: 键
        :param value: 值
        :param ex: 过期时间（秒）
        :return: bool
        """
        return self.client.set(key, value, ex=ex)

    def get_string(self, key):
        """
        获取字符串值
        :param key: 键
        :return: 值
        """
        return self.client.get(key)

    # ==================== 哈希操作 ====================
    def set_hash_field(self, key, field, value):
        """
        设置哈希字段
        :param key: 哈希键
        :param field: 字段名
        :param value: 字段值
        :return: 1/0 成功或失败
        """
        return self.client.hset(key, field, value)

    def get_hash_field(self, key, field):
        """
        获取哈希字段值
        :param key: 哈希键
        :param field: 字段名
        :return: 字段值
        """
        return self.client.hget(key, field)

    def set_hash_multiple(self, key, mapping):
        """
        一次性设置多个哈希字段
        :param key: 哈希键
        :param mapping: 字段字典
        :return: 插入的字段数
        """
        return self.client.hset(key, mapping=mapping)

    def get_hash_all(self, key):
        """
        获取哈希所有字段和值
        :param key: 哈希键
        :return: 字段字典
        """
        return self.client.hgetall(key)

    def get_hash_keys(self, key):
        """
        获取哈希所有字段名
        :param key: 哈希键
        :return: 字段名列表
        """
        return self.client.hkeys(key)

    def delete_hash_field(self, key, field):
        """
        删除哈希字段
        :param key: 哈希键
        :param field: 字段名
        :return: 删除的字段数量
        """
        return self.client.hdel(key, field)

    # ==================== 列表操作 ====================
    def list_push_left(self, key, *values):
        """
        从列表左侧插入元素
        :param key: 列表键
        :param values: 要插入的值
        :return: 插入后列表长度
        """
        return self.client.lpush(key, *values)

    def list_push_right(self, key, *values):
        """
        从列表右侧插入元素
        :param key: 列表键
        :param values: 要插入的值
        :return: 插入后列表长度
        """
        return self.client.rpush(key, *values)

    def list_pop_left(self, key):
        """
        从列表左侧弹出元素
        :param key: 列表键
        :return: 弹出的元素
        """
        return self.client.lpop(key)

    def list_pop_right(self, key):
        """
        从列表右侧弹出元素
        :param key: 列表键
        :return: 弹出的元素
        """
        return self.client.rpop(key)

    def list_range(self, key, start=0, stop=-1):
        """
        获取列表片段
        :param key: 列表键
        :param start: 开始索引
        :param stop: 结束索引
        :return: 列表片段
        """
        return self.client.lrange(key, start, stop)

    def list_length(self, key):
        """
        获取列表长度
        :param key: 列表键
        :return: 列表长度
        """
        return self.client.llen(key)

    def list_get_by_index(self, key, index):
        """
        根据索引获取列表元素
        :param key: 列表键
        :param index: 索引位置
        :return: 元素值
        """
        return self.client.lindex(key, index)

    # ==================== 批量操作 ====================
    def get_keys_by_pattern(self, pattern, count=100):
        """
        批量获取匹配模式的键（高效方式）
        :param pattern: 键模式
        :param count: 每次扫描数量
        :return: 键列表
        """
        keys = []
        cursor = 0
        while True:
            cursor, partial_keys = self.client.scan(cursor=cursor, match=pattern, count=count)
            keys.extend(partial_keys)
            if cursor == 0:
                break
        return keys

    def batch_get_strings(self, pattern):
        """
        批量获取字符串值
        :param pattern: 键模式
        :return: 键值对字典
        """
        keys = self.get_keys_by_pattern(pattern)
        values = self.client.mget(keys)
        return dict(zip(keys, values))

    def batch_get_hashes(self, pattern):
        """
        批量获取哈希值
        :param pattern: 键模式
        :return: 哈希字典
        """
        keys = self.get_keys_by_pattern(pattern)
        pipeline = self.client.pipeline()
        for key in keys:
            pipeline.hgetall(key)
        results = pipeline.execute()
        return dict(zip(keys, results))

    def batch_set_strings(self, data_dict, expire_seconds=None):
        """
        批量设置字符串键值对
        :param data_dict: 键值对字典
        :param expire_seconds: 过期时间（秒）
        :return: 操作结果列表
        """
        pipeline = self.client.pipeline()
        for key, value in data_dict.items():
            pipeline.set(key, value, ex=expire_seconds)
        return pipeline.execute()

    def batch_set_hashes(self, hash_data, expire_seconds=None):
        """
        批量设置哈希数据
        :param hash_data: 哈希数据字典
        :param expire_seconds: 过期时间（秒）
        :return: 操作结果列表
        """
        pipeline = self.client.pipeline()
        for hash_key, field_dict in hash_data.items():
            pipeline.hset(hash_key, mapping=field_dict)
            if expire_seconds:
                pipeline.expire(hash_key, expire_seconds)
        return pipeline.execute()

    # ==================== 通用操作 ====================
    def set_expire(self, key, seconds):
        """
        设置键的过期时间
        :param key: 键名
        :param seconds: 过期时间（秒）
        :return: bool
        """
        return self.client.expire(key, seconds)

    def delete_key(self, key):
        """
        删除键
        :param key: 键名
        :return: 删除的键数量
        """
        return self.client.delete(key)

    def exists_key(self, key):
        """
        检查键是否存在
        :param key: 键名
        :return: bool
        """
        return self.client.exists(key)


def demo_all_operations():
    """演示所有Redis操作"""
    # 创建客户端
    r = RedisClient()

    print("=== Redis学习演示 ===\n")

    # 1. 测试连接
    print("1. 连接测试:")
    print(f"连接状态: {'成功' if r.ping() else '失败'}\n")

    # 2. 字符串操作演示
    print("2. 字符串操作:")
    r.set_string("demo:string", "Hello Redis!", ex=60)
    value = r.get_string("demo:string")
    print(f"设置字符串: demo:string = {value}")

    # 3. 哈希操作演示
    print("\n3. 哈希操作:")
    # 设置单个字段
    r.set_hash_field("demo:hash", "name", "张三")
    r.set_hash_field("demo:hash", "age", "25")

    # 批量设置字段
    r.set_hash_multiple("demo:hash2", {"name": "李四", "age": "30", "city": "北京"})

    # 获取数据
    hash_data = r.get_hash_all("demo:hash")
    print(f"哈希数据: {hash_data}")
    print(f"哈希字段: {r.get_hash_keys('demo:hash')}")
    print(f"单个字段: {r.get_hash_field('demo:hash', 'name')}")

    # 4. 列表操作演示
    print("\n4. 列表操作:")
    r.list_push_left("demo:list", "item3", "item2", "item1")
    r.list_push_right("demo:list", "item4", "item5")

    list_data = r.list_range("demo:list")
    print(f"列表内容: {list_data}")
    print(f"列表长度: {r.list_length('demo:list')}")
    print(f"左侧弹出: {r.list_pop_left('demo:list')}")
    print(f"索引获取: {r.list_get_by_index('demo:list', 0)}")

    # 5. 批量操作演示
    print("\n5. 批量操作:")
    # 批量设置字符串
    strings_data = {
        "batch:str1": "value1",
        "batch:str2": "value2",
        "batch:str3": "value3"
    }
    r.batch_set_strings(strings_data, 120)

    # 批量设置哈希
    hashes_data = {
        "batch:hash1": {"field1": "val1", "field2": "val2"},
        "batch:hash2": {"field3": "val3", "field4": "val4"}
    }
    r.batch_set_hashes(hashes_data, 120)

    # 批量获取
    batch_strings = r.batch_get_strings("batch:*")
    print(f"批量字符串: {batch_strings}")

    # 6. 清理演示数据
    print("\n6. 清理演示数据...")
    keys_to_delete = [
        "demo:string", "demo:hash", "demo:hash2", "demo:list",
        "batch:str1", "batch:str2", "batch:str3",
        "batch:hash1", "batch:hash2"
    ]

    for key in keys_to_delete:
        if r.exists_key(key):
            r.delete_key(key)

    print("演示完成！")


if __name__ == "__main__":
    demo_all_operations()