from managers import vector_store
from offline.insert2milvus import doc_process
from datas.filepaths import PDFS_DIR

def insert_data():
    vs = vector_store.VectorStore()
    loader = doc_process.DocumentLoader()
    chunks = loader.load_directory(PDFS_DIR)
    vs.add_chunks(chunks)
if __name__ == '__main__':
    insert_data()
