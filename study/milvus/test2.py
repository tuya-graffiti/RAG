# milvus_demo.py
import random
from datetime import datetime
from pymilvus import DataType, connections, utility
from conn.milvus_conn import MilvusConn  # 假设你有一个连接类
"""
1.元数据过滤类型
相等过滤: field == "value"
数值范围: field > value, field >= value
逻辑组合: and, or
IN 操作符: field in ["value1", "value2"]
布尔过滤: bool_field == true/false
2. 查询类型
向量搜索 + 过滤: 结合相似度搜索和元数据过滤
纯元数据查询: 仅基于元数据条件，不涉及向量
"""



class MilvusLearningDemo:
    def __init__(self, collection_name="MetadataFilter"):
        """初始化 Milvus 连接和集合名称"""
        self.client = MilvusConn("demo").client
        self.collection_name = collection_name

    def create_collection(self):
        """创建包含丰富元数据字段的集合"""
        # 定义 schema
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)

        # 添加字段
        schema.add_field("id", DataType.VARCHAR, max_length=64, is_primary=True)
        schema.add_field("text", DataType.VARCHAR, max_length=65535)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=768)
        schema.add_field("source", DataType.VARCHAR, max_length=256)
        schema.add_field("category", DataType.VARCHAR, max_length=256)
        schema.add_field("timestamp", DataType.FLOAT)
        schema.add_field("views", DataType.INT64)
        schema.add_field("rating", DataType.FLOAT)
        schema.add_field("tags", DataType.ARRAY,
                         element_type=DataType.VARCHAR,
                         max_capacity=100,
                         max_length=50)
        schema.add_field("author", DataType.VARCHAR, max_length=256)
        schema.add_field("is_public", DataType.BOOL)

        # 定义索引参数
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",  # 使用余弦相似度
            params={"nlist": 128}
        )

        # 创建集合
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"集合 '{self.collection_name}' 创建成功")

    def insert_sample_data(self):
        """插入示例数据"""
        datas = [
            {
                "id": "doc_001",
                "text": "这是第一篇文档的内容，介绍了人工智能的基本概念",
                "vector": [random.random() for _ in range(768)],
                "source": "website_A",
                "category": "technology",
                "timestamp": datetime(2024, 1, 15).timestamp(),
                "views": 1500,
                "rating": 4.5,
                "tags": ["AI", "基础"],
                "author": "李四",
                "is_public": True
            },
            {
                "id": "doc_002",
                "text": "第二篇文档讨论机器学习的各种算法和应用场景",
                "vector": [random.random() for _ in range(768)],
                "source": "website_B",
                "category": "technology",
                "timestamp": datetime(2024, 1, 20).timestamp(),
                "views": 2800,
                "rating": 4.8,
                "tags": ["机器学习", "算法"],
                "author": "王五",
                "is_public": True
            },
            {
                "id": "doc_003",
                "text": "第三篇文档深入探讨深度学习在自然语言处理中的应用",
                "vector": [random.random() for _ in range(768)],
                "source": "website_C",
                "category": "academic",
                "timestamp": datetime(2024, 2, 5).timestamp(),
                "views": 900,
                "rating": 4.2,
                "tags": ["深度学习", "NLP"],
                "author": "张三",
                "is_public": False
            },
            {
                "id": "doc_004",
                "text": "第四篇文档是关于Python编程的基础教程",
                "vector": [random.random() for _ in range(768)],
                "source": "website_A",
                "category": "programming",
                "timestamp": datetime(2024, 2, 10).timestamp(),
                "views": 3500,
                "rating": 4.7,
                "tags": ["Python", "编程"],
                "author": "赵六",
                "is_public": True
            }
        ]

        # 插入数据
        result = self.client.upsert(
            collection_name=self.collection_name,
            data=datas
        )
        print("示例数据插入完成")
        return result

    def demonstrate_metadata_filters(self):
        """演示各种元数据过滤查询"""
        query_vector = [random.random() for _ in range(768)]

        print("=== 元数据过滤查询演示 ===\n")

        # 1. 基本相等过滤
        print("1. 搜索特定来源的文档:")
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
            filter='source == "website_A"',
            output_fields=["id", "text", "source"]
        )
        self._print_search_results(results)

        # 2. 数值范围过滤
        print("2. 搜索浏览量大于2000的文档:")
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
            filter='views > 2000',
            output_fields=["id", "views", "rating"]
        )
        self._print_search_results(results)

        # 3. 多条件组合过滤
        print("3. 搜索技术类且评分高于4.5的文档:")
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
            filter='category == "technology" and rating > 4.5',
            output_fields=["id", "category", "rating"]
        )
        self._print_search_results(results)

        # 4. IN 操作符
        print("4. 搜索特定作者的文档:")
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
            filter='author in ["李四", "王五"]',
            output_fields=["id", "author"]
        )
        self._print_search_results(results)

        # 5. 布尔值过滤
        print("5. 搜索公开文档:")
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
            filter='is_public == true',
            output_fields=["id", "is_public"]
        )
        self._print_search_results(results)

    def _print_search_results(self, results):
        """格式化打印搜索结果"""
        for i, hits in enumerate(results):
            print(f"  搜索批次 {i}:")
            for hit in hits:
                print(f"    ID: {hit.id}, 距离: {hit.distance:.4f}, 实体: {hit.entity}")
        print()

    def demonstrate_pure_metadata_query(self):
        """演示纯元数据查询（不涉及向量）"""
        print("=== 纯元数据查询演示 ===")

        results = self.client.query(
            collection_name=self.collection_name,
            filter='rating >= 4.5 and is_public == true',
            output_fields=["id", "author", "rating", "views"]
        )

        print("高评分公开文档:")
        for result in results:
            print(f"  ID: {result['id']}, 作者: {result['author']}, "
                  f"评分: {result['rating']}, 浏览量: {result['views']}")
        print()

    def demonstrate_deletion_with_filter(self):
        """演示基于元数据过滤的文档删除"""
        print("=== 元数据过滤删除演示 ===")

        # 先查询符合条件的文档
        results_before = self.client.query(
            collection_name=self.collection_name,
            filter='rating < 4.5 and is_public == false',
            output_fields=["id", "rating", "is_public"]
        )

        print(f"删除前符合条件的文档数量: {len(results_before)}")
        for doc in results_before:
            print(f"  待删除: ID: {doc['id']}, 评分: {doc['rating']}, 公开: {doc['is_public']}")

        # 执行删除
        self.client.delete(
            collection_name=self.collection_name,
            filter='rating < 4.5 and is_public == false'
        )

        print("删除操作完成")

        # 验证删除结果
        results_after = self.client.query(
            collection_name=self.collection_name,
            filter='rating < 4.5 and is_public == false',
            output_fields=["id", "rating", "is_public"]
        )

        print(f"删除后剩余的文档数量: {len(results_after)}")

    def cleanup(self):
        """清理集合"""
        if utility.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            print(f"集合 '{self.collection_name}' 已删除")


def main():
    """主函数：演示完整的 Milvus 操作流程"""
    demo = MilvusLearningDemo()

    try:
        # 1. 创建集合
        demo.create_collection()

        # 2. 插入数据
        demo.insert_sample_data()

        # 3. 演示元数据过滤搜索
        demo.demonstrate_metadata_filters()

        # 4. 演示纯元数据查询
        demo.demonstrate_pure_metadata_query()

        # 5. 演示基于过滤条件的删除
        demo.demonstrate_deletion_with_filter()

    finally:
        # 6. 清理（可选）
        # demo.cleanup()
        pass


if __name__ == '__main__':
    main()