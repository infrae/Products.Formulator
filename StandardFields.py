from Form import BasicForm
from Field import PythonField
from DummyField import fields
from MethodField import Method
from DateTime import DateTime
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

    # this field is not addable anymore and deprecated. For
    # backwards compatibility it's a clone of IntegerField,
    # though it may go away in the future.
    internal_field = 1 
    
    widget = Widget.TextWidgetInstance
    validator = Validator.IntegerValidatorInstance

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

class RadioField(PythonField):
    meta_type = "RadioField"

    widget = Widget.RadioWidgetInstance
    validator = Validator.SelectionValidatorInstance

class HaxorMethod(Method):
    def __init__(self, field, method_name):
        HaxorMethod.inheritedAttribute('__init__')(self, method_name)
        self.field = field
        
        
    def __call__(self, *arg, **kw):
        method = getattr(self.field, self.method_name)
        return apply(method, arg, kw)
    
class DateTimeField(PythonField):
    meta_type = "DateTimeField"

    widget = Widget.DateTimeWidgetInstance
    validator = Validator.DateTimeValidatorInstance

    def __init__(self, id, **kw):
        # icky but necessary...
        apply(PythonField.__init__, (self, id), kw)
        
        self.sub_form = create_datetime_text_sub_form()

    def on_value_input_style_changed(self, value):
        if value == 'text':
            self.sub_form = create_datetime_text_sub_form()
        elif value == 'list':
            self.sub_form = create_datetime_list_sub_form()
            year_field = self.sub_form.get_field('year')
            year_field.overrides['items'] = HaxorMethod(self,
                                                        'override_year_items')
        else:
            assert 0, "Unknown input_style."
    
    def override_year_items(self):
        """The method gets called to get the right amount of years.
        """
        start_datetime = self.get_value('start_datetime')
        end_datetime = self.get_value('end_datetime')
        current_year = DateTime().year()
        if start_datetime:
            first_year = start_datetime.year()
        else:
            first_year = current_year
        if end_datetime:
            last_year = end_datetime.year() + 1
        else:
            last_year = first_year + 11
        return create_items(first_year, last_year)
            
def create_datetime_text_sub_form():
    sub_form = BasicForm()
        
    year = IntegerField('year',
                        title="Year",
                        required=0,
                        display_width=4,
                        display_maxwidth=4,
                        max_length=4)
    
    month = IntegerField('month',
                         title="Month",
                         required=0,
                         display_width=2,
                         display_maxwidth=2,
                         max_length=2)
    
    day = IntegerField('day',
                       title="Day",
                       required=0,
                       display_width=2,
                       display_maxwidth=2,
                       max_length=2)
    
    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    sub_form.add_group("time")
    sub_form.add_fields([hour, minute], "time")
    return sub_form

def create_datetime_list_sub_form():
    sub_form = BasicForm()

    year = ListField('year',
                     title="Year",
                     required=0,
                     default="",
                     items=create_items(2000, 2010),
                     size=1)
    
    month = ListField('month',
                      title="Month",
                      required=0,
                      default="",
                      items=create_items(1, 13, digits=2),
                      size=1)
    
    day = ListField('day',
                    title="Day",
                    required=0,
                    default="",
                    items=create_items(1, 32, digits=2),
                    size=1)

    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    sub_form.add_group("time")
    sub_form.add_fields([hour, minute], "time")
    return sub_form

def create_items(start, end, digits=0):
    result = [("-", "")]
    if digits:
        format_string = "%0" + str(digits) + "d"
    else:
        format_string = "%s"
        
    for i in range(start, end):
        s = format_string % i
        result.append((s, s))
    return result



