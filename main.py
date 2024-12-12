import weaviate
from weaviate.classes.init import Auth
import os

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,                       # `weaviate_url`: your Weaviate URL
    auth_credentials=Auth.api_key(weaviate_key),    # `weaviate_key`: your Weaviate API key
)

# Work with Weaviate

client.close()