import unittest
import Zope

# XXX this does not work for zope2.x if x < 3
# can we fake this? should we do this?
from Testing import makerequest

from Products.Formulator.Form import ZMIForm
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Formulator.MethodField import Method
from Products.Formulator.TALESField import TALESMethod

from Products.PythonScripts.PythonScript import PythonScript


""" random assembly testing some reported bugs.
    This is _not_ a structured or even complete test suite
"""

class FormTestCase(unittest.TestCase):

    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(self.connection.root()['Application'])

        self.root.manage_addProduct['Formulator'].manage_add('form', 'Test Form')
        self.form = self.root.form


    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        

    def test_has_field(self):
        """ test if has_field works, if one asks for a non-field attribute.
            this has raised AttributeError "aq_explicit" in previous versions
        """
        self.failIf(self.form.has_field('title'))

    def _test_list_values(self):
        """ test if a list of values returned by TALES (override) expressions is interpreted properly.
        If a TALES tab returns a sequence of items and some item is
        actually a string of length 2 (e.g. "ok"), this previously
        has lead to a item text of 'o' and a display value of 'k'
        (as the this is actually a sequence of length 2 ...)
         See http://sourceforge.net/mailarchive/forum.php?thread_id=1359918&forum_id=1702
         
        Actually the original problem still does not work,
        as passing a list of int's is not yet supported.
        If it should, please uncomment the second part of the test.
        """

        # XXX deactivated: this maybe should not be fixed at all

        self.form.manage_addField('list_field', 'Test List Field', 'ListField')

        # adding a python script to be called by the override tab
        # FIXME: the following does not work, as the fake-request
        # does not have a "form" atribute (?)
        #self.root.manage_addProduct['PythonScripts'] \
        #         .manage_addPythonScript('override_test', 'Test for override')
        #
        #self.root._getOb('override_test').write("return ['ok', 'no']\n")

        self.form.override_test = PythonScript('override_test')
        self.form.override_test.write("return ['ok', 'no']\n")
        # ps._makeFunction()

        
        list_field = getattr(self.form, 'list_field')
        list_field.values['items'] = [ ('ok', 'ok'), ('no', 'no') ]

        items1 = list_field.render()

        # test TALES
        list_field.tales['items'] = TALESMethod("python:['ok', 'no']")
        items2 = list_field.render()

        self.assertEquals(items1, items2)

        # test override
        del list_field.tales['items']
        list_field.overrides['items'] = Method('override_test')
        items2 = list_field.render()
        
        self.assertEquals(items1, items2)
        
        # test if TALES returns a list of e.g. int
        #list_field.values['items'] = [ ('42', '42'), ('88', '88') ]
        #
        #items1 = list_field.render()
        #
        #list_field.tales['items'] = TALESMethod("python:[42, 88]")
        #items2 = list_field.render()
        #
        #self.assertEquals(items1, items2)

    def test_labels(self):
        self.form.manage_addField(
            'label_field', 'Test Label Field', 'LabelField')

        self.form.label_field.overrides['default'] = "Some label"

        self.form.manage_addField(
            'int_field', 'Test integer field', 'IntegerField')

        result = self.form.validate_all(
            {'field_int_field': '3'})
        self.assertEquals({'int_field': 3}, result)

        
def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(FormTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
