import io
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from src.core.base_storage import IStorageService


class GoogleDriveService(IStorageService):
    def __init__(self, credentials_path: str, folder_id: str):
        """
        Սկզբնավորում է Google Drive API-ն Service Account-ի միջոցով:
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            # readonly-ն բավարար է կարդալու համար
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = folder_id

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Վերցնում է նշված թղթապանակի բոլոր PDF ֆայլերը:
        """
        query = f"'{self.folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        try:
            results = self.service.files().list(
                q=query,
                fields="files(id, name, webViewLink)",
                pageSize=1000  # Կարող ես կարգավորել ըստ քանակի
            ).execute()

            return results.get('files', [])
        except Exception as e:
            print(
                f"--- ❌ Սխալ Google Drive-ից ֆայլերի ցուցակը վերցնելիս: {e} ---")
            return []

    def download_file_bytes(self, file_id: str) -> bytes:
        """
        Ներբեռնում է ֆայլը որպես բայթերի հոսք (RAM)՝ առանց սկավառակի վրա պահելու:
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            return fh.getvalue()
        except Exception as e:
            print(f"--- ❌ Սխալ ֆայլը ներբեռնելիս (ID: {file_id}): {e} ---")
            raise e

    def upload_medical_pair(self, file_hash: str, pdf_bytes: bytes, doc_data: dict) -> str:
        """
        Մնում է IStorageService ինտերֆեյսի պահանջը բավարարելու համար:
        Քանի որ մենք հիմա աշխատում ենք ավտոմատ sync մոդելով (Drive-ից դեպի SQL),
        այս մեթոդն այս պրոցեսում ակտիվ չի օգտագործվում:
        """
        pass
