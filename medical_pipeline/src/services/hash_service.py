import hashlib
from typing import Union


class BinaryHashService:
    def hash_bytes(self, data: Union[bytes, bytearray]) -> str:
        digest = hashlib.sha256()
        digest.update(data)
        return digest.hexdigest()
