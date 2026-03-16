import json
from src.models.document import MedicalDocument


class JSONExporter:
    @staticmethod
    def export(doc: MedicalDocument, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                doc.model_dump(mode="json"),
                f,
                ensure_ascii=False,
                indent=4,
            )
        print(f"JSON ֆայլը պատրաստ է: {output_path}")
