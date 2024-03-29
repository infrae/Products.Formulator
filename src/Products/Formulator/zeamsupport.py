# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


import six

import grokcore.component as grok
from zeam.form.base import NO_VALUE
from zeam.form.base import Error
from zeam.form.base import Field
from zeam.form.base import interfaces
from zeam.form.base.markers import getValue
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface import providedBy
from zope.interface.interface import Specification

from Products.Formulator.Errors import ValidationError
from Products.Formulator.interfaces import IForm


def decode(value):
    """Helper to ensure we have unicode everywhere, as Formulator use
    it in an optional fashion.
    """
    if not isinstance(value, six.text_type):
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return six.text_type(value)
    return value


class CustomizedField(object):
    """Proxy around a native Formulator field to be able to
    programmatically change values retrieved with get_value.
    """

    def __init__(self, field, defaults):
        self._field = field
        self._customizations = defaults

    def __getattr__(self, key):
        return getattr(self._field, key)

    def get_value(self, id, **kw):
        if id in self._customizations:
            return self._customizations[id]
        return self._field.get_value(id, **kw)


class IFormulatorField(interfaces.IField):
    meta_type = Attribute(u"Field meta type")

    def customize(customizations):
        """Customization formulator field values.
        """


class IFormulatorWidget(interfaces.IFieldWidget):
    pass


@grok.implementer(IFormulatorField)
class FormulatorField(Field):

    def __init__(self, field, form):
        self._form = form
        self._field = field
        self._customizations = {}
        required = bool(self._getValue('required', False))
        readonly = bool(self._getValue('readonly', False))
        css_class = ['field']
        if required:
            css_class.append('field-required')
        self._customizations['css_class'] = ' '.join(css_class)
        super(FormulatorField, self).__init__(
            identifier=field.id,
            title=decode(field.get_value('title')),
            required=required,
            readonly=readonly)

    def _getValue(self, identifier, default=NO_VALUE):
        if identifier in self._customizations:
            return self._customizations[identifier]
        if identifier in self._field.values:
            return self._field.get_value(identifier)
        return default

    def getDefaultValue(self, form):
        return self._getValue('default')

    @property
    def meta_type(self):
        # Hack for widget.
        return self._field.meta_type

    @property
    def __providedBy__(self):
        # Hack to bind different widgets.
        return Specification(
            (implementedBy(self.__class__), providedBy(self._field)))

    def customize(self, customizations):
        self._customizations.update(customizations)


@grok.implementer(IFormulatorWidget)
class FormulatorWidget(object):
    """Bind a Formulator field to a data.
    """
    order = 0
    alternateLayout = False
    defaultHtmlAttributes = set([])
    defaultHtmlClass = ['field']

    def __init__(self, component, form, request):
        field = component._field.__of__(form.context)
        if component._customizations:
            field = CustomizedField(field, component._customizations)
        self._field = field
        self.component = component
        self.form = form
        self.request = request
        self.identifier = self._field.generate_field_html_id()
        self.title = decode(self._field.get_value('title'))
        self.description = decode(self._field.get_value('description'))
        self.readonly = component.readonly
        self.required = component.required
        self.defaultHtmlClass = [self._field.get_value('css_class')]

    def htmlAttribute(self, name):
        raise NotImplementedError

    def htmlAttributes(self):
        raise NotImplementedError

    def clone(self, new_identifier=None):
        raise NotImplementedError

    @property
    def error(self):
        return self.form.errors.get(self.identifier, None)

    def htmlId(self):
        return self.identifier

    def htmlClass(self):
        result = self.defaultHtmlClass
        if self.required:
            result = result + ['field-required', ]
        return ' '.join(result)

    def isVisible(self):
        return not self._field.get_value('hidden')

    def computeValue(self):
        field = self._field
        if not getValue(self.component, 'ignoreRequest', self.form):
            if 'marker_' + self._key in self.request:
                return field._get_default(self._key, None, self.request)
        if not getValue(self.component, 'ignoreContent', self.form):
            if self.form.getContent() is not None:
                data = self.form.getContentData()
                try:
                    return data.get(self.component.identifier)
                except KeyError:
                    pass
        return field.get_value('default')

    def update(self):
        self._key = self._field.generate_field_key()
        self.value = self.computeValue()

    def render(self):
        field = self._field
        renderer = field.widget.render
        if field.get_value('hidden'):
            renderer = field.widget.render_hidden
        return (decode(renderer(field, self._key, self.value, None)) +
                u' <input type="hidden" value="1" name="%s" />' % (
                'marker_' + self._key))


class FormulatorDisplayWidget(FormulatorWidget):

    def render(self):
        field = self._field
        renderer = field.widget.render_view
        return decode(renderer(field, self.value))


grok.global_adapter(
    FormulatorWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"input")
grok.global_adapter(
    FormulatorWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"hidden")
grok.global_adapter(
    FormulatorDisplayWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"display")


@grok.implementer(interfaces.IWidgetExtractor)
class FormulatorExtractor(grok.MultiAdapter):
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(
        IFormulatorField,
        interfaces.IFieldExtractionValueSetting,
        Interface)

    def __init__(self, component, form, request):
        self._field = component._field.__of__(form.context)
        self.identifier = self._field.generate_field_html_id()
        self.request = request

    def extract(self):
        if not self._field.need_validate(self.request):
            return (NO_VALUE, None)
        try:
            return (self._field.validate(self.request), None)
        except ValidationError as error:
            return (None, Error(error.error_text, self.identifier))

    def extractRaw(self):
        return {}


@grok.implementer(interfaces.IFieldFactory)
class FormulatorFieldFactory(grok.Adapter):
    grok.context(IForm)

    def __init__(self, form):
        self.form = form

    def produce(self):
        for field in self.form.get_fields():
            yield FormulatorField(field, self.form)
