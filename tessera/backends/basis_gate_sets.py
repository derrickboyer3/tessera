'''
    Basis Gate Sets
    ---------------
    This is our setup for defining the different backends we have available. Different backends have different basis gate sets.
    Defining those here allows us to create our decomposition maps to break down gates into their basis steps.
'''

# IBM Basis Gate Set
IBM_BASIS_GATES = {"cx", "rz", "sx", "x", "u"}