import weaviate
from weaviate.classes.init import Auth
import os

weaviate_url = os.environ.get("WEAVIATE_URL")
weaviate_key = os.environ.get("WEAVIATE_API_KEY")

mistral_key = os.getenv("MISTRAL_API_KEY")
headers = {
    "X-Mistral-Api-Key": mistral_key,}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,                       # `weaviate_url`: your Weaviate URL
    auth_credentials=Auth.api_key(weaviate_key),      # `weaviate_key`: your Weaviate API key
    headers=headers
)

from weaviate.classes.config import Configure

client.collections.create(
    "DemoCollection",
    vectorizer_config=[
        Configure.NamedVectors.text2vec_mistral(
            name="title_vector",
            source_properties=["title"],
        )
    ],
    # Additional parameters not shown
)

# from weaviate.classes.config import Configure

# client.collections.create(
#     "DemoCollection",
#     generative_config=Configure.Generative.mistral()
#     # Additional parameters not shown
# )

# import weaviate
# from weaviate.classes.init import Auth
# import os

# # Recommended: save sensitive data as environment variables
# mistral_key = os.getenv("MISTRAL_APIKEY")
# headers = {
#     "X-Mistral-Api-Key": mistral_key,
# }

# client = weaviate.connect_to_weaviate_cloud(
#     cluster_url=weaviate_url,                       # `weaviate_url`: your Weaviate URL
#     auth_credentials=Auth.api_key(weaviate_key),      # `weaviate_key`: your Weaviate API key
#     headers=headers
# )

# # Work with Weaviate

# client.close()

# from weaviate.classes.config import Configure

# client.collections.create(
#     "DemoCollection",
#     generative_config=Configure.Generative.mistral(
#         model="mistral-large-latest"
#     )
#     # Additional parameters not shown
# )

# Work with Weaviate

client.close()

# from weaviate.classes.config import Configure

# client.collections.create(
#     "DemoCollection",
#     vectorizer_config=[
#         Configure.NamedVectors.text2vec_weaviate(
#             name="title_vector",
#             source_properties=["title"]
#         )
#     ],
#     # Additional parameters not shown
# )

# from weaviate.classes.config import Configure, Property, DataType

# client.collections.create(
#     "Article",
#     vectorizer_config=Configure.Vectorizer.text2vec_openai(),
#     properties=[  # properties configuration is optional
#         Property(name="title", data_type=DataType.TEXT),
#         Property(name="body", data_type=DataType.TEXT),
#     ]
# )