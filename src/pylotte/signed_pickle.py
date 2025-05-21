import pickle
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

class SignedPickle:
    """
    A utility class for securely serializing (pickling) Python objects with RSA-based digital signatures.

    This class allows you to:
    - Dump (pickle) data to a file and generate a cryptographic signature using a private RSA key.
    - Verify the signature of the pickled data using a corresponding public RSA key before unpickling.
    
    This ensures the integrity and authenticity of the serialized data.

    Attributes:
        public_key (RSAPublicKey): The RSA public key used to verify signatures.
        private_key (RSAPrivateKey or None): The RSA private key used to sign data (optional).

    Args:
        public_key_path (str): Path to the PEM-encoded public RSA key.
        private_key_path (str, optional): Path to the PEM-encoded private RSA key (required for signing).

    Methods:
        dump_and_sign(data, pickle_path, sig_path):
            Pickles the given data to `pickle_path` and writes its digital signature to `sig_path`.

        safe_load(pickle_path, sig_path):
            Verifies the digital signature at `sig_path` and returns the unpickled data if valid.
    """
    def __init__(self, public_key_path: str, private_key_path: str = None):
        with open(public_key_path, 'rb') as public_key_file:
            self.public_key = serialization.load_pem_public_key(public_key_file.read())
            self.private_key = None

        if private_key_path is not None:
            with open(private_key_path, 'rb') as private_key_file:
                self.private_key = serialization.load_pem_private_key(private_key_file.read(), password=None)

    def dump_and_sign(self, data: object, pickle_path: str, sig_path: str) -> None:
        if self.private_key is None:
            raise ValueError("Private key is required to sign the data.")
        
        # Pickle the data
        with open(pickle_path, 'wb') as file:
            pickle.dump(data, file)
        
        # Open the file and sign the data
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

        # Save the signature to a file
        with open(sig_path, 'wb') as sig_file:
            sig_file.write(signature)

    def safe_load(self, pickle_path: str, sig_path: str) -> object:
        # Load the data and signature:
        with open(sig_path, 'rb') as sig_file:
            signature = sig_file.read()

        with open(pickle_path, 'rb') as file:
            file_data = file.read()
        
        # Verify the signature:
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
                return pickle.load(file)
        
        except InvalidSignature:
            raise ValueError("Invalid signature!. File may have been tampered")
        