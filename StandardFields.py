from Field import PythonField
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

class TextAreaField(PythonField):
    meta_type = "TextAreaField"

    widget = Widget.TextAreaWidgetInstance
    validator = Validator.TextValidatorInstance
    
class ListField(PythonField):
    meta_type = "ListField"

    widget = Widget.ListWidgetInstance
    validator = Validator.SelectionValidatorInstance









