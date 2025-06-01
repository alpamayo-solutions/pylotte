from pylotte.signed_pickle import SignedPickle

def create_keys():
    """Create RSA key pair for demonstration."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Save private key
    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save public key
    with open("public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def pickle_example():
    """Example using standard pickle serialization."""
    print("\n=== Pickle Example ===")
    
    # Initialize with pickle (default)
    signer = SignedPickle("public.pem", "private.pem")
    
    # Simple data that pickle can handle
    data = {
        "name": "Alice",
        "age": 30,
        "roles": ["admin", "user"]
    }
    
    # Save and sign
    signer.dump_and_sign(data, "data_pickle.pkl", "data_pickle.sig")
    print("✓ Data saved and signed with pickle")
    
    # Load and verify
    loader = SignedPickle("public.pem")
    loaded_data = loader.safe_load("data_pickle.pkl", "data_pickle.sig")
    print("✓ Data loaded and verified")
    print(f"Loaded data: {loaded_data}")

def dill_example():
    """Example using dill serialization for more complex objects."""
    print("\n=== Dill Example ===")
    
    try:
        # Initialize with dill
        signer = SignedPickle("public.pem", "private.pem", serializer="dill")
        
        # Complex data that only dill can handle
        data = {
            "name": "Bob",
            "age": 25,
            "roles": ["user"],
            "process": lambda x: x * 2,  # Lambda function
            "nested": {
                "func": lambda y: y + 1  # Nested lambda
            }
        }
        
        # Save and sign
        signer.dump_and_sign(data, "data_dill.pkl", "data_dill.sig")
        print("✓ Data saved and signed with dill")
        
        # Load and verify
        loader = SignedPickle("public.pem", serializer="dill")
        loaded_data = loader.safe_load("data_dill.pkl", "data_dill.sig")
        print("✓ Data loaded and verified")
        
        # Test the loaded lambda functions
        print(f"Lambda test (2 * 5): {loaded_data['process'](5)}")
        print(f"Nested lambda test (3 + 1): {loaded_data['nested']['func'](3)}")
        
    except ImportError:
        print("❌ Dill not installed. Install with: pip install pylotte[dill]")

if __name__ == "__main__":
    # Create RSA keys for the examples
    create_keys()
    
    # Run examples
    pickle_example()
    dill_example() 