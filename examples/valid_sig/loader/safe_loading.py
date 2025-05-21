from pylotte.signed_pickle import SignedPickle

"""
This is the perspective of a person that wants to safely load the data. We assume that 
the public key is available as a file and that the files he wants to verify are in his
directory. Execute this file to verify the signature of data.pkl.
"""

safe_pickler = SignedPickle('example_public_key.pem')
pickled_data = safe_pickler.safe_load('data.pkl', 'data.pkl.sig')

if pickled_data is not None:
    print(pickled_data)