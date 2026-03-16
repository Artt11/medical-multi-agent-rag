from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.base_chunking import IChunkingService
from src.models.document import MedicalDocument, MedicalChunk
from src.models.elements import ElementType


class ChunkingService(IChunkingService):
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def create_chunks(self, doc: MedicalDocument) -> List[MedicalChunk]:
        if not doc.raw_elements:
            print("ԶԳՈՒՇԱՑՈՒՄ: raw_elements-ը դատարկ է: Chunking չի արվի:")
            return []

        chunks = []
        current_section = "General / Header"
        current_text_buffer = []

        base_metadata = {
            "source": doc.source,
            "patient_id": str(doc.patient.patient_id or "unknown"),
            "patient_name": doc.patient.name,
            "exam_date": str(doc.patient.exam_date) if doc.patient.exam_date else None
        }

        def flush_buffer():
            if not current_text_buffer:
                return

            text_content = "\n".join(current_text_buffer).strip()
            if not text_content:
                return

            if len(text_content) < 1000:
                chunks.append(MedicalChunk(
                    page_content=text_content,
                    metadata={
                        **base_metadata,
                        "section": current_section,
                        "type": "text"
                    }
                ))
            else:
                split_texts = self.text_splitter.split_text(text_content)
                for i, split_t in enumerate(split_texts):
                    chunks.append(MedicalChunk(
                        page_content=split_t,
                        metadata={
                            **base_metadata,
                            "section": current_section,
                            "type": "text",
                            "chunk_index": i
                        }
                    ))

            current_text_buffer.clear()

        for el in doc.raw_elements:
            if not isinstance(el, dict):
                try:
                    el = el.dict()
                except:
                    continue

            content = str(el.get("content", "")).strip()
            el_type = el.get("type")

            if not content:
                continue

            is_header = (
                (content.isupper() and len(content) < 50 and content.endswith(":")) or
                ("CONCLUSION" in content.upper() and len(content) < 20)
            )

            if is_header:
                flush_buffer()
                current_section = content.replace(":", "").title()
                continue

            if el_type == ElementType.TABLE.value or el_type == "table":
                flush_buffer()
                table_md = self._format_table_to_markdown(el.get("content"))

                if table_md:
                    chunks.append(MedicalChunk(
                        page_content=table_md,
                        metadata={**base_metadata,
                                  "section": current_section, "type": "table"}
                    ))

            elif el_type == ElementType.TEXT.value or el_type == "text":
                current_text_buffer.append(content)

        flush_buffer()

        print(f" Chunking completed: Created {len(chunks)} chunks.")
        return chunks

    def _format_table_to_markdown(self, table_data: List[List[str]]) -> str:
        if not table_data:
            return ""

        try:
            headers = [str(cell).strip()
                       if cell else "" for cell in table_data[0]]
            lines = [
                "| " + " | ".join(headers) + " |",
                "| " + " | ".join(["---"] * len(headers)) + " |"
            ]
            for row in table_data[1:]:
                clean_row = [str(cell).strip() if cell else "" for cell in row]
                lines.append("| " + " | ".join(clean_row) + " |")
            return "\n".join(lines)
        except Exception as e:
            print(f" Table formatting error: {e}")
            return ""
