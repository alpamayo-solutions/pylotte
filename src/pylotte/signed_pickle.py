import pickle
from typing import Literal, Optional
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

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
        serializer (module): The serialization module to use (pickle or dill).

    Args:
        public_key_path (str): Path to the PEM-encoded public RSA key.
        private_key_path (str, optional): Path to the PEM-encoded private RSA key (required for signing).
        serializer (Literal["pickle", "dill"], optional): The serialization module to use. Defaults to "pickle".
    """
    def __init__(self, public_key_path: str, private_key_path: Optional[str] = None, serializer: Literal["pickle", "dill"] = "pickle"):
        with open(public_key_path, 'rb') as public_key_file:
            self.public_key = serialization.load_pem_public_key(public_key_file.read())
            self.private_key = None

        if private_key_path is not None:
            with open(private_key_path, 'rb') as private_key_file:
                self.private_key = serialization.load_pem_private_key(private_key_file.read(), password=None)

        if serializer == "dill":
            try:
                import dill
                self.serializer = dill
            except ImportError:
                raise ImportError("dill is not installed. Install it with: pip install pylotte[dill]")
        else:
            self.serializer = pickle

    def dump_and_sign(self, data: object, pickle_path: str, sig_path: str) -> None:
        if self.private_key is None:
            raise ValueError("Private key is required to sign the data.")
        
        with open(pickle_path, 'wb') as file:
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
                return self.serializer.load(file)
        
        except InvalidSignature:
            raise ValueError("Invalid signature!. File may have been tampered")
        