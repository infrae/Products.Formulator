from Form import BasicForm
from Field import ZMIField
from DummyField import fields
from MethodField import BoundMethod
from DateTime import DateTime
import Validator, Widget
import OFS

class StringField(ZMIField):
    meta_type = "StringField"
    
    widget = Widget.TextWidgetInstance
    validator = Validator.StringValidatorInstance

class PasswordField(ZMIField):
    meta_type = "PasswordField"

    widget = Widget.PasswordWidgetInstance
    validator = Validator.StringValidatorInstance

class EmailField(ZMIField):
    meta_type = "EmailField"

    widget = Widget.TextWidgetInstance
    validator = Validator.EmailValidatorInstance
    
class CheckBoxField(ZMIField):
    meta_type = "CheckBoxField"

    widget = Widget.CheckBoxWidgetInstance
    validator = Validator.BooleanValidatorInstance
        
class IntegerField(ZMIField):
    meta_type = "IntegerField"

    widget = Widget.TextWidgetInstance
    validator = Validator.IntegerValidatorInstance

class RangedIntegerField(ZMIField):
    meta_type = "RangedIntegerField"

    # this field is not addable anymore and deprecated. For
    # backwards compatibility it's a clone of IntegerField,
    # though it may go away in the future.
    internal_field = 1 
    
    widget = Widget.TextWidgetInstance
    validator = Validator.IntegerValidatorInstance

class FloatField(ZMIField):
    meta_type = "FloatField"

    widget = Widget.TextWidgetInstance
    validator = Validator.FloatValidatorInstance
    
class TextAreaField(ZMIField):
    meta_type = "TextAreaField"

    widget = Widget.TextAreaWidgetInstance
    validator = Validator.TextValidatorInstance
    
class ListField(ZMIField):
    meta_type = "ListField"

    widget = Widget.ListWidgetInstance
    validator = Validator.SelectionValidatorInstance

class MultiListField(ZMIField):
    meta_type = "MultiListField"

    widget = Widget.MultiListWidgetInstance
    validator = Validator.MultiSelectionValidatorInstance

class LinesField(ZMIField):
    meta_type = "LinesField"

    widget = Widget.LinesTextAreaWidgetInstance
    validator = Validator.LinesValidatorInstance
   
class RadioField(ZMIField):
    meta_type = "RadioField"

    widget = Widget.RadioWidgetInstance
    validator = Validator.SelectionValidatorInstance

class MultiCheckBoxField(ZMIField):
    meta_type = "MultiCheckBoxField"

    widget = Widget.MultiCheckBoxWidgetInstance
    validator = Validator.MultiSelectionValidatorInstance
    
class FileField(ZMIField):
     meta_type = "FileField"
 
     widget = Widget.FileWidgetInstance
     validator = Validator.FileValidatorInstance
 
class LinkField(ZMIField):
    meta_type = "LinkField"
    
    widget = Widget.TextWidgetInstance
    validator = Validator.LinkValidatorInstance

class DateTimeField(ZMIField):
    meta_type = "DateTimeField"

    widget = Widget.DateTimeWidgetInstance
    validator = Validator.DateTimeValidatorInstance

    def __init__(self, id, **kw):
        # icky but necessary...
        apply(ZMIField.__init__, (self, id), kw)

        if self.get_value('input_style') == 'text':
            self.sub_form = create_datetime_text_sub_form()
        elif value == 'list':
            self.sub_form = create_datetime_list_sub_form()
        else:
            assert 0, "Unknown input_style"
            
    def on_value_input_style_changed(self, value):
        if value == 'text':
            self.sub_form = create_datetime_text_sub_form()
        elif value == 'list':
            self.sub_form = create_datetime_list_sub_form()
            year_field = self.sub_form.get_field('year')
            year_field.overrides['items'] = BoundMethod(self,
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



