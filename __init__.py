from Globals import DTMLFile
import Form
import StandardFields, HelperFields
from FieldRegistry import FieldRegistry

def initialize(context):
    """Initialize the Formulator product.
    """
    # register field classes
    FieldRegistry.registerField(StandardFields.StringField,
                                'www/StringField.gif')
    FieldRegistry.registerField(StandardFields.CheckBoxField,
                                'www/CheckBoxField.gif')
    FieldRegistry.registerField(StandardFields.IntegerField,
                                'www/IntegerField.gif')
    FieldRegistry.registerField(StandardFields.TextAreaField,
                                'www/TextAreaField.gif')
    FieldRegistry.registerField(StandardFields.ListField,
                                'www/ListField.gif')
    FieldRegistry.registerField(StandardFields.RadioField,
                                'www/ListField.gif')
    FieldRegistry.registerField(StandardFields.PasswordField,
                                'www/PasswordField.gif')
    FieldRegistry.registerField(StandardFields.EmailField,
                                'www/EmailField.gif')
    FieldRegistry.registerField(StandardFields.FloatField,
                                'www/FloatField.gif')
    FieldRegistry.registerField(StandardFields.DateTimeField,
                                'www/DateTimeField.gif')
    
    # some helper fields
    FieldRegistry.registerField(HelperFields.ListTextAreaField)
    FieldRegistry.registerField(HelperFields.MethodField)

    # obsolete field (same as helper; useable but not addable)
    FieldRegistry.registerField(StandardFields.RangedIntegerField,
                                'www/RangedIntegerField.gif')
    
    # register help for the product
    context.registerHelp()
    # register field help for all fields
    FieldRegistry.registerFieldHelp(context)
    
    # register the form itself
    context.registerClass(
        Form.PythonForm,
        constructors = (Form.manage_addForm,
                        Form.manage_add),
        icon = 'www/Form.gif')

    # make Dummy Fields into real fields
    FieldRegistry.initializeFields()
    
    # do initialization of Form class to make fields addable
    Form.initializeForm(FieldRegistry)

