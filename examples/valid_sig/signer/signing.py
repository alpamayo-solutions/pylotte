from task import Task
from pylotte.signed_pickle import SignedPickle 

"""
This is the perspective of a person that signs the file. We assume that the public and
private key are available. Execute this file to create data.pkl and data.pkl.sig that is
then supposed to be sent to the person that loads the data.
"""

tasks = [
    Task("Create a prototype", completed=True),
    Task("Test the prototype",  completed=False),
    Task("Integrate into system", completed=False)
]

safe_pickler = SignedPickle('example_public_key.pem', 'example_private_key.pem')
safe_pickler.dump_and_sign(tasks, 'data.pkl', 'data.pkl.sig')