import unittest
import Zope
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLSerialize import XMLToForm, formToXML

class SerializeTestCase(unittest.TestCase):
    def test_simpleSerialize(self):
        form = ZMIForm('test', 'My test')
        xml = '''\
<?xml version="1.0" encoding="iso-8859-1" ?>

<form>
  <title></title>
  <name>tab_status_form</name>
  <action></action>
  <enctype></enctype>
  <method></method>

  <groups>
    <group>
      <title>Default</title>
      <fields>

      <field><id>message</id> <type>RawTextAreaField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <max_length></max_length>
          <width type="int">65</width>
          <external_validator></external_validator>
          <height type="int">7</height>
          <required type="int">0</required>
          <css_class></css_class>
          <default></default>
          <title>Message</title>
          <truncate type="int">0</truncate>
          <description></description>
          <extra>wrap="soft"</extra>
        </values>
        <tales>
        </tales>
      </field>
      <field><id>publish_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <css_class></css_class>
          <title>Publish time</title>
          <description></description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expiration_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <css_class></css_class>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <title>Expiration time</title>
          <description>If this document should expire, set the time.</description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expires_flag</id> <type>CheckBoxField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <css_class></css_class>
          <default type="int">0</default>
          <title>Expire flag</title>
          <description>Turn on expiration time?</description>
          <external_validator></external_validator>
          <extra></extra>
        </values>
        <tales>
        </tales>
      </field>
      </fields>
    </group>
  </groups>
</form>'''
        XMLToForm(xml, form)
        s = formToXML(form)
        f = open('output1.txt', 'w')
        f.write(s)
        f.close()
        form2 = ZMIForm('another', 'Something')
        XMLToForm(xml, form2)
        f = open('output2.txt', 'w')
        f.write(formToXML(form2))
        f.close()
        
def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(SerializeTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
