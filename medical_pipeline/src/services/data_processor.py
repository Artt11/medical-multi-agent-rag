import json
import requests
from typing import Iterable
from src.core.base_processor import IProcessor, SupportsHashing
from src.models.document import MedicalDocument, PatientInfo
from src.models.elements import ElementType, ParsedElement


class MedicalProcessor(IProcessor):
    def __init__(self, hasher: SupportsHashing, model_name: str = "llama3")\
            -> None:
        self._hasher = hasher
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"

    def process(self, source_name: str, elements: Iterable[ParsedElement])\
            -> MedicalDocument:
        text_stream = []
        json_for_llm_list = []

        for el in elements:
            el_type_str = el.type.value if hasattr(
                el.type, 'value') else str(el.type)
            json_for_llm_list.append({
                "type": el_type_str,
                "page": el.page,
                "content": el.content
            })

            if el.type == ElementType.TEXT:
                text_stream.append(str(el.content))
            elif el.type == ElementType.TABLE:
                for row in el.content:
                    text_stream.append(" | ".join(
                        [str(c).strip() for c in row if c]))

        full_text = "\n".join(text_stream)

        json_payload_for_llm = json.dumps(
            json_for_llm_list, ensure_ascii=False)

        llm_extracted_data = self._extract_via_llm(json_payload_for_llm)

        patient_data = llm_extracted_data.get("patient", {})

        doc = MedicalDocument(
            source=source_name,
            patient=PatientInfo(**patient_data),
            diagnosis=llm_extracted_data.get("diagnosis", []),
            conclusion=llm_extracted_data.get("conclusion", []),
            recommendations=llm_extracted_data.get("recommendations", []),
            all_data=full_text,
            raw_elements=[el.model_dump() for el in elements]
        )

        if self._hasher:
            doc.hash = self._hasher.hash_bytes(full_text.encode("utf-8"))
            # doc.hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        return doc

    def _extract_via_llm(self, json_data_str: str) -> dict:

        prompt = f"""
        You are an expert medical data extractor.
        Read the provided Medical Document Data (which is in JSON format)\
            and extract the requested entities.
        CRITICAL RULES:
        1. Return ONLY a valid JSON object. No markdown, no extra text.
        2. Do NOT invent or hallucinate data. If a field is not found in the\
            text, set its value to null.
        3. Extract the exact words from the text.

        The JSON MUST have the EXACT following structure:
        {{
            "patient": {{
                "name": "full name or null",
                "dob": "date of birth or null",
                "gender": "male, female, or null",
                "patient_id": "patient ID or null",
                "social_card": "social card number or null",
                "email": "email address or null",
                "phone": "phone number or null",
                "exam_date": "date of examination or null",
                "referring_physician": "doctor's name or null",
                "examination_type": "type of examination or null"
            }},
            "diagnosis": ["list of diagnoses or empty list"],
            "conclusion": ["list of conclusions or empty list"],
            "recommendations": ["list of recommendations or empty list"]
        }}

        Medical Document Data:
        ---
        {json_data_str}
        ---
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }

        try:
            response = requests.post(
                self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            return json.loads(result["response"])
        except Exception as e:
            print(f" LLM Extraction failed: {e}")
            return {}
