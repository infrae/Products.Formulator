import string, re
from DummyField import fields
from DateTime import DateTime

class ValidationError(Exception):
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, error_key, field):
        Exception.__init__(self, error_key)
        self.error_key = error_key
        self.field_id = field.id
        self.field = field
        self.error_text = field.get_error_message(error_key)

class Validator:
    """Validates input and possibly transforms it to output.
    """
    property_names = []
    message_names = []
    
    def raise_error(self, error_key, field):
        raise ValidationError(error_key, field)
    
    def validate(self, field, key, REQUEST):
        return REQUEST.get(key, None)
    
class StringBaseValidator(Validator):
    """Simple string validator.
    """
    property_names = Validator.property_names + ['required']

    required = fields.CheckBoxField('required',
                                    title='Required',
                                    description=(
        "Checked if the field is required; the user has to fill in some "
        "data."),
                                    default=1)

    message_names = Validator.message_names + ['required_not_found']
    
    required_not_found = 'Input is required but no input given.'
        
    def validate(self, field, key, REQUEST):
        value = string.strip(REQUEST.get(key, ""))
        if field.get_value('required') and value == "":
            self.raise_error('required_not_found', field)
        return value

class StringValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                     ['max_length', 'truncate']

    max_length = fields.IntegerField('max_length',
                                     title='Maximum length',
                                     description=(
        "The maximum amount of characters that can be entered in this "
        "field. If set to 0, there is no maximum. Note that this is "
        "server side validation. Required."),
                                     default=0,
                                     required=1)
    truncate = fields.CheckBoxField('truncate',
                                    title='Truncate',
                                    description=(
        "If checked, truncate the field if it receives more input than is "
        "allowed. The normal behavior in this case is to raise a validation "
        "error, but the text can be silently truncated instead."),
                                    default=0)

    message_names = StringBaseValidator.message_names +\
                    ['too_long']

    too_long = 'Too much input was given.'

    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)

        max_length = field.get_value('max_length')
        truncate = field.get_value('truncate')
        
        if max_length > 0 and len(value) > max_length:
            if truncate:
                value = value[:max_length]
            else:
                self.raise_error('too_long', field)
        return value

StringValidatorInstance = StringValidator()

class EmailValidator(StringValidator):
    message_names = StringValidator.message_names + ['not_email']

    not_email = 'You did not enter an email address.'

    # contributed, I don't pretend to understand this..
    pattern = re.compile("^([0-9a-z_&.+-]+!)*[0-9a-z_&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,3}|([0-9]{1,3}\.){3}[0-9]{1,3})$")
    
    def validate(self, field, key, REQUEST):
        value = StringValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value

        if self.pattern.search(string.lower(value)) == None:
            self.raise_error('not_email', field)
        return value

EmailValidatorInstance = EmailValidator()

class BooleanValidator(Validator):
    def validate(self, field, key, REQUEST):
        return not not REQUEST.get(key, 0)

BooleanValidatorInstance = BooleanValidator()

class IntegerValidator(StringBaseValidator):

    message_names = StringBaseValidator.message_names +\
                    ['not_integer']

    not_integer = 'You did not enter an integer.'
    
    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)
        # need to add this check to allow empty fields
        if value == "" and not field.get_value('required'):
            return value
        
        try:
            value = int(value)
        except ValueError:
            self.raise_error('not_integer', field)
        return value

IntegerValidatorInstance = IntegerValidator()

class RangedIntegerValidator(IntegerValidator):
    property_names = IntegerValidator.property_names +\
                     ['start', 'end']

    start = fields.IntegerField('start',
                                title='Start',
                                description=(
        "The integer entered by the user must be larger than or equal to "
        "this value. Required."),
                                default=0,
                                required=1)

    end = fields.IntegerField('end',
                              title='End',
                              description=(
        "The integer entered by the user must be smaller than this "
        "value. Required."),
                              default=100,
                              required=1)

    message_names = IntegerValidator.message_names +\
                    ['integer_out_of_range']

    integer_out_of_range = 'The integer you entered was out of range.'

    def validate(self, field, key, REQUEST):
        value = IntegerValidator.validate(self, field, key, REQUEST)
        # we need to add this check again
        if value == "" and not field.get_value('required'):
            return value
        if not field.get_value('start') <= value <= field.get_value('end'):
            self.raise_error('integer_out_of_range', field)

        return value

RangedIntegerValidatorInstance = RangedIntegerValidator()

class FloatValidator(StringBaseValidator):
    message_names = StringBaseValidator.message_names + ['not_float']

    not_float = "You did not enter a floating point number."

    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value

        try:
            value = float(value)
        except ValueError:
            self.raise_error('not_float', field)
        return value

FloatValidatorInstance = FloatValidator()

class LinesValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                     ['max_lines', 'max_linelength', 'max_length']

    max_lines = fields.IntegerField('max_lines',
                                    title='Maximum lines',
                                    description=(
        "The maximum amount of lines a user can enter. If set to 0, "
        "there is no maximum. Required."),
                                    default=0,
                                    required=1)

    max_linelength = fields.IntegerField('max_linelength',
                                         title="Maximum length of line",
                                         description=(
        "The maximum length of a line. If set to 0, there is no "
        "maximum. Required."),
                                         default=0,
                                         required=1)

    max_length = fields.IntegerField('max_length',
                                     title="Maximum length (in characters)",
                                     description=(
        "The maximum total length in characters that the user may enter. "
        "If set to 0, there is no maximum. Required."),
                                     default=0,
                                     required=1)
    
    message_names = StringBaseValidator.message_names +\
                    ['too_many_lines', 'line_too_long', 'too_long']

    
    too_many_lines = 'You entered too many lines.'
    line_too_long = 'A line was too long.'
    too_long = 'You entered too many characters.'
    
    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)
        # we need to add this check again
        if value == "" and not field.get_value('required'):
            return value
        # check whether the entire input is too long
        max_length = field.get_value('max_length')
        if max_length and len(value) > max_length:
            self.raise_error('too_long', field)
        # split input into separate lines
        lines = string.split(value, "\n")

        # check whether we have too many lines
        max_lines = field.get_value('max_lines')
        if max_lines and len(lines) > max_lines:
            self.raise_error('too_many_lines', field)

        # strip extraneous data from lines and check whether each line is
        # short enough
        max_linelength = field.get_value('max_linelength')
        result = []
        for line in lines:
            line = string.strip(line)
            if max_linelength and len(line) > max_linelength:
                self.raise_error('line_too_long', field)
            result.append(line)
            
        return result

LinesValidatorInstance = LinesValidator()    

class TextValidator(LinesValidator):
    def validate(self, field, key, REQUEST):
        value = LinesValidator.validate(self, field, key, REQUEST)
        # we need to add this check again
        if value == [] and not field.get_value('required'):
            return value

        # join everything into string again with \n and return
        return string.join(value, "\n")

TextValidatorInstance = TextValidator()

class SelectionValidator(StringBaseValidator):

    message_names = StringBaseValidator.message_names +\
                    ['unknown_selection']

    unknown_selection = 'You selected an item that was not in the list.'
    
    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        items_method = field.get_value('items_method')
        if items_method:
            items = items_method()
        else:
            items = field.get_value('items')

        # we want the string representation of all possible values,
        # just in case we're getting something else, because the user
        # form input will always be a string representation
        values = map(lambda element: str(element[1]), items)
        
        if value in values:
            return value
        else:
            self.raise_error('unknown_selection', field)
            
SelectionValidatorInstance = SelectionValidator()

class TestValidator(Validator):
    def validate(self, field, key, REQUEST):
        first_value = field.validate_sub_field('first_field', REQUEST)
        second_value = field.validate_sub_field('second_field', REQUEST)
        return first_value, second_value


TestValidatorInstance = TestValidator()
        
    
