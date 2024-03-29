# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import Acquisition
from Persistence import Persistent
from Products.PageTemplates.Expressions import getEngine

from Products.Formulator import Validator
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator.Field import ZMIField


class TALESWidget(Widget.TextWidget):
    default = fields.MethodField('default',
                                 title='Default',
                                 default="",
                                 required=0)

    def render(self, field, key, value, REQUEST):
        if value is None:
            text = field.get_value('default')
        else:
            if value != "":
                text = value._text
            else:
                text = ""
        return Widget.TextWidget.render(self, field, key, text, REQUEST)


class TALESMethod(Persistent, Acquisition.Implicit):
    """A method object; calls method name in acquisition context.
    """

    def __init__(self, text):
        self._text = text

    def __call__(self, **kw):
        expr = getattr(self, '_v_expr', None)
        if expr is None:
            self._v_expr = expr = getEngine().compile(self._text)
        return getEngine().getContext(kw).evaluate(expr)

        # check if we have 'View' permission for this method
        # (raises error if not)
        # getSecurityManager().checkPermission('View', method)


class TALESValidator(Validator.StringBaseValidator):

    def validate(self, field, key, REQUEST):
        value = Validator.StringBaseValidator.validate(
            self, field, key, REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        return TALESMethod(value)


TALESWidgetInstance = TALESWidget()
TALESValidatorInstance = TALESValidator()


class TALESField(ZMIField):
    meta_type = 'TALESField'

    internal_field = 1

    widget = TALESWidgetInstance
    validator = TALESValidatorInstance
