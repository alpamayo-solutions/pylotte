import pickle
import json
import struct
from typing import Optional, Protocol, runtime_checkable, Any, IO
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

@runtime_checkable
class Serializer(Protocol):
    def dump(self, obj: Any, file: IO[bytes]) -> None: ...
    def load(self, file: IO[bytes]) -> Any: ...


class SignedPickle:
    """
    A utility class for securely serializing Python objects with RSA-based digital signatures.

    This class allows you to:
    - Dump data to a file and generate a cryptographic signature using a private RSA key.
    - Verify the signature of the serialized data using a corresponding public RSA key before loading.
    
    This ensures the integrity and authenticity of the serialized data.

    Attributes:
        public_key (RSAPublicKey): The RSA public key used to verify signatures.
        private_key (RSAPrivateKey or None): The RSA private key used to sign data (optional).
        serializer (module): The serialization module/object to use. Must provide dump/load.

    Args:
        public_key_path (str): Path to the PEM-encoded public RSA key.
        private_key_path (str, optional): Path to the PEM-encoded private RSA key (required for signing).
        serializer (Optional[Serializer], optional):
            Any object with compatible dump/load callables. Defaults to None
            which uses the built-in pickle module.
    """
    def __init__(
        self,
        public_key_path: str,
        private_key_path: Optional[str] = None,
        serializer: Optional[Serializer] = None,
    ):
        self._magic = b"PYLOTTE-SP\x01"
        with open(public_key_path, 'rb') as public_key_file:
            self.public_key = serialization.load_pem_public_key(public_key_file.read())
            self.private_key = None

        if private_key_path is not None:
            with open(private_key_path, 'rb') as private_key_file:
                self.private_key = serialization.load_pem_private_key(private_key_file.read(), password=None)

        if serializer is None:
            self.serializer = pickle
        else:
            if not (hasattr(serializer, "dump") and callable(getattr(serializer, "dump", None)) and hasattr(serializer, "load") and callable(getattr(serializer, "load", None))):
                raise TypeError("serializer must provide callable dump and load")
            self.serializer = serializer

    def _serializer_name(self) -> str:
        s = self.serializer
        if s is None:
            return "pickle"
        name = getattr(s, "__name__", None)
        if isinstance(name, str):
            return name
        return f"{s.__class__.__module__}.{s.__class__.__name__}"

    def _write_header(self, file: IO[bytes]) -> None:
        header = {"serializer": {"name": self._serializer_name()}}
        header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
        file.write(self._magic)
        file.write(struct.pack(">I", len(header_bytes)))
        file.write(header_bytes)

    def _read_header(self, file: IO[bytes]) -> tuple[dict, int]:
        start = file.tell()
        magic = file.read(len(self._magic))
        if magic != self._magic:
            file.seek(start)
            return {}, start
        (length,) = struct.unpack(">I", file.read(4))
        header_bytes = file.read(length)
        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except Exception:
            header = {}
        return header, file.tell()

    def dump_and_sign(self, data: object, pickle_path: str, sig_path: str) -> None:
        if self.private_key is None:
            raise ValueError("Private key is required to sign the data.")
        
        with open(pickle_path, 'wb') as file:
            self._write_header(file)
            self.serializer.dump(data, file)
        
        with open(pickle_path, 'rb') as file:
            file_data = file.read()

        signature = self.private_key.sign(
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        with open(sig_path, 'wb') as sig_file:
            sig_file.write(signature)

    def safe_load(self, pickle_path: str, sig_path: str) -> object:
        with open(sig_path, 'rb') as sig_file:
            signature = sig_file.read()

        with open(pickle_path, 'rb') as file:
            file_data = file.read()
        
        try: 
            self.public_key.verify(
                signature,
                file_data, 
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            print("Signature is valid. Loading the data.")

            with open(pickle_path, 'rb') as file:
                _, payload_offset = self._read_header(file)
                file.seek(payload_offset)
                return self.serializer.load(file)
        
        except InvalidSignature:
            raise ValueError("Invalid signature!. File may have been tampered")

    def read_metadata(self, pickle_path: str) -> dict:
        with open(pickle_path, 'rb') as file:
            header, _ = self._read_header(file)
            return header
        