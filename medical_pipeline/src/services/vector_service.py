import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField, VectorSearch,
    VectorSearchProfile, HnswAlgorithmConfiguration
)
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


class AzureVectorService:
    def __init__(self, index_name="medical-reports-index"):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = index_name
        self.credential = AzureKeyCredential(self.key)

        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),
        )

    def create_index(self):
        index_client = SearchIndexClient(self.endpoint, self.credential)

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(
                name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),

            SimpleField(name="patient_id",
                        type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="document_hash",
                        type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="examination_type",
                            type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="blob_url", type=SearchFieldDataType.String)
        ]

        vector_search = VectorSearch(
            profiles=[VectorSearchProfile(
                name="myHnswProfile", algorithm_configuration_name="myHnsw")],
            algorithms=[HnswAlgorithmConfiguration(name="myHnsw")]
        )

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search
        )

        index_client.create_or_update_index(index)
        print(
            f" Ինդեքսը '{self.index_name}' հաջողությամբ ստեղծվեց (Vector Search Only):")

    def index_chunks(self, chunks):
        search_docs = []

        for i, chunk in enumerate(chunks):
            vector = self.embeddings.embed_query(chunk.page_content)

            search_docs.append({
                "id": f"{chunk.metadata.get('doc_hash')}-{i}",
                "content": chunk.page_content,
                "content_vector": vector,
                "patient_id": str(chunk.metadata.get("patient_db_id")),
                "document_hash": chunk.metadata.get("doc_hash"),
                "blob_url": chunk.metadata.get("blob_url"),
                "examination_type": chunk.metadata.get("examination_type", "Medical Report")
            })

        return self.upload_documents(search_docs)

    def upload_documents(self, documents):
        search_client = SearchClient(
            self.endpoint, self.index_name, self.credential)
        search_client.upload_documents(documents)
        print(f"✅ {len(documents)} փաստաթուղթ վերբեռնվեց:")
