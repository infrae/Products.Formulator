import string
from DummyField import fields
import Widget, Validator
from Globals import Persistent
import Acquisition
from Field import ZMIField
from AccessControl import getSecurityManager
from Products.PageTemplates.Expressions import getEngine

class TALESWidget(Widget.TextWidget):
    default = fields.MethodField('default',
                                 title='Default',
                                 default="",
                                 required=0)
    
    def render(self, field, key, value, REQUEST):
        if value == None:
            text = field.get_value('default')
        else:
            if value != "":
                text = value._text
            else:
                text = ""
        return Widget.TextWidget.render(self, field, key, text, REQUEST)

TALESWidgetInstance = TALESWidget()

class TALESMethod(Persistent, Acquisition.Implicit):
    """A method object; calls method name in acquisition context.
    """
    def __init__(self, text):
        self._text = text
        #self._expr = getEngine().compile(text)
        
    def __call__(self, **kw):
        expr = getEngine().compile(self._text)
        return getEngine().getContext(kw).evaluate(expr)
        
        # check if we have 'View' permission for this method
        # (raises error if not)
        # getSecurityManager().checkPermission('View', method)

    
class TALESValidator(Validator.StringBaseValidator):

    def validate(self, field, key, REQUEST):
        value = Validator.StringBaseValidator.validate(self, field, key,
                                                       REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        return TALESMethod(value)
    
TALESValidatorInstance = TALESValidator()

class TALESField(ZMIField):
    meta_type = 'TALESField'

    internal_field = 1

    widget = TALESWidgetInstance
    validator = TALESValidatorInstance
    
    
