from StringIO import StringIO
from cgi import escape

def formToXML(form, prologue=1):
    """Takes a formulator form and serializes it to an XML representation.
    """
    f = StringIO()
    write = f.write

    if prologue:
        write('<?xml version="1.0" encoding="iso-8859-1"?>\n\n')
    write('<form>\n')
    # export form settings
    # XXX Should we be encoding some text?
    write('  <title>%s</title>\n' % escape(form.title))
    write('  <name>%s</name>\n' % escape(form.name))
    write('  <action>%s</action>\n' % form.action)
    write('  <enctype>%s</enctype>\n' % form.enctype)
    write('  <method>%s</method>\n\n' % form.method)
    # export form groups
    write('  <groups>\n')
    for group in form.get_groups():
        write('    <group>\n')
        write('      <title>%s</title>\n' % escape(group))
        write('      <fields>\n\n')
        for field in form.get_fields_in_group(group):
            write('      <field><id>%s</id> <type>%s</type>\n' % (field.id, field.meta_type))
            write('        <values>\n')
            items = field.values.items()
            items.sort()
            for key, value in items:
                if value is None:
                    continue
                if type(value) == type(1.1):
                    write('          <%s type="float">%s</%s>\n' % (key, escape(str(value)), key))
                if type(value) == type(1):
                    write('          <%s type="int">%s</%s>\n' % (key, escape(str(value)), key))
                elif type(value) == type([]):
                    write('          <%s type="list">%s</%s>\n' % (key, escape(str(value)), key))
                else:
                    write('          <%s>%s</%s>\n' % (key, escape(str(value)), key))
            write('        </values>\n')

            write('        <tales>\n')
            items = field.tales.items()
            items.sort()
            for key, value in items:
                if value:
                    write('          <%s>%s</%s>\n' % (key, escape(str(value._text)), key))
            write('        </tales>\n')

            write('        <messages>\n')
            for message_key in field.get_error_names():
                write('          <message name="%s">%s</message>\n' %
                      (escape(message_key), escape(field.get_error_message(message_key))))
            write('        </messages>\n')
            write('      </field>\n')
        write('      </fields>\n')
        write('    </group>\n')
    write('  </groups>\n')
    write('</form>')

    return f.getvalue()
