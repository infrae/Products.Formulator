from Acquisition import aq_base

seq_types = [type([]), type(())]

def is_sequence(v):
    return type(aq_base(v)) in seq_types
