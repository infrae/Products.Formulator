import XMLObjects
from Products.Formulator.TALESField import TALESMethod

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
        if not hasattr(group.first.fields.elements, 'field'):
            # empty <fields> element
            continue
        for entry in group.first.fields.elements.field:
            id = entry.first.id.text.encode('latin1')
            meta_type = entry.first.type.text.encode('latin1')
            try:
                form._delObject(id)
            except (KeyError, AttributeError):
                pass
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
                elif value.attributes.get('type') == 'list':
                    # XXX bare eval here (this may be a security leak ?)
                    field.values[name] = eval(value.text.encode('latin1'))
                else:
                    field.values[name] = value.text.encode('latin1')

            # special hack for the DateTimeField
            if field.meta_type=='DateTimeField':
                field.on_value_input_style_changed(field.get_value('input_style'))

            # set tales
            tales = entry.first.tales
            for name in tales.getElementNames():
                field.tales[name] = TALESMethod(
                    getattr(tales.first, name).text.encode('latin1'))

            # set messages
            if hasattr(entry.first, 'messages'):
                messages = entry.first.messages
                for entry in messages.elements.message:
                    name = entry.attributes.get('name')
                    text = entry.text.encode('latin1')
                    field.message_values[name] = text

            # for persistence machinery
            field.values = field.values
            field.tales = field.tales
            field.message_values = field.message_values
        
    # delete default group
    if not has_default:
        form.move_group_down('Default')
        form.remove_group('Default')
    
