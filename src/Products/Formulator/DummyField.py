# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt
"""
This module contains some magic glue to make it seem as if we
can refer to field classes before they've been defined, through the
'fields' class.

This way, they can be used to create properties on fields.
When the field classes have been defined, get_field()
can be used on FieldProperty objects to get an
actual field object.
"""

from Acquisition import Implicit

from Products.Formulator.FieldRegistry import FieldRegistry


class DummyFieldFactory:

    def __getattr__(self, name):
        return DummyField(name)


fields = DummyFieldFactory()


class DummyField(Implicit):
    def __init__(self, desired_meta_class):
        self.desired_meta_class = desired_meta_class

    def __call__(self, id, **kw):
        self.id = id
        self.kw = kw
        return self

    def get_value(self, name):
        return self.kw.get(name, "")

    def get_real_field(self):
        """Get an actual field for this property.
        """
        field_class = FieldRegistry.get_field_class(self.desired_meta_class)
        return field_class(self.id, **self.kw)
