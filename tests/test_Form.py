import unittest, re
import Zope
from DateTime import DateTime

from xml.dom.minidom import parseString

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

    def test_list_items(self):
        self._test_list_items('ListField')

    def test_multi_list_items(self):
        self._test_list_items('MultiListField')
        
    def _test_list_items(self, list_field_type):
        """ test if a list of values returned by TALES (override) expressions
        is interpreted properly.
        If a TALES tab returns a sequence of items and some item is
        actually a string of length 2 (e.g. "ok"), this previously
        has lead to a item text of 'o' and a display value of 'k'
        (as the this is actually a sequence of length 2 ...)
         See http://sourceforge.net/mailarchive/forum.php?thread_id=1359918&forum_id=1702
        """

        self.form.manage_addField('list_field', 'Test List Field', list_field_type)

        self.form.override_test = PythonScript('override_test')
        self.form.override_test.write("return ['ok', 'no']\n")

        list_field = getattr(self.form, 'list_field')
        list_field.values['items'] = [ ('ok', 'ok'), ('no', 'no') ]

        list_field.values['first_item'] = 'on'

        items1 = list_field.render()

        # test TALES
        list_field.tales['items'] = TALESMethod("python:['ok', 'no']")
        items2 = list_field.render()

        # test render
        self.assertEquals(items1, items2)
        # test render_view
        self.assertEquals('ok', list_field.render_view('ok') )
        # test validation ... fake request with a dictionary ...
        list_field.validate({'field_list_field':'ok'})
        
        # test override (most probably superfluous)
        del list_field.tales['items']
        list_field.overrides['items'] = Method('override_test')
        items2 = list_field.render()

        self.assertEquals(items1, items2)

        # missing: if returning a list of int,
        # rendering does work here, but validation fails.
        # maybe it should fail, but on the other hand this is a FAQ on the list ...
        del list_field.overrides['items']
        # test when TALES returns a list of e.g. int
        list_field.values['items'] = [ ('42', '42'), ('88', '88') ]
        
        items1 = list_field.render()
        
        list_field.tales['items'] = TALESMethod("python:[42, 88]")
        items2 = list_field.render()
        
        self.assertEquals(items1, items2)

        list_field.validate({'field_list_field':'42'})


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
        # not to be rendered for DateTime fields

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


    def _helper_render_hidden_datetime(self,expected_values,rendered):
        # heper to check if the generated HTML from render_hidden
        # meets the expectations
        dom = parseString('<dummy>%s</dummy>' % rendered)
        elements = [ child for child in dom.documentElement.childNodes \
                     if child.nodeType == child.ELEMENT_NODE ]
        self.assertEquals(len(expected_values.keys()), len(elements))
        values={}
        for child in elements:
            self.assertEquals('input',child.nodeName)
            self.assertEquals('hidden',child.getAttribute('type'))
            self.failIf(child.childNodes)
            values[child.getAttribute('name')] = child.getAttribute('value')
        self.assertEquals(expected_values, values)

    def _helper_render_hidden_list(self,expected_name, expected_values,
                                   rendered):
        # heper to check if the generated HTML from render_hidden
        # meets the expectations
        dom = parseString('<dummy>%s</dummy>' % rendered)
        elements = [ child for child in dom.documentElement.childNodes \
                     if child.nodeType == child.ELEMENT_NODE ]
        self.assertEquals(len(expected_values), len(elements))
        values={}
        for child in elements:
            self.assertEquals('input',child.nodeName)
            self.assertEquals('hidden',child.getAttribute('type'))
            self.assertEquals(expected_name,child.getAttribute('name'))
            self.assertEquals(expected_values.pop(0),
                              child.getAttribute('value'))
            self.failIf(child.childNodes)



    def test_render_hidden(self):
        # test that rendering fields hidden does produce
        # meaningful results; i.e. such which may still lead to successfull
        # validation when submitting a form with hidden fields
        # this has been broken for DateTimeFields, and fields
        # which allowed multiple values
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('date_time','Test Field','DateTimeField')
        self.form.manage_addProduct['Formulator']\
                  .manage_addField('multi_list','Test Field','MultiListField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('check_boxes','Test Field','MultiCheckBoxField')
        self.form.manage_addProduct['Formulator']\
                  .manage_addField('lines','Test Field','LinesField')

        self.form.date_time.values['default']=DateTime(1970,1,1,)
        self.form.date_time.values['hidden']=1

        expected_values = {
            'subfield_date_time_year'  : '1970',
            'subfield_date_time_month' : '01',
            'subfield_date_time_day'   : '01',
            'subfield_date_time_hour'  : '00',
            'subfield_date_time_minute': '00',
            }
        self._helper_render_hidden_datetime(expected_values,
                                            self.form.date_time.render())

        self.form.date_time.values['date_only']=1
        del expected_values['subfield_date_time_hour']
        del expected_values['subfield_date_time_minute']
        self._helper_render_hidden_datetime(expected_values,
                                            self.form.date_time.render())

        self.form.date_time.values['date_only']=0
        self.form.date_time.values['ampm_time_style']=1
        expected_values['subfield_date_time_hour']='12'
        expected_values['subfield_date_time_minute']='00'
        expected_values['subfield_date_time_ampm']='am'
        self._helper_render_hidden_datetime(expected_values,
                                            self.form.date_time.render())

        self.form.multi_list.values['items'] = (('a','a'),('b','b'), ('c','c'))
        self.form.multi_list.values['default'] = ['a','c']
        self.form.multi_list.values['hidden'] = 1
        self._helper_render_hidden_list('field_multi_list',['a','c'],
                                        self.form.multi_list.render())

        self.form.check_boxes.values['items'] = (('a','a'),('b','b'), ('c','c'))
        self.form.check_boxes.values['default'] = ['a','c']
        self.form.check_boxes.values['hidden'] = 1
        self._helper_render_hidden_list('field_check_boxes',['a','c'],
                                        self.form.check_boxes.render())


        self.form.lines.values['default'] = ['a','c']
        self.form.lines.values['hidden'] = 1
        expect_str = 'a\nc'
        # FIXME: a straight comparision fails ...
        # minidom seems to barf on string linebreaks in attributes (?)
        # instead ...
        rendered = self.form.lines.render()
        rendered = rendered.replace('\n','NEWLINE_HERE')
        expect_str = expect_str.replace('\n','NEWLINE_HERE')
        self._helper_render_hidden_list('field_lines',[expect_str],
                                        rendered)


    def test_render_view_items(self):
        # test that the render_view is correct for fields
        # for which the values internally handled by Formulator
        # are different from the ones shown to the user
        # (e.g. checkboxes, radio buttons, option-lists)

        self.form.manage_addProduct['Formulator']\
                  .manage_addField('single_list','Test Field','ListField')
        self.form.manage_addProduct['Formulator']\
                  .manage_addField('multi_list','Test Field','MultiListField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('check_boxes','Test Field',
                                  'MultiCheckBoxField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('radio','Test Field','RadioField')

        for field in self.form.single_list, self.form.radio:
            field.values['items'] = [ ('Alpha','a'),
                                      ('Beta','b'),
                                      ('Gamma','c'), ]
            self.assertEquals('Gamma',field.render_view('c'),msg=field.id)


        for field in self.form.multi_list, self.form.check_boxes:
            field.values['items'] = [ ('Alpha','a'),
                                      ('Beta','b'),
                                      ('Gamma','c'), ]

            field.values['view_separator'] = '|||'
            self.assertEquals('Gamma',field.render_view(['c']))
            self.assertEquals('|||'.join(('Alpha','Gamma')),
                              field.render_view(['a','c']))
            self.assertEquals('', field.render_view([]))


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(FormTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
