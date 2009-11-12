import re

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

    # if it something else, leave it untouched
    return struct

#for converting (sub)field keys into html ids
key_to_id_re = re.compile('([\.\:_ ]+)')
# for pulling the value of an 'id' attribute out of an 'extra' parameter
# this should work for:
# |onclick="blah" id="ASDF"|
# | id =  "ASDF"|
# |ID="ASDF"|
id_value_re = re.compile('^(?:.*\s)?id(?:\s*)=(?:\s*)[\"\'](.*?)[\"\']', re.I)