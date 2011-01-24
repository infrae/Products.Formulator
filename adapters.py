# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface
from zope.component import queryMultiAdapter

from Products.Formulator import interfaces
from Products.Formulator.Errors import FormValidationError

_marker = object()


class FieldValueWriter(grok.MultiAdapter):
    grok.provides(interfaces.IFieldValueWriter)
    grok.implements(interfaces.IFieldValueWriter)
    grok.adapts(interfaces.IField, Interface)

    def __init__(self, field, form):
        self._field = field
        self._content = form.get_content()

    def __call__(self, value):
        self._content.__dict__[self._field.id] = value


class FieldValueReader(grok.MultiAdapter):
    grok.provides(interfaces.IFieldValueReader)
    grok.implements(interfaces.IFieldValueReader)
    grok.adapts(interfaces.IField, Interface)

    def __init__(self, field, form):
        self._field = field
        self._content = form.get_content()

    def __call__(self):
        return self._content.__dict__.get(self._field.id, _marker)


class BindedField(object):
    grok.implements(interfaces.IBindedField)

    def __init__(self, field, value):
        self._field = field
        self._value = value
        self.id = field.generate_field_html_id()
        self.title = field.get_value('title')
        self.description = field.get_value('description')
        self.required = field.get_value('required') and True

    def __call__(self):
        return self._field.render(self._value)


class BindedForm(grok.MultiAdapter):
    grok.implements(interfaces.IBindedForm)
    grok.provides(interfaces.IBindedForm)
    grok.adapts(interfaces.IForm, Interface, Interface)

    def __init__(self, form, request, context):
        self.form = form
        self.request = request
        self.context = context
        self.__content = None
        self.__values = None

    def set_content(self, content):
        self.__content = content

    def get_content(self):
        if self.__content is not None:
            return self.__content
        return self.context

    def fields(self, ignoreContent=True, ignoreRequest=True):
        values = {}
        if not ignoreRequest:
            values = self.extract()
        elif not ignoreContent:
            values = self.read()
        for field in self.form.get_fields():
            yield BindedField(field, values.get(field.id, None))

    def validate(self):
        try:
            self.__values = self.form.validate_all(self.request)
        except FormValidationError as failure:
            raise ValueError(failure.errors)
        return True

    def extract(self):
        if self.__values is None:
            self.validate()
        return self.__values

    def read(self):
        values = {}
        for field in self.form.get_fields():
            reader = queryMultiAdapter(
                (field, self), interfaces.IFieldValueReader)
            value = reader()
            if value is _marker:
                value = field.get_value('default')
            # Do we handle alternate names ?
            values[field.id] = value
        return values

    def save(self):
        values = self.extract()
        for field in self.form.get_fields():
            value = values.get(field.id, _marker)
            if value is not _marker:
                writer = queryMultiAdapter(
                    (field, self), interfaces.IFieldValueWriter)
                writer(value)

