from Field import PythonField
from DummyField import fields
import Validator, Widget
import OFS

class StringField(PythonField):
    meta_type = "StringField"
    
    widget = Widget.TextWidgetInstance
    validator = Validator.StringValidatorInstance

class PasswordField(PythonField):
    meta_type = "PasswordField"

    widget = Widget.PasswordWidgetInstance
    validator = Validator.StringValidatorInstance

class EmailField(PythonField):
    meta_type = "EmailField"

    widget = Widget.TextWidgetInstance
    validator = Validator.EmailValidatorInstance
    
class CheckBoxField(PythonField):
    meta_type = "CheckBoxField"

    widget = Widget.CheckBoxWidgetInstance
    validator = Validator.BooleanValidatorInstance
        
class IntegerField(PythonField):
    meta_type = "IntegerField"

    widget = Widget.TextWidgetInstance
    validator = Validator.IntegerValidatorInstance

class RangedIntegerField(PythonField):
    meta_type = "RangedIntegerField"

    widget = Widget.TextWidgetInstance
    validator = Validator.RangedIntegerValidatorInstance

class FloatField(PythonField):
    meta_type = "FloatField"

    widget = Widget.TextWidgetInstance
    validator = Validator.FloatValidatorInstance
    
class TextAreaField(PythonField):
    meta_type = "TextAreaField"

    widget = Widget.TextAreaWidgetInstance
    validator = Validator.TextValidatorInstance
    
class ListField(PythonField):
    meta_type = "ListField"

    widget = Widget.ListWidgetInstance
    validator = Validator.SelectionValidatorInstance

class TestField(PythonField):
    meta_type = "TestField"

    sub_field_names = PythonField.sub_field_names +\
                      ['first_field', 'second_field']
    
    first_field = fields.StringField('first_field',
                                     title="First field",
                                     required=0,
                                     display_width=5)

    second_field = fields.StringField('second_field',
                                      title="Second field",
                                      required=0,
                                      display_width=5)

    widget = Widget.TestWidgetInstance
    validator = Validator.TestValidatorInstance
    






