import os
from datetime import datetime, timedelta
from typing import Iterable, List, Optional

from azure.storage.blob import BlobSasPermissions, generate_blob_sas


def _parse_connection_string(conn_str: str) -> dict:
    parts = conn_str.split(";")
    parsed = {}
    for part in parts:
        if not part:
            continue
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        parsed[key] = value
    return parsed


def build_pdf_url(
    doc_hash: str,
    container_name: str = "reports-archive",
    use_sas: bool = True
) -> Optional[str]:
    if not doc_hash:
        return None

    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    if not conn_str:
        return None

    parsed = _parse_connection_string(conn_str)
    blob_endpoint = parsed.get("BlobEndpoint", "").rstrip("/")
    account = parsed.get("AccountName", "")
    account_key = parsed.get("AccountKey", "")
    if blob_endpoint:
        base = blob_endpoint
    else:
        if not account:
            return None
        endpoint_suffix = parsed.get("EndpointSuffix", "core.windows.net")
        base = f"https://{account}.blob.{endpoint_suffix}"

    blob_name = f"raw_pdfs/{doc_hash}.pdf"

    if use_sas and account and account_key:
        expiry_minutes = int(os.getenv("AZURE_BLOB_SAS_EXPIRY_MINUTES", "120"))
        sas_token = generate_blob_sas(
            account_name=account,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes),
        )
        return f"{base}/{container_name}/{blob_name}?{sas_token}"

    return f"{base}/{container_name}/{blob_name}"


def build_pdf_urls(
    doc_hashes: Iterable[str],
    container_name: str = "reports-archive",
    use_sas: bool = True
) -> List[str]:
    urls: List[str] = []
    for doc_hash in doc_hashes:
        url = build_pdf_url(
            doc_hash, container_name=container_name, use_sas=use_sas)
        if url:
            urls.append(url)
    return urls


def format_source_links(urls: Iterable[str], title: str = "Source Documents") -> str:
    unique: List[str] = []
    seen = set()
    for url in urls:
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        unique.append(url)

    if not unique:
        return ""

    lines = ["", "", title]
    for idx, url in enumerate(unique, start=1):
        label = f"PDF {idx}"
        lines.append(f"- [{label}]({url})")

    return "\n".join(lines)
