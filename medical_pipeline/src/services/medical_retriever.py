# import os
# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.models import VectorizedQuery
# from src.core.base_retriever import IBaseRetriever
# from src.core.schemas import MedicalSearchQuery, RetrieverOutput
# from src.core.config import embeddings
# from typing import List


# class HybridMedicalRetriever(IBaseRetriever):
#     def __init__(self, index_name="medical-reports-index"):
#         self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
#         self.key = os.getenv("AZURE_SEARCH_KEY")
#         self.credential = AzureKeyCredential(self.key)
#         self.client = SearchClient(self.endpoint, index_name, self.credential)

#     def search(self, params: MedicalSearchQuery) -> List[RetrieverOutput]:

#         query_vector = embeddings.embed_query(params.query_text)

#         vector_query = VectorizedQuery(
#             vector=query_vector,
#             k_nearest_neighbors=params.top_k,
#             fields="content_vector"
#         )

#         results = self.client.search(
#             search_text=params.query_text,
#             vector_queries=[vector_query],
#             filter=f"patient_id eq '{params.patient_id}'",
#             top=params.top_k,
#             semantic_configuration_name="my-semantic-config"
#         )

#         return [
#             RetrieverOutput(
#                 content=doc.get("content"),
#                 page_number=doc.get("metadata", {}).get("page"),
#                 blob_url=doc.get("blob_url"),
#                 score=doc.get("@search.score", 0.0),
#                 metadata=doc.get("metadata", {})
#             ) for doc in results
#         ]
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from src.core.base_retriever import IBaseRetriever
from src.core.schemas import MedicalSearchQuery, RetrieverOutput
from src.core.config import embeddings
from typing import List


class HybridMedicalRetriever(IBaseRetriever):
    def __init__(self, index_name="medical-reports-index"):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.credential = AzureKeyCredential(self.key)
        self.client = SearchClient(self.endpoint, index_name, self.credential)

    def search(self, params: MedicalSearchQuery) -> List[RetrieverOutput]:
        # 1. Հարցումը վերածում ենք վեկտորի
        query_vector = embeddings.embed_query(params.query_text)

        # 2. Սահմանում ենք վեկտորային որոնումը
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=params.top_k,
            fields="content_vector"
        )

        # 3. Կատարում ենք Hybrid Search (առանց Semantic Ranker-ի)
        # Azure-ը ինքնուրույն կմիավորի BM25 և Vector արդյունքները RRF-ով
        filter_expr = None
        if params.patient_id:
            patient_id = str(params.patient_id).strip()
            if patient_id and patient_id.lower() != "unknown":
                filter_expr = f"patient_id eq '{patient_id}'"

        search_kwargs = {
            "search_text": params.query_text,   # BM25 (Keyword search)
            "vector_queries": [vector_query],  # Vector search
            "top": params.top_k,
            # semantic_configuration_name հեռացված է Free Tier-ի համար
        }
        if filter_expr:
            search_kwargs["filter"] = filter_expr

        results = self.client.search(**search_kwargs)

        return [
            RetrieverOutput(
                content=doc.get("content"),
                page_number=doc.get("metadata", {}).get("page"),
                blob_url=doc.get("blob_url"),
                document_hash=doc.get("document_hash"),
                score=doc.get("@search.score", 0.0),
                metadata=doc.get("metadata", {})
            ) for doc in results
        ]
