# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt
try:
    from html import escape
except ImportError:
    from cgi import escape  # PY2

import six
from six import StringIO

from DateTime import DateTime
from zope.interface.interfaces import IInterface


def formToXML(form, prologue=1):
    """Takes a formulator form and serializes it to an XML representation.
    """
    f = StringIO()
    write = f.write

    if prologue:
        write('<?xml version="1.0"?>\n\n')
    write('<form>\n')
    # export form settings
    for field in form.settings_form.get_fields(include_disabled=1):
        id = field.id
        value = getattr(form, id)
        if id == 'title':
            value = escape(value)
        if id == 'unicode_mode':
            if value:
                value = 'true'
            else:
                value = 'false'
        write('  <%s>%s</%s>\n' % (id, value, id))
    # export form groups
    write('  <groups>\n')
    for group in form.get_groups(include_empty=1):
        write('    <group>\n')
        write('      <title>%s</title>\n' % escape(group))
        write('      <fields>\n\n')
        for field in form.get_fields_in_group(group, include_disabled=1):
            write('      <field><id>%s</id> <type>%s</type>\n' %
                  (field.id, field.meta_type))
            write('        <values>\n')
            items = sorted(field.values.items())
            for key, value in items:
                if value is None:
                    continue
                # convert boolean to int
                if isinstance(value, bool):
                    value = value and 1 or 0
                if isinstance(value, float):
                    write('          <%s type="float">%s</%s>\n' %
                          (key, escape(str(value)), key))
                if isinstance(value, int):
                    write('          <%s type="int">%s</%s>\n' %
                          (key, escape(str(value)), key))
                elif isinstance(value, list):
                    write('          <%s type="list">%s</%s>\n' %
                          (key, escape(str(value)), key))
                elif IInterface.providedBy(value):
                    write('          <%s type="interface">%s</%s>\n' %
                          (key, value.__identifier__, key))
                elif callable(value):
                    write('          <%s type="method">%s</%s>\n' %
                          (key, escape(str(value.method_name)), key))
                elif isinstance(value, DateTime):
                    write('          <%s type="datetime">%s</%s>\n' %
                          (key, escape(str(value)), key))
                else:
                    if not isinstance(
                            value, (six.binary_type, six.text_type)):
                        value = str(value)
                    write('          <%s>%s</%s>\n'
                          % (key, escape(value), key))
            write('        </values>\n')

            write('        <tales>\n')
            items = sorted(field.tales.items())
            for key, value in items:
                if value:
                    write('          <%s>%s</%s>\n' %
                          (key, escape(str(value._text)), key))
            write('        </tales>\n')

            write('        <messages>\n')
            for message_key in field.get_error_names():
                # get message text, don't want a MessageId as we
                # don't want to trigger translation in serialization
                message_text = field.get_error_message(message_key,
                                                       want_message_id=False)
                message_text = escape(message_text)
                message_key = escape(message_key)
                # we don't want unicode here
                if not form.unicode_mode:
                    if six.PY2 and isinstance(message_text, six.text_type):
                        message_text = message_text.encode(
                            form.stored_encoding)
                write('          <message name="%s">%s</message>\n' %
                      (message_key, message_text))
            write('        </messages>\n')
            write('      </field>\n')
        write('      </fields>\n')
        write('    </group>\n')
    write('  </groups>\n')
    write('</form>')

    if six.PY3:
        return f.getvalue()
    elif form.unicode_mode:
        return f.getvalue().encode('UTF-8')
    return six.text_type(f.getvalue(), form.stored_encoding).encode('UTF-8')
