from pymilvus import MilvusClient,DataType
import base.config_gen as cfg
from datetime import datetime
import random
# ==== 1 连接milvus =======cfg.MILVUS.HOST
class MilvusConn:
    # 连接
    def __init__(self,url=f'http://47.108.85.255:8000',db_name='demo'):
        self.client = MilvusClient(uri=url,db_name=db_name)
        self.url = url
    # 建新数据库
    def create_datebase(self,db_name2):
        return self.client.create_database(db_name2)
    # 切换数据库
    def change_database(self,db_name3):
        return MilvusClient(self.url,db_name3)
    def close(self):
        self.client.close()
# ============2.向量存储操作类===============
class VectorStore:
    def __init__(self,collection_name = "demo_collection",db_name="demo"):
        self.client = MilvusConn(db_name).client
        self.collection_name = collection_name
    # 2.1 基础建表
    def create_basic_collection(self):
        """创建集合 Schema，禁用自动 ID，启用动态字段"""
        schema = self.client.create_schema(auto_id=False,enable_dynamic_field=True)
        schema.add_field(field_name="id",datatype=DataType.VARCHAR,is_primary=True,max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)
        self.client.create_collection(collection_name=self.collection_name,schema=schema)
        print(f"集合 {self.collection_name} 创建成功（base）")
   # 2.2 自动索引
    def create_autoindex_collection(self):
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)

        index_params = self.client.prepare_index_params()
        # 标量字段自动索引
        index_params.add_index(
            field_name='text',
            index_type='AUTOINDEX'
        )
        index_params.add_index(
            field_name="vector",
            index_type="AutoINDEX",
            metric_type="COSINE"
        )
        print(f"集合 {self.collection_name} 创建成功（自动索引）")
    # 2.3 自动索引
    def create_custom_index_collection(self):
        """创建带自定义索引的集合"""
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128}
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"集合 {self.collection_name} 创建成功（自定义索引）")

    # 2.4 多种索引示例
    def create_multi_index_collection(self):
        """创建包含多种索引的集合（演示用）"""
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="IVF_FLAT", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="IVF_SQ8", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="IVF_PQ", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="HNSW", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)

        index_params = self.client.prepare_index_params()

        # IVF_FLAT 索引
        index_params.add_index(
            field_name="IVF_FLAT",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128}
        )

        # IVF_SQ8 索引
        index_params.add_index(
            field_name="IVF_SQ8",
            index_type="IVF_SQ8",
            metric_type="COSINE",
            params={"nlist": 128}
        )

        # IVF_PQ 索引
        index_params.add_index(
            field_name="IVF_PQ",
            index_type="IVF_PQ",
            metric_type="COSINE",
            params={"nlist": 128, "m": 8, "nbits": 8}
        )

        # HNSW 索引
        index_params.add_index(
            field_name="HNSW",
            index_type="HNSW",
            metric_type="COSINE",
            params={"M": 30, "efConstruction": 360}
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"集合 {self.collection_name} 创建成功（多索引示例）")
    # 2.5 分区管理
    def create_partitioned_collecion(self):
        """
        创建带分区的集合
        :return:
        """
        self.partitons = {
            "website_A": "partition_website_A",
            "website_B": "partition_website_B",
            "website_C": "partition_website_C",
        }
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        for source,parition_name in self.partitons.items():
            self.client.create_partition(self.collection_name,parition_name)
            print("分区创建成功")
# ========== 3. 数据操作 ==========
    def insert_data(self, use_partition=False):
        """插入示例数据"""
        datas = [
            {
                "id": "doc_001",
                "text": "这是第一篇文档的内容，介绍了人工智能的基本概念",
                "vector": [random.random() for _ in range(768)],
                "source": "website_A",
                "timestamp": datetime.now().timestamp()
            },
            {
                "id": "doc_002",
                "text": "第二篇文档讨论机器学习的各种算法和应用场景",
                "vector": [random.random() for _ in range(768)],
                "source": "website_B",
                "timestamp": datetime.now().timestamp(),
            },
            {
                "id": "doc_003",
                "text": "第三篇文档深入探讨深度学习在自然语言处理中的应用",
                "vector": [random.random() for _ in range(768)],
                "source": "website_C",
                "timestamp": datetime.now().timestamp(),
                "author": "张三"  # 动态字段示例
            }
        ]
        if use_partition and hasattr(self,"partitons"):
            # 分区插入
            for data in datas:
                source = data['source']
                partition_name = self.partitons.get(source)
                # upsert/insert:updata+insert/insert
                result = self.client.upsert(
                    collection_name=self.collection_name,
                    data=[data],
                    partition_name=partition_name
                )
                print(f"数据插入成功 - ID: {data['id']}, 分区: {partition_name}")
    def search_data(self,query_vector=None,partition_name=None):
        """向量搜索"""
        if query_vector is None:
            # 格式: 双重列表 [[...]]，因为 Milvus 支持同时搜索多个向量
            query_vector = [[random.random() for _ in range(768)]]
        # nprobe: 8 - 搜索时检查的聚类数量（IVF索引参数）
        # 值越大，精度越高，但搜索速度越慢
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 8}}
        partition_names = None
        if partition_name and hasattr(self, 'partitions'):
            if partition_name in self.partitions.values():
                partition_names = [partition_name]
        results = self.client.search(
            collection_name=self.collection_name,
            data=query_vector,
            anns_field="vector",
            search_params=search_params,
            limit=3,
            output_fields=["id", "text", "source", "author"],
            partition_names=partition_names
        )
        return results
if __name__ == '__main__':
    client = MilvusClient(uri='http://47.108.85.255:19530', db_name='demo')


