from Acquisition import aq_base

seq_types = [type([]), type(())]

def is_sequence(v):
    return type(aq_base(v)) in seq_types

def convert_unicode(struct):
    """ convert all strings of a possibly deeply nested structure
    of lists from utf-8 to unicode
    in case of a dictionary only converts the values, not the keys
    """

    if type(struct) == type(''):
        return unicode(struct, 'utf-8')

    if type(struct) == type([]):
        return map( convert_unicode, struct )

    if type(struct) == type(()):
        return tuple( map( convert_unicode, struct ) )

    if type(struct) == type({}):
        new_dict = {}
        for k,v in struct.items():
            new_dict[k] = convert_unicode(v)
        return new_dict
