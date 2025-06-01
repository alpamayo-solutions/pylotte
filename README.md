# pylotte

**Secure Pickle Serialization with RSA Signatures**

`pylotte` is a lightweight Python utility that allows you to **securely serialize Python objects with RSA digital signatures**. It ensures the **integrity** and **authenticity** of your data by cryptographically signing serialized files and verifying them before loading.

---

## ✨ Features

- 🔐 Sign serialized files using an RSA **private key**
- ✅ Verify signatures with the corresponding **public key**
- 🛡️ Prevents tampering and ensures data authenticity
- 📦 Simple and minimal interface
- 🔄 Support for both `pickle` and `dill` serialization

---

## 📦 Installation

Install directly from PyPI:

```bash
# Basic installation with pickle support
pip install pylotte

# With dill support for advanced serialization
pip install pylotte[dill]
```

---

## 🛠 Usage

### Basic Usage with Pickle

```python
from pylotte.signed_pickle import SignedPickle

# Initialize with RSA key paths
signer = SignedPickle(public_key_path="public.pem", private_key_path="private.pem")

# Data to serialize
data = {"user": "alice", "role": "admin"}

# Securely dump and sign the pickle file
signer.dump_and_sign(data, "data.pkl", "data.sig")

# Load and verify the signed pickle file
loader = SignedPickle(public_key_path="public.pem")
data_loaded = loader.safe_load("data.pkl", "data.sig")
```

### Advanced Usage with Dill

```python
from pylotte.signed_pickle import SignedPickle

# Initialize with dill serializer
signer = SignedPickle(
    public_key_path="public.pem",
    private_key_path="private.pem",
    serializer="dill"  # Use dill instead of pickle
)

# Complex data with lambda functions
data = {
    "name": "bob",
    "process": lambda x: x * 2,
    "nested": {
        "func": lambda y: y + 1
    }
}

# Save and sign
signer.dump_and_sign(data, "data.pkl", "data.sig")

# Load and verify
loader = SignedPickle(public_key_path="public.pem", serializer="dill")
data_loaded = loader.safe_load("data.pkl", "data.sig")

# Use the loaded lambda functions
result = data_loaded["process"](5)  # Returns 10
```

---

## 🔐 How It Works

- `dump_and_sign()`:

  - Serializes your data (using pickle or dill) and saves it to a file.
  - Signs the file contents using an RSA private key.
  - Stores the signature in a separate `.sig` file.

- `safe_load()`:
  - Reads the serialized file and its signature.
  - Verifies the signature using the RSA public key.
  - If valid, loads and returns the original data.

---

## 🔧 Requirements

- Python 3.9+
- [`cryptography`](https://pypi.org/project/cryptography/)
- [`dill`](https://pypi.org/project/dill/) (optional, for advanced serialization)

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🌐 Links

- 📚 Documentation: [GitHub Repository](https://github.com/alpamayo-solutions/pylotte)
- 🐛 Issue Tracker: [Report Bugs](https://github.com/alpamayo-solutions/pylotte/issues)
- 📦 PyPI: [pylotte on PyPI](https://pypi.org/project/pylotte)

---

## 👤 Author

Developed by [Alpamayo Solutions](mailto:info@alpamayo-solutions.com)
