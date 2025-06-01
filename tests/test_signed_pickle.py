import os
import tempfile
import pytest
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from pylotte.signed_pickle import SignedPickle


@pytest.fixture
def rsa_keys():
    # Generate RSA keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    with tempfile.TemporaryDirectory() as tmpdir:
        priv_path = os.path.join(tmpdir, "private.pem")
        pub_path = os.path.join(tmpdir, "public.pem")

        # Write private key
        with open(priv_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Write public key
        with open(pub_path, 'wb') as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        yield pub_path, priv_path  # yield before tempdir is deleted


def test_dump_and_safe_load(rsa_keys):
    pub_path, priv_path = rsa_keys
    sp = SignedPickle(pub_path, priv_path)

    data = {"hello": "world"}

    with tempfile.TemporaryDirectory() as tmpdir:
        pickle_path = os.path.join(tmpdir, "data.pkl")
        sig_path = os.path.join(tmpdir, "data.sig")

        sp.dump_and_sign(data, pickle_path, sig_path)
        assert os.path.exists(pickle_path)
        assert os.path.exists(sig_path)

        result = sp.safe_load(pickle_path, sig_path)
        assert result == data


def test_dump_without_private_key(rsa_keys):
    pub_path, _ = rsa_keys
    sp = SignedPickle(pub_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        pickle_path = os.path.join(tmpdir, "data.pkl")
        sig_path = os.path.join(tmpdir, "data.sig")

        with pytest.raises(ValueError, match="Private key is required"):
            sp.dump_and_sign({"x": 1}, pickle_path, sig_path)


def test_tampered_pickle_file_raises(rsa_keys):
    pub_path, priv_path = rsa_keys
    sp = SignedPickle(pub_path, priv_path)

    data = {"auth": True}

    with tempfile.TemporaryDirectory() as tmpdir:
        pickle_path = os.path.join(tmpdir, "data.pkl")
        sig_path = os.path.join(tmpdir, "data.sig")

        sp.dump_and_sign(data, pickle_path, sig_path)

        # Tamper with the file
        with open(pickle_path, 'wb') as f:
            f.write(b"tampered")

        with pytest.raises(ValueError, match="Invalid signature"):
            sp.safe_load(pickle_path, sig_path)


@pytest.mark.optional
def test_dill_serialization(rsa_keys):
    pub_path, priv_path = rsa_keys
    sp = SignedPickle(pub_path, priv_path, serializer="dill")

    # Test with a lambda function which pickle can't handle but dill can
    data = {"func": lambda x: x * 2}

    with tempfile.TemporaryDirectory() as tmpdir:
        pickle_path = os.path.join(tmpdir, "data.pkl")
        sig_path = os.path.join(tmpdir, "data.sig")

        sp.dump_and_sign(data, pickle_path, sig_path)
        result = sp.safe_load(pickle_path, sig_path)
        
        # Verify the lambda function works
        assert result["func"](5) == 10


def test_dill_not_installed(rsa_keys):
    pub_path, priv_path = rsa_keys
    
    # Mock the import of dill to raise ImportError
    with patch('builtins.__import__', side_effect=ImportError("No module named 'dill'")):
        with pytest.raises(ImportError, match="dill is not installed"):
            SignedPickle(pub_path, priv_path, serializer="dill")
