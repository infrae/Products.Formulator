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

class DateTimeField(PythonField):
    meta_type = "DateTimeField"

    sub_field_names = PythonField.sub_field_names +\
                      ['text_year', 'text_month', 'text_day',
                       'hour', 'minute']

    text_year = fields.IntegerField('text_year',
                                   title="Year",
                                   required=0,
                                   display_width=4,
                                   display_maxwidth=4,
                                   max_length=4)
    
    text_month = fields.IntegerField('text_month',
                                    title="Month",
                                    required=0,
                                    display_width=2,
                                    display_maxwidth=2,
                                    max_length=2)

    text_day = fields.IntegerField('text_day',
                                   title="Day",
                                   required=0,
                                   display_width=2,
                                   display_maxwidth=2,
                                   max_length=2)

    hour = fields.IntegerField('hour',
                               title="Hour",
                               required=0,
                               display_width=2,
                               display_maxwidth=2,
                               max_length=2)
    
    minute = fields.IntegerField('minute',
                                 title="Minute",
                                 required=0,
                                 display_width=2,
                                 display_maxwidth=2,
                                 max_length=2)

    widget = Widget.DateTimeWidgetInstance
    validator = Validator.DateTimeValidatorInstance
    






