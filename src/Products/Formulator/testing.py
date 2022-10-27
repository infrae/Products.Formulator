# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


import importlib

import plone.testing.zope
from plone.testing.layer import Layer
from plone.testing.zca import ZCMLSandbox
from plone.testing.zope import WSGI_SERVER
from Testing.makerequest import makerequest
from zope.publisher.browser import TestRequest


ZCMLLayer = ZCMLSandbox(
    None, 'Products.Formulator:ZCML', __name__, 'ftesting.zcml',
    importlib.import_module(__name__.replace('.testing', '')))


class FormulatorLayer(Layer):

    defaultBases = (ZCMLLayer, WSGI_SERVER, )

    PRODUCTS = (
        'Products.Formulator',
        'zeam.form.base',
    )

    USERS = {
        'manager': ['Manager'],
    }

    def login(self, username):
        """Login with the given id."""
        userfolder = self['app'].acl_users
        plone.testing.zope.login(userfolder, username)

    def setUp(self):
        with plone.testing.zope.zopeApp(self['zodbDB']) as app:
            for product in self.PRODUCTS:
                plone.testing.zope.installProduct(app, product)
            uf = app.acl_users
            for username, roles in self.USERS.items():
                uf._doAddUser(username, username, roles, [])

    def tearDown(self):
        with plone.testing.zope.zopeApp(self['zodbDB']) as app:
            for product in self.PRODUCTS:
                plone.testing.zope.uninstallProduct(app, product)

    def get_application(self):
        """Return root folder wrapped inside a test request, which is
        the same object you have when you are working on a real
        published request.
        """
        return makerequest(self['app'], environ={'SERVER_NAME': 'localhost'})

    default_users = {
        'manager': ['Manager'],
    }


FunctionalLayer = FormulatorLayer()

__all__ = ['FunctionalLayer', 'TestRequest']
