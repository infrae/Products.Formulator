import XMLObjects
from StringIO import StringIO
from cgi import escape
from Products.Formulator.TALESField import TALESMethod

def formToXML(form):
    """Takes a formulator form and serializes it to an XML representation.
    """
    id = form.getId()
    id = id + '.form'

    f = StringIO()
    write = f.write
    
    write('<?xml version="1.0" encoding="iso-8859-1"?>\n\n')
    write('<form>\n')
    # export form settings
    # XXX Should we be encoding some text?
    write('  <title>%s</title>\n' % form.title)
    write('  <name>%s</name>\n' % form.name)
    write('  <action>%s</action>\n' % form.action)
    write('  <enctype>%s</enctype>\n' % form.enctype)
    write('  <method>%s</method>\n\n' % form.method)
    # export form groups
    write('  <groups>\n')
    for group in form.get_groups():
        write('    <group>\n')
        write('      <title>%s</title>\n' % group)
        write('      <fields>\n\n')
        for field in form.get_fields_in_group(group):
            write('      <field><id>%s</id> <type>%s</type>\n' % (field.id, field.meta_type))
            write('        <values>\n')
            for key, value in field.values.items():
                if value is None:
                    continue
                if type(value) == type(1):
                    write('          <%s type="int">%s</%s>\n' % (key, escape(str(value)), key))
                else:
                    write('          <%s>%s</%s>\n' % (key, escape(str(value)), key))
            write('        </values>\n')
            write('        <tales>\n')
            for key, value in field.tales.items():
                if value:
                    write('          <%s>%s</%s>\n' % (key, escape(str(value._text)), key))
            write('        </tales>\n')
            write('      </field>\n')
        write('      </fields>\n')
        write('    </group>\n')
    write('  </groups>\n')
    write('</form>')
    
    return f.getvalue()

class XMLToFormError(Exception):
    pass

def getTextContents(node):
    result = []
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE:
            result.append(child.data)
    return ''.join(result)

def XMLToForm(s, form):
    """Takes an xml string and changes formulator form accordingly.
    Heavily inspired by code from Nikolay Kim.
    """
    top = XMLObjects.XMLToObjectsFromString(s)
    # wipe out groups
    form.groups = {'Default':[]}
    form.group_list = ['Default']

    #  get the settings
    settings = ['title', 'name', 'action', 'enctype', 'method']
    for setting in settings:
        value = getattr(top.first.form.first, setting, None)
        if value is None:
            continue
        setattr(form, setting, value.text.encode('latin1')) 

    # create groups
    has_default = 0
    for group in top.first.form.first.groups.elements.group:
        # get group title and create group
        group_title = group.first.title.text.encode('latin1')
        if group_title == 'Default':
            has_default = 1
        form.add_group(group_title)
        # create fields in group
        for entry in group.first.fields.elements.field:
            id = entry.first.id.text.encode('latin1')
            meta_type = entry.first.type.text.encode('latin1')
            form.manage_addField(id, '', meta_type)
            field = form._getOb(id)
            if group_title != 'Default':
                form.move_field_group([id], 'Default', group_title)
            # set values
            values = entry.first.values
            for name in values.getElementNames():
                value = getattr(values.first, name)
                if value.attributes.get('type') == 'int':
                    field.values[name] = int(value.text)
                else:
                    field.values[name] = value.text.encode('latin1')
            # set tales
            tales = entry.first.tales
            for name in tales.getElementNames():
                field.tales[name] = TALESMethod(
                    getattr(tales.first, name).text.encode('latin1'))
            # for persistence machinery
            field.values = field.values
            field.tales = field.tales
        
    # delete default group
    if not has_default:
        form.move_group_down('Default')
        form.remove_group('Default')
    
