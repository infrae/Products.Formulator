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
    
