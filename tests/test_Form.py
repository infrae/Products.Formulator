import unittest, re
import Zope
from DateTime import DateTime

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
        # XXX compatibility with 2.7: the following does not work any longer
        # self.connection = Zope.DB.open()
        # instead do it ugly:
        self.connection = Zope.app()._p_jar
        self.root = makerequest.makerequest(
            self.connection.root()['Application'])

        self.root.manage_addProduct['Formulator'] \
                 .manage_add('form', 'Test Form')
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
        """ test if a list of values returned by TALES (override) expressions
        is interpreted properly.
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


    def test_datetime_css_class_rendering(self):
        # test that a bug is fixed, which causing the css_class value
        # not to be rendered
        
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('date_time','Test Field','DateTimeField')
        field = self.form.date_time
        
        css_matcher = re.compile('class="([^"]*)"')

        # initially no css class is set
        self.assertEquals(0, len(css_matcher.findall(field.render())))

        # edit the field, bypassing validation ... 
        field._edit({'css_class':'some_class'})

        # now we should have five matches for the five subfields ...
        css_matches = css_matcher.findall(field.render())
        self.assertEquals(5, len(css_matches))
        # ... and all have the given value:
        for m in css_matches:
            self.assertEquals('some_class',m)

        # change the input style: the css needs to be
        # propagated to the newly created subfields
        current_style = field['input_style']
        other_style = {'list':'text', 'text':'list'} [current_style]
        field._edit({'input_style':other_style})
        
        # still the css classes should remain the same
        css_matches = css_matcher.findall(field.render())
        self.assertEquals(5, len(css_matches))
        for m in css_matches:
            self.assertEquals('some_class',m)

        # now just change to another value:
        field._edit({'css_class':'other_class'})
        css_matches = css_matcher.findall(field.render())
        self.assertEquals(5, len(css_matches))
        for m in css_matches:
            self.assertEquals('other_class',m)           

        # and clear the css_class field:
        field._edit({'css_class':''})
        css_matches = css_matcher.findall(field.render())
        self.assertEquals(0, len(css_matches))


    def test_renderHidden(self):
        # test that rendering fields hidden does produce
        # meaningful results; i.e. such which may still lead to successfull
        # validation when submitting a form with hidden fields
        # this has been broken for DateTimeFields, and fields
        # which allowed multiple values
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('date_time','Test Field','DateTimeField')
        self.form.manage_addProduct['Formulator']\
                  .manage_addField('multi_list','Test Field','MultiCheckBoxField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('check_boxes','Test Field','MultiListField')
        self.form.manage_addProduct['Formulator']\
                  .manage_addField('lines','Test Field','LinesField')

        self.form.date_time.values['default']=DateTime(1970,1,1,)
        self.form.date_time.values['hidden']=1
        
        # FIXME: compare result agains a fixed string
        # this may break even if the tested feature is intact
        # for example it breaks with python 2.3.2, as this causes
        # a different sorting on the attributes :-/
        # however I am definitely too lazy to parse and compare this properly
        hidden_datetime_expected = [
            '<input value="1970" name="subfield_date_time_year" type="hidden"  />',
            '<input value="01" name="subfield_date_time_month" type="hidden"  />',
            '<input value="01" name="subfield_date_time_day" type="hidden"  />',
            '<input value="00" name="subfield_date_time_hour" type="hidden"  />',
            '<input value="00" name="subfield_date_time_minute" type="hidden"  />',
            '<input value="am" name="subfield_date_time_ampm" type="hidden"  />'
            ]

        self.assertEquals(''.join(hidden_datetime_expected[:5]),
                          self.form.date_time.render())

        self.form.date_time.values['date_only']=1
        self.assertEquals(''.join(hidden_datetime_expected[:3]),
                          self.form.date_time.render())
        
        self.form.date_time.values['date_only']=0
        self.form.date_time.values['ampm_time_style']=1
        hidden_datetime_expected[3] = \
           '<input value="12" name="subfield_date_time_hour" type="hidden"  />'
        self.assertEquals(''.join(hidden_datetime_expected),
                          self.form.date_time.render())
        

        self.form.multi_list.values['items'] = (('a','a'),('b','b'), ('c','c'))
        self.form.multi_list.values['default'] = ['a','c']
        self.form.multi_list.values['hidden'] = 1

        hidden_multilist_expected = [
            '<input value="a" name="field_multi_list" type="hidden"  />',
            '<input value="c" name="field_multi_list" type="hidden"  />',
            ]
        
        self.assertEquals(''.join(hidden_multilist_expected),
                          self.form.multi_list.render())

        self.form.check_boxes.values['items'] = (('a','a'),('b','b'), ('c','c'))
        self.form.check_boxes.values['default'] = ['a','c']
        self.form.check_boxes.values['hidden'] = 1

        hidden_checkboxes_expected = \
           [ s.replace('multi_list','check_boxes') \
             for s in hidden_multilist_expected ]
        self.assertEquals(''.join(hidden_checkboxes_expected),
                          self.form.check_boxes.render())

        self.form.lines.values['default'] = ['a','c']
        self.form.lines.values['hidden'] = 1

        hidden_lines_expected = '''<input value="a
c" name="field_lines" type="hidden"  />'''
        self.assertEquals(hidden_lines_expected,
                          self.form.lines.render())

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(FormTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
