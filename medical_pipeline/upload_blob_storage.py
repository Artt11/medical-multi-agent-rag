# from __future__ import annotations

# import argparse
# import os
# from pathlib import Path
# from typing import List, Optional, Tuple

# try:
#     from dotenv import load_dotenv, find_dotenv
# except Exception:
#     load_dotenv = None

# from src.services.azure_storage_service import AzureMedicalStorage
# from src.services.hash_service import BinaryHashService


# def _load_env() -> None:
#     if load_dotenv:
#         env_path = find_dotenv()
#         load_dotenv(env_path, override=True)

#         conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
#         if "medicaldatadiploma" in conn_str:
#             print(
#                 "✅ Հաջողություն: Կոդը կարդաց նոր 'medicaldatadiploma' Connection String-ը:")
#         else:
#             print("❌ ՍԽԱԼ: Կոդը դեռ կարդում է հին կամ դատարկ Connection String:")


# def _find_pdf_files(data_dir: Path) -> List[Path]:
#     if not data_dir.exists():
#         return []
#     return sorted([p for p in data_dir.rglob("*.pdf") if p.is_file()])


# def upload_pdfs(
#     data_dir: Path,
#     container_name: Optional[str] = None,
#     dry_run: bool = False,
# ) -> List[Tuple[Path, str]]:
#     pdf_files = _find_pdf_files(data_dir)
#     if not pdf_files:
#         return []

#     if dry_run:
#         return [(p, "") for p in pdf_files]

#     storage = (
#         AzureMedicalStorage(container_name=container_name)
#         if container_name
#         else AzureMedicalStorage()
#     )
#     hasher = BinaryHashService()

#     results: List[Tuple[Path, str]] = []
#     for pdf_path in pdf_files:
#         pdf_bytes = pdf_path.read_bytes()
#         file_hash = hasher.hash_bytes(pdf_bytes)
#         url = storage.upload_pdf(file_hash, pdf_bytes)
#         results.append((pdf_path, url))

#     return results


# def main() -> int:
#     # Environment փոփոխականները բեռնում ենք ամենասկզբից
#     _load_env()

#     parser = argparse.ArgumentParser(
#         description="Upload PDFs from data_pdf to Azure Blob Storage."
#     )
#     parser.add_argument(
#         "--data-dir",
#         default=str(Path(__file__).resolve().parent / "data_pdf"),
#         help="Directory containing PDF files to upload.",
#     )
#     parser.add_argument(
#         "--container",
#         default=None,
#         help="Azure Blob container name override.",
#     )
#     parser.add_argument(
#         "--dry-run",
#         action="store_true",
#         help="List files without uploading.",
#     )
#     args = parser.parse_args()

#     data_dir = Path(args.data_dir).expanduser().resolve()
#     pdf_files = _find_pdf_files(data_dir)

#     if not pdf_files:
#         print(f"No PDF files found in: {data_dir}")
#         return 0

#     if args.dry_run:
#         print("Dry run. Found PDF files:")
#         for pdf_path in pdf_files:
#             print(f"- {pdf_path}")
#         return 0

#     results = upload_pdfs(
#         data_dir, container_name=args.container, dry_run=False)

#     print("Uploaded PDF files:")
#     for pdf_path, url in results:
#         print(f"- {pdf_path} -> {url}")

#     return 0


# if __name__ == "__main__":
#     raise SystemExit(main())
