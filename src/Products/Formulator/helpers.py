# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt
import re

import six

from Acquisition import aq_base


seq_types = [list, tuple]


def ensure_unicode(value, convert=True, encoding='utf-8'):
    if six.PY3 or convert:
        if not isinstance(value, six.text_type):
            if not isinstance(value, six.binary_type):
                value = str(value)
            else:
                value = six.text_type(value, encoding)
    elif isinstance(value, six.text_type):
        value = value.encode(encoding)
    elif not isinstance(value, (six.binary_type, six.text_type)):
        value = str(value).encode(encoding)
    return value


def is_sequence(v):
    return type(aq_base(v)) in seq_types


def convert_unicode(struct, encoding):
    """ convert all strings of a possibly deeply nested structure
    of lists from utf-8 to unicode
    in case of a dictionary only converts the values, not the keys
    """

    if isinstance(struct, six.binary_type):
        return six.text_type(struct, encoding)

    if isinstance(struct, list):
        return [convert_unicode(x, encoding) for x in struct]

    if isinstance(struct, tuple):
        return tuple([convert_unicode(x, encoding) for x in struct])

    if isinstance(struct, dict):
        new_dict = {}
        for k, v in struct.items():
            new_dict[k] = convert_unicode(v, encoding)
        return new_dict

    # if it something else, leave it untouched
    return struct


# for converting (sub)field keys into html ids
key_to_id_re = re.compile(r'([\.\:_ ]+)')
# for pulling the value of an 'id' attribute out of an 'extra' parameter
# this should work for:
# |onclick="blah" id="ASDF"|
# | id =  "ASDF"|
# |ID="ASDF"|
id_value_re = re.compile(
    '^(?:.*\\s)?id(?:\\s*)=(?:\\s*)[\"\'](.*?)[\"\']', re.I)
