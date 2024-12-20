import weaviate
from weaviate.classes.init import Auth
import os
import nltk
from nltk.tokenize import sent_tokenize
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from weaviate.classes.config import Configure, Property

# Download all necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

weaviate_url = os.environ.get("WEAVIATE_URL")
weaviate_key = os.environ.get("WEAVIATE_API_KEY")
mistral_key = os.getenv("MISTRAL_API_KEY")

headers = {
    "X-Mistral-Api-Key": mistral_key,
}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_key),
    headers=headers
)



# Check if collection exists, create only if it doesn't
collection_name = "DemoCollection"
try:
    collection = client.collections.get(collection_name)
    print(f"Collection {collection_name} already exists")
except:
    print(f"Creating collection {collection_name}")
    client.collections.create(
        collection_name,
        vectorizer_config=Configure.Vectorizer.text2vec_mistral(),
        generative_config=Configure.Generative.mistral(
            model="mistral-medium"
        ),
        properties=[
            {
                "name": "title",
                "dataType": ["text"]
            },
            {
                "name": "content",
                "dataType": ["text"]
            },
            {
                "name": "chunk_id",
                "dataType": ["text"]
            }
        ]
    )

def chunk_text(text, chunk_size=5):
    """Split text into chunks of approximately equal size based on sentences
    
    Example usage:
    >>> text = "Your long document text here..."
    >>> chunks = chunk_text(text, chunk_size=3)  # Split into chunks of 3 sentences
    >>> chunks = chunk_text(text, chunk_size=10)  # Larger chunks for more context
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        current_chunk.append(sentence)
        current_length += 1
        
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
    
    if current_chunk:  # Add any remaining sentences
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Example data structure:
# documents = [
#     {
#         "title": "Your Document Title",
#         "content": "Your document content...",
#         # Optional: Add more fields as needed
#         "author": "John Doe",
#         "date": "2024-03-21"
#     }
# ]

documents = [
    {
        "title": "Document 1",
        "content": "This is a long text document that needs to be chunked. It contains multiple sentences. Each sentence will be processed. We want to make sure it works properly. This is another sentence for testing.",
    },
    {
        "title": "Document 2",
        "content": "Another long document with content that should be split. It also has multiple sentences. We'll process this one too. Let's see how it works with our chunking method.",
    }
]

try:
    # Process and add documents
    for doc in documents:
        chunks = chunk_text(doc["content"])
        
        # Update the collection access syntax
        for i, chunk in enumerate(chunks):
            collection = client.collections.get(collection_name)
            collection.data.insert({
                "title": doc["title"],
                "content": chunk,
                "chunk_id": f"{doc['title']}_chunk_{i}"
            })
    print("Successfully added documents to collection")

    def query_documents(query: str, limit: int = 3):
        """
        Perform RAG query on the documents
        """
        try:
            # Get the collection reference
            collection = client.collections.get(collection_name)
            
            # First get relevant documents using near_text
            response = collection.query.near_text(
                query=query,
                limit=limit,
                return_properties=["title", "content", "chunk_id"]
            )

            if not response.objects:
                return {
                    "generated_answer": "No relevant documents found.",
                    "retrieved_chunks": []
                }

            # Prepare the context from retrieved chunks
            context = " ".join([obj.properties["content"] for obj in response.objects])
            
            # Generate answer using the context
            generate_prompt = f"""Based on the following context, answer the question.
            Context: {context}
            
            Question: {query}
            
            Answer:"""
            
            generated_response = collection.generate.near_text(
                query=query,
                prompt=generate_prompt
            )

            return {
                "generated_answer": generated_response.generated,
                "retrieved_chunks": [
                    {
                        "title": obj.properties["title"],
                        "content": obj.properties["content"],
                        "chunk_id": obj.properties["chunk_id"]
                    }
                    for obj in response.objects
                ]
            }
        except Exception as e:
            print(f"Query error: {str(e)}")
            return {"error": str(e)}

    # Example queries
    test_queries = [
        "How are the documents processed?",
        "What is the purpose of chunking?",
    ]

    # Example: Different ways to use the query results
    print("\nTesting RAG Queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = query_documents(query)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("Generated Answer:", result["generated_answer"])
            print("\nRetrieved Chunks:")
            for chunk in result["retrieved_chunks"]:
                print(f"- {chunk['title']}: {chunk['content'][:100]}...")
        
        # Increase delay between queries
        time.sleep(5)  # Increased from 2 to 5 seconds

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    # Always close the client to free up resources
    client.close()
# Additional usage examples:
# 1. Batch processing:
# docs = load_documents_from_directory("path/to/docs")
# for batch in chunks(docs, batch_size=100):
#     process_batch(batch)

# 2. Custom error handling:
# try:
#     result = query_documents("your question")
#     if "error" in result:
#         handle_error(result["error"])
#     else:
#         process_success(result)
# except Exception as e:
#     handle_exception(e)

# 3. Advanced querying:
# result = query_documents(
#     query="complex question",
#     limit=5,  # Get more context
# )
