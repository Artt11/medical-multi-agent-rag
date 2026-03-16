from src.services.data_processor import MedicalProcessor
from src.services.hash_service import BinaryHashService
from src.models.document import MedicalDocument
from src.models.elements import ParsedElement, ElementType


def test_processor_sorts_and_hashes():
    doc = MedicalDocument(source="test")
    elems = [
        ParsedElement(type=ElementType.TEXT, content="b", page=2),
        ParsedElement(type=ElementType.TEXT, content="a", page=1),
    ]
    processor = MedicalProcessor(hasher=BinaryHashService())

    processed = processor.process(doc, elems)

    assert processed.elements[0].content == "a"
    assert processed.hash is not None
