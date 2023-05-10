import pinecone
import os
from tqdm import tqdm
from config import AppConfig
from app.hash_sha import hash_message_to_sha_256

# pinecone init
pinecone.init(api_key=AppConfig.PINECONE_API_KEY,
              environment=AppConfig.PINECONE_ENVIRONMENT)
index = pinecone.Index(AppConfig.PINECONE_NAME)


def pinecone_message_upsert(
        message,
        vector,
        namespace='messages'
):
    message_dict = [{
        "id": hash_message_to_sha_256(message),
        "values": vector,
        "metadata": {
            "message": message
        }
    }]
    index.upsert(vectors=message_dict, namespace=namespace)

def pinecone_message_upsert_with_output(
        message,
        vector, 
        output, 
        from_where, 
        namespace='messages'
):
    message_dict = [{
        "id": hash_message_to_sha_256(message),
        "values": vector,
        "metadata": {
            "message": message,
            "output": output,
            "from_where": from_where
        }
    }]
    index.upsert(vectors=message_dict, namespace=namespace)


def fetch_pinecone_embedding(message_hash, namespace='messages'):
    return index.fetch(ids=[message_hash], namespace=namespace)['vectors']

def query_many(vector, namespaces, top_k=3):
    matches = []
    for namespace in namespaces:
        query_response = index.query(
            namespace=namespace,
            top_k=top_k,
            include_metadata=True,
            include_values=False,
            vector=vector
        )
        matches += query_response['matches']
    return matches

def gather_content(queries):
    content = []
    for query in queries:
        content.append(query['metadata']['content'])
    return content

def query_pinecone(vector, namespace, top_k=5):
    query_response = index.query(
        namespace=namespace,
        top_k=top_k,
        include_values=False,
        include_metadata=True,
        vector=vector)
    return query_response['matches']
