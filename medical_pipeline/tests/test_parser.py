from src.services.pdf_parser import UnstructuredParser
from src.models.document import MedicalDocument


def test_parse_returns_document():
    payload = "Line one\nLine two"
    parser = UnstructuredParser(source="test")

    result = parser.parse(payload)

    assert isinstance(result, MedicalDocument)
    assert result.source == "test"
    assert len(result.elements) == 2
    assert result.elements[0].content == "Line one"
