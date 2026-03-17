import os
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from dotenv import load_dotenv, find_dotenv

# Բեռնում ենք .env ֆայլը (find_dotenv-ն ավտոմատ կգտնի ֆայլը root թղթապանակում)
load_dotenv(find_dotenv())

# --- Azure OpenAI Embeddings ---
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),
    openai_api_version="2024-12-01-preview"
)

# --- Azure OpenAI Chat LLM (GPT-4o / gpt-4o-mini) ---
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

# --- Email (SMTP) Configuration ---
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.mail.ru")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

EMAIL_USE_TLS = os.getenv(
    "EMAIL_USE_TLS", "false").lower() in ("1", "true", "yes")
EMAIL_USE_SSL = os.getenv(
    "EMAIL_USE_SSL", "true").lower() in ("1", "true", "yes")
