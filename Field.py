import Globals
import Acquisition
from Globals import Persistent, DTMLFile
from AccessControl import ClassSecurityInfo
import OFS
from Shared.DC.Scripts.Bindings import Bindings

from Validator import ValidationError

class Field:
    """Base class of all fields.
    A field is an object consisting of a widget and a validator.
    """
    security = ClassSecurityInfo()

    sub_field_names = []

    # this is a field
    is_field = 1
    # this is not an internal field (can be overridden by subclass)
    internal_field = 0
    
    def __init__(self, id, **kw):
        self.id = id
        # initialize values of fields in form
        self.initialize_values(kw)
        
        # initialize message values with defaults
        message_values = {}
        for message_name in self.validator.message_names:
            message_values[message_name] = getattr(self.validator,
                                                   message_name)
        self.message_values = message_values

    security.declareProtected('Change Formulator Fields', 'initialize_values')
    def initialize_values(self, dict):
        """Initialize values for fields in associated form.
        """
        values = {}
        for field in self.form.get_fields():
            id = field.id
            value = dict.get(id, field.get_value('default'))
            values[id] = value
        self.values = values
        
    security.declareProtected('Access contents information', 'has_value')
    def has_value(self, id):
        """Return true if the field defines such a value.
        """
        if self.values.has_key(id) or self.form.has_field_id(id):
            return 1
        else:
            return 0

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id):
        """Get value for id."""
        try:
            value = self.values[id]
        except KeyError:
            # try to return default value in case of error
            # this way fields can be smoothly upgraded with new
            # property fields.
            # this may fail too if there is no field with this name;
            # in that case we want it to be an error
            value = self.form.get_field(id).get_value('default')
            
        if callable(value):
            return value.__of__(self)
        else:
            return value
    
    security.declareProtected('View management screens', 'get_error_names')
    def get_error_names(self):
        """Get error messages.
        """
        return self.validator.message_names

    security.declareProtected('View management screens', 'get_error_message')
    def get_error_message(self, name):
        try:
            return self.message_values[name]
        except KeyError:
            if name in self.validator.message_names:
                return getattr(self.validator, name)
            else:
                return "Unknown error: %s" % name
    
    security.declarePrivate('_render_helper')
    def _render_helper(self, key, value=None):
        if value == None:
            value = self.get_value('default')
        if self.get_value('hidden'):
            return self.widget.render_hidden(self, key, value)
        else:
            return self.widget.render(self, key, value)
        
    security.declareProtected('View', 'render')
    def render(self, value=None):
        """Render the field widget
        """
        return self._render_helper("field_%s" % self.id, value)

    security.declareProtected('View', 'render_sub_field')
    def render_sub_field(self, id, value=None):
        """Render a sub field of this field, as part of
        complete rendering of widget in a form.
        """
        return self.sub_form.get_field(id)._render_helper(
            "subfield_%s_%s" % (self.id, id), value)

    security.declarePrivate('_validate_helper')
    def _validate_helper(self, key, REQUEST):
        return self.validator.validate(self, key, REQUEST)
    
    security.declareProtected('View', 'validate')    
    def validate(self, REQUEST):
        """Validate/transform the field.
        """
        return self._validate_helper("field_%s" % self.id, REQUEST)

    security.declareProtected('View', 'validate_sub_field')
    def validate_sub_field(self, id, REQUEST):
        """Validates a subfield (as part of field validation).
        """
        return self.sub_form.get_field(id)._validate_helper(
            "subfield_%s_%s" % (self.id, id), REQUEST)

Globals.InitializeClass(Field)
    
class PythonField(
    Acquisition.Implicit,
    Persistent,
    OFS.SimpleItem.Item,
    Field,
    ):
    """Base class for a field implemented as a Python (file) product.
    """
    security = ClassSecurityInfo()

    security.declareObjectProtected('View')
   
    # the various tabs of a field
    manage_options = (
        {'label':'Edit',       'action':'manage_main',
         'help':('Formulator', 'fieldEdit.txt')},
        {'label':'Messages',   'action':'manage_messagesForm',
         'help':('Formulator', 'fieldMessages.txt')},
        {'label':'Test',       'action':'fieldTest',
         'help':('Formulator', 'fieldTest.txt')},
        ) + OFS.SimpleItem.SimpleItem.manage_options
         
    security.declareProtected('View', 'title')
    def title(self):
        """The title of this field."""
        return self.get_value('title')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = DTMLFile('www/fieldEdit', globals())

    security.declareProtected('Change Formulator Fields', 'manage_edit')
    def manage_edit(self, REQUEST):
        """Submit edit form.
        """
        try:
            # validate the form and get results
            result = self.form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_main(self,REQUEST,
                                        manage_tabs_message=message)
            else:
                raise

        # update values of field with results
        self.values.update(result)
        self.values = self.values
        
        if REQUEST:
            message="Content changed."
            return self.manage_main(self,REQUEST,
                                    manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms', 'manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        """Remove name from list if object is deleted.
        """
        # update group info in form
        if hasattr(item.aq_explicit, 'is_field'):
            container.field_removed(item.id)

    security.declareProtected('Change Formulator Forms', 'manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """What happens when we add a field.
        """
        # update group info in form
        if hasattr(item.aq_explicit, 'is_field'):
            container.field_added(item.id)
    
    # display test screen
    security.declareProtected('View management screens', 'fieldTest')
    fieldTest = DTMLFile('www/fieldTest', globals())

    # messages screen
    security.declareProtected('View management screens', 'manage_messagesForm')
    manage_messagesForm = DTMLFile('www/fieldMessages', globals())

    # field list header
    security.declareProtected('View management screens', 'fieldListHeader')
    fieldListHeader = DTMLFile('www/fieldListHeader', globals())

    # field description display
    security.declareProtected('View management screens', 'fieldDescription')
    fieldDescription = DTMLFile('www/fieldDescription', globals())
    
    security.declareProtected('Change Formulator Fields', 'manage_messages')
    def manage_messages(self, REQUEST):
        """Change message texts.
        """
        messages = self.message_values
        for message_key in self.get_error_names():
            messages[message_key] = REQUEST[message_key]

        self.message_values = messages
        if REQUEST:
            message="Content changed."
            return self.manage_messagesForm(self,REQUEST,
                                            manage_tabs_message=message)
        
    security.declareProtected('View', 'index_html')
    def index_html(self):
        """Render this field.
        """
        return self.render()

Globals.InitializeClass(PythonField)

class ZClassField(Field):
    """Base class for a field implemented as a ZClass.
    """
    pass



