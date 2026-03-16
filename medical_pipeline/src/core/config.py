# from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
# import os
# embeddings = AzureOpenAIEmbeddings(
#     azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
#     azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
#     api_key=os.getenv("AZURE_EMBEDDING_API_KEY")
# )

# llm = AzureChatOpenAI(
#     azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY")
# )


import os
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),
    openai_api_version="2024-12-01-preview"
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),

    temperature=0,
    max_retries=10,
    timeout=60,
    max_tokens=2000
)
