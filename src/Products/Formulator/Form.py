# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from six import StringIO
from six.moves import range
from six.moves.urllib.parse import quote

import Acquisition
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from App.special_dtml import DTMLFile
from ComputedAttribute import ComputedAttribute
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.role import RoleManager
from OFS.SimpleItem import Item
from Persistence import Persistent
from zope.interface import implementer

from Products.Formulator.DummyField import fields
from Products.Formulator.Errors import FieldDisabledError
from Products.Formulator.Errors import FormValidationError
from Products.Formulator.Errors import ValidationError
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.FormToXML import formToXML
from Products.Formulator.helpers import ensure_unicode
from Products.Formulator.interfaces import IForm
from Products.Formulator.Widget import render_tag
from Products.Formulator.XMLToForm import XMLToForm


@implementer(IForm)
class Form:
    """Form base class.
    """
    security = ClassSecurityInfo()

    # need to make settings form upgrade
    encoding = 'UTF-8'
    stored_encoding = 'ISO-8859-1'
    unicode_mode = 0
    i18n_domain = ''

    # CONSTRUCTORS
    def __init__(self, action, method, enctype, name,
                 encoding, stored_encoding, unicode_mode):
        """Initialize form.
        """
        # make groups dict with entry for default group
        self.groups = {"Default": []}
        # the display order of the groups
        self.group_list = ["Default"]
        # form submit info
        self.name = name     # for use by javascript
        self.action = action
        self.method = method
        self.enctype = enctype
        self.encoding = encoding
        self.stored_encoding = stored_encoding
        self.unicode_mode = unicode_mode

    security.declareProtected('View', 'test_form')
    def test_form(self, context=None, bad_fields=[]):
        all_invalid_fields = set(['name', 'action'])
        all_invalid_fields.update(bad_fields)
        try:
            form_fields = self.get_fields()
        except AttributeError:
            raise ValueError(u"Form contains broken fields.")
        errors = []
        for field in form_fields:
            if field.id in all_invalid_fields:
                errors.append(
                    (u"Form field '%s' have an identifier that will conflict "
                     u"with the behavior of the form.") % (field.id))
            for identifier, expression in field.tales.items():
                if not expression:
                    continue
                try:
                    if context is not None:
                        field = field.__of__(context)
                    field.get_value(identifier)
                except Exception as error:
                    errors.append(
                        (u"Form field '%s' contains a broken TALES "
                         u"expression for option '%s': %s: %s.") % (
                            field.id, identifier,
                            error.__class__.__name__, str(error)))
        if errors:
            raise ValueError(*errors)
        return True

    # MANIPULATORS
    security.declareProtected('Change Formulator Forms', 'field_added')
    def field_added(self, field_id, group=None):
        """A field was added to the form.
        """
        # get indicated group or the first group if none was indicated
        group = group or self.group_list[0]
        # add it to the indicated group (create group if nonexistent)
        groups = self.groups
        field_list = groups.get(group, [])
        if field_id not in field_list:
            field_list.append(field_id)
            self._p_changed = True
        groups[group] = field_list
        if group not in self.group_list:
            self.group_list.append(group)
            self._p_changed = True

    security.declareProtected('Change Formulator Forms', 'field_removed')
    def field_removed(self, field_id):
        """A field was removed from the form.
        """
        for field_list in self.groups.values():
            if field_id in field_list:
                field_list.remove(field_id)
                self._p_changed = True
                break  # should be done as soon as we found it once

    security.declareProtected('Change Formulator Forms', 'move_field_up')
    def move_field_up(self, field_id, group):
        groups = self.groups
        field_list = groups[group]
        i = field_list.index(field_id)
        if i == 0:
            return 0  # can't move further up, so we're done
        # swap fields, moving i up
        field_list[i], field_list[i - 1] = field_list[i - 1], field_list[i]
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'move_field_down')
    def move_field_down(self, field_id, group):
        groups = self.groups
        field_list = groups[group]
        i = field_list.index(field_id)
        if i == len(field_list) - 1:
            return 0  # can't move further down, so we're done
        # swap fields, moving i down
        field_list[i], field_list[i + 1] = field_list[i + 1], field_list[i]
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'move_field_group')
    def move_field_group(self, field_ids, from_group, to_group):
        """Moves a field from one group to the other.
        """
        if len(field_ids) == 0:
            return 0
        if from_group == to_group:
            return 0
        groups = self.groups
        from_list = groups[from_group]
        to_list = groups[to_group]
        for field in self.get_fields_in_group(
                from_group, include_disabled=1)[:]:
            if field.id in field_ids:
                from_list.remove(field.id)
                to_list.append(field.id)
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'add_group')
    def add_group(self, group):
        """Add a new group.
        """
        groups = self.groups
        if group in groups:
            return 0  # group already exists (NOTE: should we raise instead?)
        groups[group] = []
        # add the group to the bottom of the list of groups
        self.group_list.append(group)
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'remove_group')
    def remove_group(self, group):
        """Remove a group.
        """
        groups = self.groups
        if group == self.group_list[0]:
            return 0  # can't remove first group
        if group not in groups:
            return 0  # group does not exist (NOTE: should we raise instead?)
        # move whatever is in the group now to the end of the first group
        groups[self.group_list[0]].extend(groups[group])
        # now remove the key
        del groups[group]
        # remove it from the group order list as well
        self.group_list.remove(group)
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'rename_group')
    def rename_group(self, group, name):
        """Rename a group.
        """
        group_list = self.group_list
        groups = self.groups
        if group not in groups:
            return 0  # can't rename unexisting group
        if name in groups:
            return 0  # can't rename into existing name
        i = group_list.index(group)
        group_list[i] = name
        groups[name] = groups[group]
        del groups[group]
        self._p_changed = True
        return 1

    security.declareProtected('Change Formulator Forms', 'move_group_up')
    def move_group_up(self, group):
        """Move a group up in the group list.
        """
        group_list = self.group_list
        i = group_list.index(group)
        if i == 1:
            return 0  # can't move further up, so we're done
        # swap groups, moving i up
        group_list[i], group_list[i - 1] = group_list[i - 1], group_list[i]
        self.group_list = group_list
        return 1

    security.declareProtected('Change Formulator Forms', 'move_group_down')
    def move_group_down(self, group):
        """Move a group down in the group list.
        """
        group_list = self.group_list
        i = group_list.index(group)
        if i == len(group_list) - 1:
            return 0  # can't move further up, so we're done
        # swap groups, moving i down
        group_list[i], group_list[i + 1] = group_list[i + 1], group_list[i]
        self._p_changed = True
        return 1

    # ACCESSORS
    security.declareProtected('View', 'get_fields')
    def get_fields(self, include_disabled=0):
        """Get all fields for all groups (in the display order).
        """
        result = []
        for group in self.get_groups(include_empty=1):
            result.extend(self.get_fields_in_group(group, include_disabled))
        return result

    security.declareProtected('View', 'get_field_ids')
    def get_field_ids(self, include_disabled=0):
        """Get all the ids of the fields in the form.
        """
        result = []
        for field in self.get_fields(include_disabled):
            result.append(field.id)
        return result

    security.declareProtected('View', 'get_fields_in_group')
    def get_fields_in_group(self, group, include_disabled=0):
        """Get all fields in a group (in the display order).
        """
        result = []
        for field_id in self.groups.get(group, []):
            try:
                field = self.get_field(field_id, include_disabled)
            except FieldDisabledError:
                pass
            else:
                result.append(field)
        return result

    security.declareProtected('View', 'has_field')
    def has_field(self, id, include_disabled):
        """Check whether the form has a field of a certain id.
        """
        # define in subclass
        pass

    security.declareProtected('View', 'get_field')
    def get_field(self, id, include_disabled):
        """Get a field of a certain id.
        """
        # define in subclass
        pass

    security.declareProtected('View', 'get_groups')
    def get_groups(self, include_empty=0):
        """Get a list of all groups, in display order.

        If include_empty is false, suppress groups that do not have
        enabled fields.
        """
        if include_empty:
            return self.group_list
        return [group for group in self.group_list
                if self.get_fields_in_group(group)]

    security.declareProtected('View', 'get_form_encoding')
    def get_form_encoding(self):
        """Get the encoding the form is in. Should be the same as the
        encoding of the page, if specified, for unicode to work. Default
        is 'UTF-8'.
        """
        return getattr(self, 'encoding', 'UTF-8')

    security.declareProtected('View', 'get_stored_encoding')
    def get_stored_encoding(self):
        """Get the encoding of the stored field properties.
        """
        return getattr(self, 'stored_encoding', 'ISO-8859-1')

    security.declareProtected('View', 'get_unicode_mode')
    def get_unicode_mode(self):
        """Get unicode mode information.
        """
        return getattr(self, 'unicode_mode', 0)

    security.declareProtected('View', 'get_i18n_domain')
    def get_i18n_domain(self):
        """Get i18n domain, if any.
        """
        return getattr(self, 'i18n_domain', '')

    security.declareProtected('View', 'render')
    def render(self, dict=None, REQUEST=None):
        """Render form in a default way.
        """
        dict = dict or {}
        result = StringIO()
        w = result.write
        w(self.header())
        for group in self.get_groups():
            w('<h2>%s</h2>\n' % group)
            w('<table border="0" cellspacing="0" cellpadding="2">\n')
            for field in self.get_fields_in_group(group):
                if field.id in dict:
                    value = dict[field.id]
                else:
                    value = None
                w('<tr>\n')
                if not field.get_value('hidden'):
                    w('<td>%s</td>\n' % field.get_value('title'))
                else:
                    w('<td></td>')
                w('<td>%s</td>\n' % field.render(value, REQUEST))
                w('</tr>\n')
            w('</table>\n')
        w('<input type="submit" value=" OK " />\n')
        w(self.footer())
        return result.getvalue()

    security.declareProtected('View', 'render_view')
    def render_view(self, dict=None):
        """Render contents (default simplistic way).
        """
        dict = dict or {}
        result = StringIO()
        w = result.write
        for group in self.get_groups():
            w('<h2>%s</h2>\n' % group)
            w('<table border="0" cellspacing="0" cellpadding="2">\n')
            for field in self.get_fields_in_group(group):
                if field.id in dict:
                    value = dict[field.id]
                else:
                    value = None
                w('<tr>\n')
                w('<td>%s</td>\n' % field.get_value('title'))
                w('<td>%s</td>\n' % field.render_view(value))
                w('</tr>\n')
            w('</table>\n')
        return result.getvalue()

    security.declareProtected('View', 'validate')
    def validate(self, REQUEST):
        """Validate all enabled fields in this form. Stop validating and
        pass up ValidationError if any occurs.
        """
        result = {}
        for field in self.get_fields():
            # skip any fields we don't need to validate
            if not field.need_validate(REQUEST):
                continue
            value = field.validate(REQUEST)
            # store under id
            result[field.id] = value
            # store as alternate name as well if necessary
            alternate_name = field.get_value('alternate_name')
            if alternate_name:
                result[alternate_name] = value
        return result

    security.declareProtected('View', 'validate_to_request')
    def validate_to_request(self, REQUEST):
        """Validation, stop validating as soon as error.
        """
        result = self.validate(REQUEST)
        for key, value in result.items():
            REQUEST.set(key, value)
        return result

    security.declareProtected('View', 'validate_all')
    def validate_all(self, REQUEST):
        """Validate all enabled fields in this form, catch any ValidationErrors
        if they occur and raise a FormValidationError in the end if any
        Validation Errors occured.
        """
        result = {}
        errors = []
        for field in self.get_fields():
            # skip any field we don't need to validate
            if not field.need_validate(REQUEST):
                continue
            try:
                value = field.validate(REQUEST)
                # store under id
                result[field.id] = value
                # store as alternate name as well if necessary
                alternate_name = field.get_value('alternate_name')
                if alternate_name:
                    result[alternate_name] = value
            except ValidationError as err:
                errors.append(err)
        if len(errors) > 0:
            raise FormValidationError(errors, result)
        return result

    security.declareProtected('View', 'validate_all_to_request')
    def validate_all_to_request(self, REQUEST):
        """Validation, continue validating all fields, catch errors.
        Everything that could be validated will be added to REQUEST.
        """
        try:
            result = self.validate_all(REQUEST)
        except FormValidationError as e:
            # put whatever result we have in REQUEST
            for key, value in e.result.items():
                REQUEST.set(key, value)
            # reraise exception
            raise
        for key, value in result.items():
            REQUEST.set(key, value)
        return result

    security.declareProtected('View', 'session_store')
    def session_store(self, session, REQUEST):
        """Store form data in REQUEST into session.
        """
        data = session.getSessionData()
        for field in self.get_fields():
            id = field.id
            data.set(id, REQUEST[id])

    security.declareProtected('View', 'session_retrieve')
    def session_retrieve(self, session, REQUEST):
        """Retrieve form data from session into REQUEST.
        """
        data = session.getSessionData()
        for field in self.get_fields():
            id = field.id
            REQUEST.set(id, data.get(id))

    security.declareProtected('View', 'header')
    def header(self):
        """Starting form tag.
        """
        # FIXME: backwards compatibility; name attr may not be present
        if not hasattr(self, "name"):
            self.name = ""
        name = self.name

        if self.enctype != "":
            if name:
                res = render_tag("form",
                                 name=name,
                                 action=self.action,
                                 method=self.method,
                                 enctype=self.enctype) + ">"
            else:
                res = render_tag("form",
                                 action=self.action,
                                 method=self.method,
                                 enctype=self.enctype) + ">"
        else:
            if name:
                res = render_tag("form",
                                 name=name,
                                 action=self.action,
                                 method=self.method) + ">"
            else:
                res = render_tag("form",
                                 action=self.action,
                                 method=self.method) + ">"
        return (
            '%s\n<input type="hidden" name="formulator_submission"'
            ' value="1" />' % res)

    security.declareProtected('View', 'footer')
    def footer(self):
        """Closing form tag.
        """
        return "</form>"

    security.declareProtected('Change Formulator Forms', 'get_xml')
    def get_xml(self):
        """Get this form in XML serialization.
        """
        return formToXML(self)

    security.declareProtected('Change Formulator Forms', 'set_xml')
    def set_xml(self, xml, override_encoding=None):
        """change form according to xml"""
        XMLToForm(xml, self, override_encoding)

    def _management_page_charset(self):
        """manage_before_header calls this to determine management
        screen encodings.
        """
        if not self.unicode_mode:
            return self.stored_encoding
        else:
            return 'UTF-8'

    # XXX have to use a ComputedAttribute in Zope 2.7, as
    # management_page_charset is not automatically called anymore..
    security.declareProtected('Access contents information',
                              'management_page_charset')
    management_page_charset = ComputedAttribute(_management_page_charset)

    security.declareProtected('View', 'set_encoding_header')
    def set_encoding_header(self):
        """Set the encoding in the RESPONSE object.

        This can be used to make sure a page is in the same encoding the
        textual form contents is in.
        """
        if not self.unicode_mode:
            encoding = self.stored_encoding
        else:
            encoding = 'UTF-8'
        self.REQUEST.RESPONSE.setHeader(
            'Content-Type',
            'text/html;charset=%s' % encoding)


InitializeClass(Form)


class BasicForm(Persistent, Acquisition.Implicit, Form):
    """A form that manages its own fields, not using ObjectManager.
    Can contain dummy fields defined by DummyField.
    """
    security = ClassSecurityInfo()

    def __init__(self, action="", method="POST", enctype="", name="",
                 encoding="UTF-8", stored_encoding='ISO-8859-1',
                 unicode_mode=0):
        BasicForm.inheritedAttribute('__init__')(
            self, action, method, enctype,
            name, encoding, stored_encoding, unicode_mode)
        self.title = 'Basic Form'  # XXX to please FormToXML..
        self.fields = {}

    security.declareProtected('Change Formulator Forms', 'add_field')
    def add_field(self, field, group=None):
        """Add a field to the form to a certain group.
        """
        # update group info
        self.field_added(field.id, group)
        # add field to list
        self.fields[field.id] = field
        self.fields = self.fields

    security.declareProtected('Change Formulator Forms', 'add_fields')
    def add_fields(self, fields, group=None):
        """Add a number of fields to the form at once (in a group).
        """
        for field in fields:
            self.add_field(field, group)

    security.declareProtected('Change Formulator Forms', 'remove_field')
    def remove_field(self, field):
        """Remove field from form.
        """
        # update group info
        self.field_removed(field.id)
        # remove field from list
        del self.fields[field.id]
        self.fields = self.fields

    security.declareProtected('View', 'has_field')
    def has_field(self, id, include_disabled=0):
        """Check whether the form has a field of a certain id.
        If disabled fields are not included, pretend they're not there.
        """
        field = self.fields.get(id, None)
        if field is None:
            return 0
        return include_disabled or field.get_value('enabled')

    security.declareProtected('View', 'get_field')
    def get_field(self, id, include_disabled=0):
        """get a field of a certain id."""
        field = self.fields[id]
        if include_disabled or field.get_value('enabled'):
            return field.__of__(self)
        raise FieldDisabledError("Field %s is disabled" % id, field)

    def _realize_fields(self):
        """Make the fields in this form actual fields, not just dummy fields.
        """
        for field in self.get_fields(include_disabled=1):
            if hasattr(field, 'get_real_field'):
                field = field.get_real_field()
            self.fields[field.id] = field
        self.fields = self.fields


InitializeClass(BasicForm)


def create_settings_form():
    """Create settings form for ZMIForm.
    """
    form = BasicForm('manage_settings')

    title = fields.StringField('title',
                               title="Title",
                               required=0,
                               default="",
                               description="The title of the form.")
    row_length = fields.IntegerField(
        'row_length',
        title='Number of groups in row (in order tab)',
        required=1,
        default=4,
        description="On the order tab, determines the number of groups in each"
                    " row when the form's render function is used")
    name = fields.StringField(
        'name',
        title="Form name",
        required=0,
        default="",
        description="The name of the form.  Indented to be the value of the"
                    " 'name' attribute of the form.  If the name is not the"
                    " default of 'form', it is also the prefix for each"
                    " field's HTML ID")
    action = fields.StringField('action',
                                title='Form action',
                                required=0,
                                default="",
                                description="The action of the form.")
    method = fields.ListField('method',
                              title='Form method',
                              items=[('POST', 'POST'),
                                     ('GET', 'GET')],
                              required=1,
                              size=1,
                              default='POST',
                              description="Form method (i.e. 'POST','GET')")
    enctype = fields.ListField(
        'enctype',
        title='Form enctype',
        items=[
            ('No enctype',
             ""),
            ('application/x-www-form-urlencoded',
             'application/x-www-form-urlencoded'),
            ('multipart/form-data',
             'multipart/form-data')],
        required=0,
        size=1,
        default=None,
        description="The form encoding type.  If any FileField's are present,"
                    " this must be multipart/form-data")

    encoding = fields.StringField('encoding',
                                  title='Encoding of pages the form is in',
                                  default="UTF-8",
                                  required=1,
                                  description="The character set of page.")

    stored_encoding = fields.StringField(
        'stored_encoding',
        title='Encoding of form properties',
        default='ISO-8859-1',
        required=1,
        description="The internal encoding of the form properties")
    unicode_mode = fields.CheckBoxField('unicode_mode',
                                        title='Form properties are unicode',
                                        default=0,
                                        required=1)
    i18n_domain = fields.StringField(
        'i18n_domain',
        title='i18n domain',
        required=0,
        default="",
        description="The i18n translation domain.")

    form.add_fields([title, row_length, name, action, method,
                     enctype, encoding, stored_encoding, unicode_mode,
                     i18n_domain])
    return form


class ZMIForm(ObjectManager, PropertyManager, RoleManager, Item, Form):
    """
    A Formulator Form, fields are managed by ObjectManager.
    """
    meta_type = "Formulator Form"

    security = ClassSecurityInfo()

    # should be helpful with ZClasses, but not sure why I
    # had it in here as a comment in the first place..
    security.declareObjectProtected('View')

    # the tabs we want to show
    manage_options = (
        (
            {'label': 'Contents', 'action': 'manage_main',
             'help': ('Formulator', 'formContents.txt')},
            {'label': 'Test', 'action': 'formTest',
             'help': ('Formulator', 'formTest.txt')},
            {'label': 'Order', 'action': 'formOrder',
             'help': ('Formulator', 'formOrder.txt')},
            {'label': 'Settings', 'action': 'formSettings',
             'help': ('Formulator', 'formSettings.txt')},
            {'label': 'XML', 'action': 'formXML',
             'help': ('Formulator', 'formXML.txt')},
        ) +
        PropertyManager.manage_options +
        RoleManager.manage_options +
        Item.manage_options
    )

    def __init__(self, id, title, unicode_mode=0):
        """Initialize form.
        id    -- id of form
        title -- the title of the form
        """
        ZMIForm.inheritedAttribute('__init__')(self, "", "POST", "", id,
                                               'UTF-8', 'ISO-8859-1',
                                               unicode_mode)
        self.id = id
        if unicode_mode:
            title = ensure_unicode(title)
        self.title = title
        self.row_length = 4

    def all_meta_types(self):
        """Get all meta types addable to this field. The ZMI uses
        this method (original defined in ObjectManager).
        """
        return self._meta_types

    security.declareProtected('View', 'has_field')
    def has_field(self, id, include_disabled=0):
        """Check whether the form has a field of a certain id.
        """
        field = self._getOb(id, None)
        if field is None or not hasattr(aq_base(field), 'is_field'):
            return 0
        return include_disabled or field.get_value('enabled')

    security.declareProtected('View', 'get_field')
    def get_field(self, id, include_disabled=0):
        """Get a field of a certain id
        """
        field = self._getOb(id, None)
        if field is None or not hasattr(aq_base(field), 'is_field'):
            raise AttributeError("No field %s" % id)
        if include_disabled or field.get_value('enabled'):
            return field
        raise FieldDisabledError("Field %s disabled" % id, field)

    security.declareProtected('Change Formulator Forms', 'manage_addField')
    def manage_addField(self, id, title, fieldname, REQUEST=None, **options):
        """Add a new field to the form.
        id        -- the id of the field to add
        title     -- the title of the field to add; this will be used in
                     displays of the field on forms
        fieldname -- the name of the field (meta_type) to add
        Result    -- empty string
        """
        title = title.strip()
        if not title:
            title = id  # title is always required, use id if not provided
        if self.get_unicode_mode():
            # ZMI input is UTF-8 always (?)
            title = ensure_unicode(title)
        # get the field class we want to add
        field_class = FieldRegistry.get_field_class(fieldname)
        # create field instance
        field = field_class(id, title=title, **options)
        # add the field to the form
        id = self._setObject(id, field)
        # respond to add_and_edit button if necessary
        add_and_edit(self, id, REQUEST)
        return ''

    # security declaration for the generic "add field" form,
    # which is set as a class attribute in "initializeForm" later on
    security.declareProtected('Change Formulator Forms', 'fieldAdd')
    def fieldAdd(self):
        """Dummy implementation, set in initializeForm later on.

        This is use to shut up Zope's security warnings. Hopefully it's still
        secure...
        """

    security.declareProtected('View management screens', 'formTest')
    formTest = DTMLFile('dtml/formTest', globals())

    settings_form = create_settings_form()

    security.declareProtected('View management screens', 'formSettings')
    formSettings = DTMLFile('dtml/formSettings', globals())

    security.declareProtected('View management screens', 'formOrder')
    formOrder = DTMLFile('dtml/formOrder', globals())

    security.declareProtected('View management screens', 'formXML')
    formXML = DTMLFile('dtml/formXML', globals())

    security.declareProtected('Change Formulator Forms', 'manage_editXML')
    def manage_editXML(self, form_data, REQUEST):
        """Change form using XML.
        """
        self.set_xml(form_data)
        return self.formXML(self, REQUEST,
                            manage_tabs_message="Changed form")

    security.declareProtected('Change Formulator Forms', 'manage_settings')
    def manage_settings(self, REQUEST):
        """Change settings in settings screen.
        """
        try:
            result = self.settings_form.validate_all(REQUEST)
        except FormValidationError as e:
            message = "Validation error(s).<br />" + "<br />".join(
                ["%s: %s" % (
                    error.field.get_value('title'),
                    error.error_text) for error in e.errors])
            return self.formSettings(self, REQUEST,
                                     manage_tabs_message=message)
        # if we need to switch encoding, get xml representation before setting
        if result['unicode_mode'] != self.unicode_mode:
            xml = self.get_xml()
        # now set the form settings

        # convert XML to or from unicode mode if necessary
        unicode_message = None
        if result['unicode_mode'] != self.unicode_mode:
            # get XML (using current stored_encoding)
            xml = self.get_xml()

            # now save XML data again using specified encoding
            if result['unicode_mode']:
                encoding = 'unicode'
                unicode_message = "Converted to unicode."
            else:
                encoding = result['stored_encoding']
                unicode_message = ("Converted from unicode to %s encoding" %
                                   encoding)
            self.set_xml(xml, encoding)

        # now set the form settings
        for key, value in result.items():
            setattr(self, key, value)
        message = "Settings changed."
        if unicode_message is not None:
            message = message + ' ' + unicode_message
        return self.formSettings(self, REQUEST,
                                 manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms', 'manage_refresh')
    def manage_refresh(self, REQUEST):
        """Refresh internal data structures of this form.
        FIXME: this doesn't work right now
        """
        # self.update_groups()
        REQUEST.RESPONSE.redirect('manage_main')

    security.declarePrivate('_get_field_ids')
    def _get_field_ids(self, group, REQUEST):
        """Get the checked field_ids that we're operating on
        """
        field_ids = []
        for field in self.get_fields_in_group(group, include_disabled=1):
            if field.id in REQUEST.form:
                field_ids.append(field.id)
        return field_ids

    security.declareProtected('View management screens',
                              'get_group_rows')
    def get_group_rows(self):
        """Get the groups in rows (for the order screen).
        """
        row_length = self.row_length
        groups = self.get_groups(include_empty=1)
        # get the amount of rows
        rows = len(groups) // row_length
        # if we would have extra groups not in a row, add a row
        if len(groups) % self.row_length != 0:
            rows = rows + 1
        # now create a list of group lists and return it
        result = []
        for i in range(rows):
            start = i * row_length
            result.append(groups[start: start + row_length])
        return result

    security.declareProtected('View', 'get_largest_group_length')
    def get_largest_group_length(self):
        """Get the largest group length available; necessary for
        'order' screen user interface.
        """
        max = 0
        for group in self.get_groups(include_empty=1):
            fields = self.get_fields_in_group(group)
            if len(fields) > max:
                max = len(fields)
        return max

    security.declareProtected('Change Formulator Forms',
                              'manage_move_field_up')
    def manage_move_field_up(self, group, REQUEST):
        """Moves up a field in a group.
        """
        field_ids = self._get_field_ids(group, REQUEST)
        if (len(field_ids) == 1 and
                self.move_field_up(field_ids[0], group)):
            message = "Field %s moved up." % field_ids[0]
        else:
            message = "Can't move field up."
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_move_field_down')
    def manage_move_field_down(self, group, REQUEST):
        """Moves down a field in a group.
        """
        field_ids = self._get_field_ids(group, REQUEST)
        if (len(field_ids) == 1 and
                self.move_field_down(field_ids[0], group)):
            message = "Field %s moved down." % field_ids[0]
        else:
            message = "Can't move field down."
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_move_group')
    def manage_move_group(self, group, to_group, REQUEST):
        """Moves fields to a different group.
        """
        field_ids = self._get_field_ids(group, REQUEST)
        if (to_group != 'Move to:' and
                self.move_field_group(field_ids, group, to_group)):
            fields = ", ".join(field_ids)
            message = "Fields %s transferred from %s to %s." % (fields,
                                                                group,
                                                                to_group)
        else:
            message = "Can't transfer fields."
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_add_group')
    def manage_add_group(self, new_group, REQUEST):
        """Adds a new group.
        """
        group = new_group.strip()
        if (group and group != 'Select group' and
                self.add_group(group)):
            message = "Group %s created." % (group)
        else:
            message = "Can't create group."
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_remove_group')
    def manage_remove_group(self, group, REQUEST):
        """Removes group.
        """
        if self.remove_group(group):
            message = "Group %s removed." % (group)
        else:
            message = "Can't remove group."
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_rename_group')
    def manage_rename_group(self, group, REQUEST):
        """Renames group.
        """
        if 'new_name' in REQUEST:
            new_name = REQUEST['new_name'].strip()
            if self.rename_group(group, new_name):
                message = "Group %s renamed to %s." % (group, new_name)
            else:
                message = "Can't rename group."
        else:
            message = "No new name supplied."

        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_move_group_up')
    def manage_move_group_up(self, group, REQUEST):
        """Move a group up.
        """
        if self.move_group_up(group):
            message = "Group %s moved up." % group
        else:
            message = "Can't move group %s up" % group
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Change Formulator Forms',
                              'manage_move_group_down')
    def manage_move_group_down(self, group, REQUEST):
        """Move a group down.
        """
        if self.move_group_down(group):
            message = "Group %s moved down." % group
        else:
            message = "Can't move group %s down" % group
        return self.formOrder(self, REQUEST,
                              manage_tabs_message=message)

    security.declareProtected('Add Formulator Fields',
                              'hack_method')
    def hack_method(self):
        """This method does nothing, but is a hack to make
        'Add Formulator Fields' exist in Zope as a permission.
        We need this as we require this permission for the
        addition of fields to forms (necessary in at least
        Zope 2.10)
        """


PythonForm = ZMIForm  # NOTE: backwards compatibility
InitializeClass(ZMIForm)

manage_addForm = DTMLFile("dtml/formAdd", globals())


def manage_add(self, id, title="", unicode_mode=0, REQUEST=None):
    """Add form to folder.
    id     -- the id of the new form to add
    title  -- the title of the form to add
    Result -- empty string
    """
    # add actual object
    id = self._setObject(id, ZMIForm(id, title, unicode_mode))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''


def add_and_edit(self, id, REQUEST):
    """Helper method to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except BaseException:
        u = REQUEST['URL1']
    if hasattr(REQUEST, 'submit_add_and_edit'):
        u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u + '/manage_main')


def initializeForm(field_registry):
    """Sets up ZMIForm with fields from field_registry.
    """
    form_class = ZMIForm

    meta_types = []
    for meta_type, field in field_registry.get_field_classes().items():
        # don't set up in form if this is a field for internal use only
        if field.internal_field:
            continue

        # set up individual add dictionaries for meta_types
        dict = {'name': field.meta_type,
                'permission': 'Add Formulator Fields',
                'action':
                'manage_addProduct/Formulator/manage_add%sForm' % meta_type}
        meta_types.append(dict)
        # set up add method
        setattr(form_class,
                'manage_add%sForm' % meta_type,
                DTMLFile('dtml/fieldAdd', globals(), fieldname=meta_type))

    # set up meta_types that can be added to form
    form_class._meta_types = tuple(meta_types)

    # set up settings form
    form_class.settings_form._realize_fields()
