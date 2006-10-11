from apelib.core.interfaces import ISerializer
from apelib.core.schemas import FieldSchema

from Products.Formulator.Form import ZMIForm
from Products.Formulator.FormToXML import formToXML
from Products.Formulator.XMLToForm import XMLToForm

class FormulatorSerializer:
    __implements__ = ISerializer

    schema = FieldSchema('data', 'string')

    def getSchema(self):
        return self.schema

    def canSerialize(self, object):
        return isinstance(object, ZMIForm)

    def serialize(self, event):
        obj = event.obj
        data = formToXML(obj)
        event.ignore((
            'encoding',
            'stored_encoding',
            'unicode_mode',
            'i18n_domain',
            'groups',
            'group_list',
            'name',
            'action',
            'method',
            'enctype',
            'encoding',
            'stored_encoding',
            'unicode_mode',
            'row_length',
            '_objects'))

        for field in obj.get_fields(include_disabled=True):
            event.ignore(field.getId())

        return data

    def deserialize(self, event, state):
        obj = event.obj
        XMLToForm(state, obj)


