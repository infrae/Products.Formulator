import Globals
import Acquisition
from Globals import Persistent, DTMLFile
from AccessControl import ClassSecurityInfo
import OFS
from Shared.DC.Scripts.Bindings import Bindings
from Errors import ValidationError
from Products.Formulator.Widget import MultiItemsWidget

try:
    from Products.PlacelessTranslationService import translate, getLanguages
    have_pts = 1
except ImportError:
    have_pts = 0

class Field:
    """Base class of all fields.
    A field is an object consisting of a widget and a validator.
    """
    security = ClassSecurityInfo()

    # this is a field
    is_field = 1
    # this is not an internal field (can be overridden by subclass)
    internal_field = 0
    # can alternatively render this field with Zope's :record syntax
    # this will be the record's name
    field_record = None

    def __init__(self, id, **kw):
        self.id = id
        # initialize values of fields in form
        self.initialize_values(kw)
        # initialize tales expression for fields in form
        self.initialize_tales()
        # initialize overrides of fields in form
        self.initialize_overrides()

        # initialize message values with defaults
        message_values = {}
        for message_name in self.validator.message_names:
            message_values[message_name] = getattr(self.validator,
                                                   message_name)
        self.message_values = message_values

    security.declareProtected('Change Formulator Fields', 'initialize_values')
    def initialize_values(self, dict):
        """Initialize values for properties, defined by fields in
        associated form.
        """
        values = {}
        for field in self.form.get_fields(include_disabled=1):
            id = field.id
            value = dict.get(id, field.get_value('default'))
            values[id] = value
        self.values = values

    security.declareProtected('Change Formulator Fields',
                              'initialize_tales')
    def initialize_tales(self):
        """Initialize tales expressions for properties (to nothing).
        """
        tales = {}
        for field in self.form.get_fields():
            id = field.id
            tales[id] = ""
        self.tales = tales

    security.declareProtected('Change Formulator Fields',
                              'initialize_overrides')
    def initialize_overrides(self):
        """Initialize overrides for properties (to nothing).
        """
        overrides = {}
        for field in self.form.get_fields():
            id = field.id
            overrides[id] = ""
        self.overrides = overrides

    security.declareProtected('Access contents information', 'has_value')
    def has_value(self, id):
        """Return true if the field defines such a value.
        """
        if self.values.has_key(id) or self.form.has_field(id):
            return 1
        else:
            return 0

    security.declareProtected('Access contents information', 'get_orig_value')
    def get_orig_value(self, id):
        """Get value for id; don't do any override calculation.
        """
        if self.values.has_key(id):
            return self.values[id]
        else:
            return self.form.get_field(id).get_value('default')

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
        """Get value for id.

        Optionally pass keyword arguments that get passed to TALES
        expression.
        """
        tales_expr = self.tales.get(id, "")

        if tales_expr:
            # For some reason, path expressions expect 'here' and 'request'
            # to exist, otherwise they seem to fail. python expressions
            # don't seem to have this problem.

            # add 'here' if not in kw
            if not kw.has_key('here'):
                kw['here'] = self.aq_parent
            kw['request'] = self.REQUEST
            value = tales_expr.__of__(self)(
                field=self,
                form=self.aq_parent, **kw)
        else:
            override = self.overrides.get(id, "")
            if override:
                # call wrapped method to get answer
                value = override.__of__(self)()
            else:
                # get normal value
                value = self.get_orig_value(id)
        
        # check if an i18n id exist
        if id in ['title', 'description'] and have_pts:
            i18n_domain, i18n = self.get_i18n_info()
            if i18n_domain and i18n:
                msgid = "%s_%s_%s" % (i18n, self.id, id)
                msgstr = translate(i18n_domain, msgid, context=self.REQUEST,
                    as_unicode=self.get_unicode_mode())
                if msgstr is not None:
                    return msgstr

        # if normal value is a callable itself, wrap it
        if callable(value):
            return value.__of__(self)
        else:
            return value

    def get_i18n_info(self):
        """Get i18n info. Try to get it from the form."""
        try:
            return self.aq_parent.get_i18n_info()
        except AttributeError:
            return '', ''
        
    security.declareProtected('View management screens', 'get_override')
    def get_override(self, id):
        """Get override method for id (not wrapped)."""
        return self.overrides.get(id, "")

    security.declareProtected('View management screens', 'get_tales')
    def get_tales(self, id):
        """Get tales expression method for id."""
        return self.tales.get(id, "")

    security.declareProtected('Access contents information', 'is_required')
    def is_required(self):
        """Check whether this field is required (utility function)
        """
        return self.has_value('required') and self.get_value('required')

    security.declareProtected('View management screens', 'get_error_names')
    def get_error_names(self):
        """Get error messages.
        """
        return self.validator.message_names

    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_key(self, validation=0):
        """Generate the key Silva uses to render the field in the form.
        """
        if self.field_record is None:
            return 'field_%s' % self.id
        elif validation:
            return self.id
        elif isinstance(self.widget, MultiItemsWidget):
            return "%s.%s:record:list" % (self.field_record, self.id)
        else:
            return '%s.%s:record' % (self.field_record, self.id)

    def generate_subfield_key(self, id, validation=0):
        """Generate the key Silva uses to render a sub field.
        """
        if self.field_record is None or validation:
            return 'subfield_%s_%s'%(self.id, id)
        return '%s.subfield_%s_%s:record' % (self.field_record, self.id, id)

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
    def _render_helper(self, key, value, REQUEST):
        value = self._get_default(key, value, REQUEST)
        if self.get_value('hidden'):
            return self.widget.render_hidden(self, key, value, REQUEST)
        else:
            return self.widget.render(self, key, value, REQUEST)

    security.declarePrivate('_get_default')
    def _get_default(self, key, value, REQUEST):
        if value is not None:
            return value
        try:
            value = REQUEST.form[key]
        except (KeyError, AttributeError):
            # fall back on default
            return self.get_value('default')

        # if we enter a string value while the field expects unicode,
        # convert to unicode first
        # this solves a problem when re-rendering a sticky form with
        # values from request
        if (self.has_value('unicode') and self.get_value('unicode') and
            type(value) == type('')):
            return unicode(value, self.get_form_encoding())
        else:
            return value

    security.declareProtected('View', 'render')
    def render(self, value=None, REQUEST=None):
        """Render the field widget.
        value -- the value the field should have (for instance
                 from validation).
        REQUEST -- REQUEST can contain raw (unvalidated) field
                 information. If value is None, REQUEST is searched
                 for this value.
        if value and REQUEST are both None, the 'default' property of
        the field will be used for the value.
        """
        return self._render_helper(self.generate_field_key(), value, REQUEST)

    security.declareProtected('View', 'render_view')
    def render_view(self, value):
        """Render value to be viewed.
        """
        return self.widget.render_view(self, value)

    security.declareProtected('View', 'render_from_request')
    def render_from_request(self, REQUEST):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self._render_helper(self.generate_field_key(), None, REQUEST)

    security.declareProtected('View', 'render_sub_field')
    def render_sub_field(self, id, value=None, REQUEST=None):
        """Render a sub field, as part of complete rendering of widget in
        a form. Works like render() but for sub field.
        """
        return self.sub_form.get_field(id)._render_helper(
            self.generate_subfield_key(id), value, REQUEST)

    security.declareProtected('View', 'render_sub_field_from_request')
    def render_sub_field_from_request(self, id, REQUEST):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self.sub_form.get_field(id)._render_helper(
            self.generate_subfield_key(id), None, REQUEST)

    security.declarePrivate('_validate_helper')
    def _validate_helper(self, key, REQUEST):
        value = self.validator.validate(self, key, REQUEST)
        # now call external validator after all other validation
        external_validator = self.get_value('external_validator')
        if external_validator and not external_validator(value, REQUEST):
            self.validator.raise_error('external_validator_failed', self)
        return value

    security.declareProtected('View', 'validate')
    def validate(self, REQUEST):
        """Validate/transform the field.
        """
        return self._validate_helper(
            self.generate_field_key(validation=1), REQUEST)

    security.declareProtected('View', 'need_validate')
    def need_validate(self, REQUEST):
        """Return true if validation is needed for this field.
        """
        return self.validator.need_validate(
            self, self.generate_field_key(validation=1), REQUEST)

    security.declareProtected('View', 'validate_sub_field')
    def validate_sub_field(self, id, REQUEST):
        """Validates a subfield (as part of field validation).
        """
        return self.sub_form.get_field(id)._validate_helper(
            self.generate_subfield_key(id, validation=1), REQUEST)

Globals.InitializeClass(Field)

class ZMIField(
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
        {'label':'TALES',      'action':'manage_talesForm',
         'help':('Formulator', 'fieldTales.txt')},
        {'label':'Override',    'action':'manage_overrideForm',
         'help':('Formulator', 'fieldOverride.txt')},
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
    manage_main = DTMLFile('dtml/fieldEdit', globals())

    security.declareProtected('Change Formulator Fields', 'manage_edit')
    def manage_edit(self, REQUEST):
        """Submit Field edit form.
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

        self._edit(result)

        if REQUEST:
            message="Content changed."
            return self.manage_main(self,REQUEST,
                                    manage_tabs_message=message)

    security.declareProtected('Change Formulator Fields', 'manage_edit_xmlrpc')
    def manage_edit_xmlrpc(self, map):
        """Edit Field Properties through XMLRPC
        """
        # BEWARE: there is no validation on the values passed through the map
        self._edit(map)

    def _edit(self, result):
        # first check for any changes
        values = self.values
        # if we are in unicode mode, convert result to unicode
        # acquire get_unicode_mode and get_stored_encoding from form..
        if self.get_unicode_mode():
            new_result = {}
            for key, value in result.items():
                if type(value) == type(''):
                    # in unicode mode, Formulator UI always uses UTF-8
                    value = unicode(value, 'UTF-8')
                new_result[key] = value
            result = new_result

        changed = []
        for key, value in result.items():
            # store keys for which we want to notify change
            if not values.has_key(key) or values[key] != value:
                changed.append(key)

        # now do actual update of values
        values.update(result)
        self.values = values

        # finally notify field of all changed values if necessary
        for key in changed:
            method_name = "on_value_%s_changed" % key
            if hasattr(self, method_name):
                getattr(self, method_name)(values[key])


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

    # methods screen
    security.declareProtected('View management screens',
                              'manage_overrideForm')
    manage_overrideForm = DTMLFile('dtml/fieldOverride', globals())

    security.declareProtected('Change Formulator Forms', 'manage_override')
    def manage_override(self, REQUEST):
        """Change override methods.
        """
        try:
            # validate the form and get results
            result = self.override_form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_overrideForm(self,REQUEST,
                                                manage_tabs_message=message)
            else:
                raise

        # update overrides of field with results
        if not hasattr(self, "overrides"):
            self.overrides = result
        else:
            self.overrides.update(result)
            self.overrides = self.overrides

        if REQUEST:
            message="Content changed."
            return self.manage_overrideForm(self,REQUEST,
                                            manage_tabs_message=message)

    # tales screen
    security.declareProtected('View management screens',
                              'manage_talesForm')
    manage_talesForm = DTMLFile('dtml/fieldTales', globals())

    security.declareProtected('Change Formulator Forms', 'manage_tales')
    def manage_tales(self, REQUEST):
        """Change TALES expressions.
        """
        try:
            # validate the form and get results
            result = self.tales_form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_talesForm(self,REQUEST,
                                             manage_tabs_message=message)
            else:
                raise

        self._edit_tales(result)

        if REQUEST:
            message="Content changed."
            return self.manage_talesForm(self, REQUEST,
                                         manage_tabs_message=message)

    def _edit_tales(self, result):
        if not hasattr(self, 'tales'):
            self.tales = result
        else:
            self.tales.update(result)
            self.tales = self.tales

    security.declareProtected('Change Formulator Forms', 'manage_tales_xmlrpc')
    def manage_tales_xmlrpc(self, map):
        """Change TALES expressions through XMLRPC.
        """
        # BEWARE: there is no validation on the values passed through the map
        from TALESField import TALESMethod
        result = {}
        for key, value in map.items():
            result[key] = TALESMethod(value)
        self._edit_tales(result)

    # display test screen
    security.declareProtected('View management screens', 'fieldTest')
    fieldTest = DTMLFile('dtml/fieldTest', globals())

    # messages screen
    security.declareProtected('View management screens', 'manage_messagesForm')
    manage_messagesForm = DTMLFile('dtml/fieldMessages', globals())

    # field list header
    security.declareProtected('View management screens', 'fieldListHeader')
    fieldListHeader = DTMLFile('dtml/fieldListHeader', globals())

    # field description display
    security.declareProtected('View management screens', 'fieldDescription')
    fieldDescription = DTMLFile('dtml/fieldDescription', globals())

    security.declareProtected('Change Formulator Fields', 'manage_messages')
    def manage_messages(self, REQUEST):
        """Change message texts.
        """
        messages = self.message_values
        unicode_mode = self.get_unicode_mode()
        for message_key in self.get_error_names():
            message = REQUEST[message_key]
            if unicode_mode:
                message = unicode(message, 'UTF-8')
            messages[message_key] = message

        self.message_values = messages
        if REQUEST:
            message="Content changed."
            return self.manage_messagesForm(self,REQUEST,
                                            manage_tabs_message=message)

    security.declareProtected('View', 'index_html')
    def index_html(self, REQUEST):
        """Render this field.
        """
        return self.render(REQUEST=REQUEST)

    security.declareProtected('Access contents information', '__getitem__')
    def __getitem__(self, key):
        return self.get_value(key)

    security.declareProtected('View management screens', 'isTALESAvailable')
    def isTALESAvailable(self):
        """Return true only if TALES is available.
        """
        try:
            from Products.PageTemplates.Expressions import getEngine
            return 1
        except ImportError:
            return 0

Globals.InitializeClass(ZMIField)
PythonField = ZMIField # NOTE: for backwards compatibility

class ZClassField(Field):
    """Base class for a field implemented as a ZClass.
    """
    pass



