# pylotte

**Secure Pickle Serialization with RSA Signatures**

`pylotte` is a lightweight Python utility that allows you to **securely serialize (pickle) Python objects with RSA digital signatures**. It ensures the **integrity** and **authenticity** of your data by cryptographically signing pickled files and verifying them before loading.

---

## ✨ Features

- 🔐 Sign pickle files using an RSA **private key**
- ✅ Verify signatures with the corresponding **public key**
- 🛡️ Prevents tampering and ensures data authenticity
- 📦 Simple and minimal interface

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install pylotte
```

---

## 🛠 Usage

```python
from pylotte import SignedPickle

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

---

## 🔐 How It Works

- `dump_and_sign()`:
  - Pickles your data and saves it to a file.
  - Signs the file contents using an RSA private key.
  - Stores the signature in a separate `.sig` file.

- `safe_load()`:
  - Reads the pickled file and its signature.
  - Verifies the signature using the RSA public key.
  - If valid, loads and returns the original data.

---

## 🔧 Requirements

- Python 3.9+
- [`cryptography`](https://pypi.org/project/cryptography/)

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
