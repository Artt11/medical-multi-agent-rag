# import json
# import os
# from azure.storage.blob import BlobServiceClient, ContentSettings
# from src.core.base_storage import IStorageService


# class AzureMedicalStorage(IStorageService):
#     def __init__(self, connection_string: str = None, container_name: str = "raw-files"):
#         conn_str = connection_string or os.getenv(
#             "AZURE_STORAGE_CONNECTION_STRING")
#         if not conn_str:
#             raise ValueError("Azure Storage Connection String is missing!")

#         self.blob_service_client = BlobServiceClient.from_connection_string(
#             conn_str)
#         self.container_client = self.blob_service_client.get_container_client(
#             container_name)

#         if not self.container_client.exists():
#             self.container_client.create_container()

#     def upload_pdf(self, file_hash: str, pdf_bytes: bytes) -> str:

#         blob_path = f"raw_pdfs/{file_hash}.pdf"
#         blob_client = self.container_client.get_blob_client(blob_path)

#         content_settings = ContentSettings(content_type='application/pdf')
#         blob_client.upload_blob(pdf_bytes, overwrite=True,
#                                 content_settings=content_settings)

#         return blob_client.url

#     def upload_json(self, file_hash: str, doc_data: dict) -> str:
#         blob_path = f"processed_jsons/{file_hash}.json"
#         blob_client = self.container_client.get_blob_client(blob_path)

#         json_data = json.dumps(doc_data, indent=4, ensure_ascii=False)
#         content_settings = ContentSettings(content_type='application/json')

#         blob_client.upload_blob(json_data, overwrite=True,
#                                 content_settings=content_settings)

#         return blob_client.url

#     def upload_medical_pair(self, file_hash: str, pdf_bytes: bytes, doc_data: dict) -> str:

#         pdf_url = self.upload_pdf(file_hash, pdf_bytes)
#         self.upload_json(file_hash, doc_data)

#         return pdf_url
