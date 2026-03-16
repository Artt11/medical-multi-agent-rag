import io
import pdfplumber
from typing import Any, List
from src.core.base_parser import IParser
from src.models.elements import ElementType, ParsedElement


class PdfPlumberParser(IParser):
    def parse(self, payload: Any) -> List[ParsedElement]:

        if not isinstance(payload, (bytes, bytearray)):
            return []

        elements_list = []

        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 3
        }

        with pdfplumber.open(io.BytesIO(payload)) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                page_elements = []

                tables = page.find_tables(table_settings=table_settings)
                table_bboxes = [t.bbox for t in tables]

                for table in tables:
                    raw_data = table.extract()

                    page_elements.append(ParsedElement(
                        type=ElementType.TABLE,
                        content=raw_data,
                        page=page_idx,
                        top=table.bbox[1]
                    ))

                def not_in_table(obj):
                    if obj.get("object_type") not in ("char", "rect", "line"):
                        return True
                    x0, top, x1, bottom = obj["x0"], obj["top"], obj["x1"], obj["bottom"]
                    return not any(x0 >= b[0] and x1 <= b[2] and top >= b[1]
                                   and bottom <= b[3] for b in table_bboxes)
                lines = page.filter(not_in_table).extract_text_lines()

                for line in lines:
                    text_content = line["text"].strip()
                    if text_content:
                        page_elements.append(ParsedElement(
                            type=ElementType.TEXT,
                            content=text_content,
                            page=page_idx,
                            top=line["top"]
                        ))

                page_elements.sort(key=lambda x: x.top)

                elements_list.extend(page_elements)

        return elements_list
