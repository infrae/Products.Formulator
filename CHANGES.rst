Changes
=======

2.2 (unreleased)
----------------

- Nothing changed yet.


2.1 (2023-07-31)
----------------

- Port to Python 3, supporting Python 3.7 up to 3.11.


2.0.1 (2023-03-28)
------------------

Bug fixes
+++++++++

- Fix HTML quoting for values containing ``"``.


2.0 (2023-03-14)
----------------

Backwards incompatible changes
++++++++++++++++++++++++++++++

- Remove support for Zope 2 help system.

- Stop testing Zope 2 compatibility. This release should still work with Zope 2
  but the testing infrastructure was modernized to use ``plone.testing``
  instead of ``infrae.testing`` and ``infrae.wsgi`` to be more future proof.
  Expect this to be the last release working on Zope 2.

Features
++++++++

- Support Zope 4.

Other changes
+++++++++++++

- Remove (test) dependencies of ``five.grok``, ``infrae.wsgi`` and
  ``infrae.testing``.

1.16 (2022-06-16)
-----------------

- Run tests in GitHub Actions.

- Fix deprecation warnings.


1.15.5 (2013/10/08)
-------------------

- Fix various unicode issues following the modifications of the 1.15
  series.

1.15.4 (2013/08/26)
-------------------

- ``test_form`` now except a list of bad identifiers for fields as a
  parameter. An error will be returned if one of those identifier is
  used by a field.

- HTML entities are now escaped by default inside field values.

- Formulator Widgets will now return unicode when it is possible.

- ``zeam.form`` extractors have been updated to have the same Acquisition
  wrapping than the ``zeam.form`` widgets.

- Dependencies got properly defined in ``setup.py`` to facilitate the
  installation of the product.

1.15.3 (2013/05/23)
-------------------

- Fix unicode issues with the integration of ``zeam.form``.

- Fix required and readonly attributes with the interface of
  ``zeam.form``.

- Fix ListTextAreaField so it properly works with values from the request.

1.15.2 (2013/03/05)
-------------------

- Fix compability with the latest version of ``zeam.form``.

1.15.1 (2012/12/12)
-------------------

- Don't validate values against criterias when deserializing
  when. This makes impossible to deserialize values that are
  well-formed, but invalid on a given instance, loosing all
  information by doing so.

1.15 (2012/09/04)
-----------------

- Add support to integrate with ``zeam.form``.

- Add support for validators to validate already extracted values from
  the request.

- Some level of validation can be disabled when extracting values from
  the request, if a value with the id ``field.id_novalidate`` is
  present as well in the request. This is usefull to extract form
  values from a request intended for an older version of your form.

1.14 (2011/11/10)
-----------------

- Compatibility fixes for Zope 2.13 and Python 2.7.

- DateTime widget now support datetime values.

- Add a method ``test_form`` on a Form to know if it is broken (have
  ZODB broken fields, or other problems).

- Add a way to programmatically change all fields options for a form.

- Add support to serialize/deserialize form values on a content
  object (see the adapters code).

- TAL expressions in fields now have access to a context value: the
  acquisition parent of the form.

- Add some fields that where somewhere else in the past,
  EmailLinesField and an InterfaceField.

- Add support for interfaces in XML import/export, for an interface
  field.

- Support for FileSystemSite is optional.

1.13 (2010/07/15)
-----------------

- Compatibility fixes for Zope 2.12 and Python 2.6. Those are the
  requirements now.

Ported from 1.11 branch:

- Fix problem with MultiListFields not showing values from request
  if in unicode mode, as the incoming values from the request
  did not get converted to unicode in the Field._get_default

- The "convert_unicode" helper now expects a separate parameter
  "encoding" instead of assuming utf8 encoding always.


Ported from 1.12 branch:

- The majority of Widgets now auto-generate an html 'id' attribute for the
  rendered widget.  This 'id' attribute is accessible in page templates via
  the field/html_id.  If the field has an id attribute set in the 'extra'
  parameter, the value of this attribute is returned, rather than the
  auto-generated id.  The html id and name attributes are now visible
  in the ZMI edit screen for the fields.  The widgets which do not have
  html_ids are: RadioWidget, MultiCheckBoxWidget, DateTimeWidget.  The widgets
  have a property "has_html_id" that templates can use to determine whether
  to place a label around the field title.


1.11.6 (2009/11/11)
-------------------
- Added the option for the DateTime Widget to use a popup calendar to input
  the date and time.

- The DateTime Widget popup defaults to midnight for the time.

- The DateTime Widget now understands both upper and lower case 'am' and 'pm'.

- Fix the factor that a REQUEST is required to use a field object on
  recent Zope (2.11).

- Fixed field events: copy of forms containing fields and folders
  containing forms was broken.

- Added a 'required' validator property to FileFields

- Added a validator for FileFields to check whether the value is a
  StringType, which is an indicator that the form encoding is set
  incorrectly.  The error message informs the user the form
  encoding should be set to multipart/form-data.

- Property descriptions are now displayed on the edit tab.  These already existed
  but were never exposed in the ZMI.

1.11.5 (2008/30/09)
-------------------

- Reformat documentation to ReST to release an egg.

1.11.4
------

Bugs fixed:

- Zope i18n *needs* an 'en' directory, or browsers like firefox will
  use the first language in the language preferences list that does
  have a translation, even if english is above it in the list of
  preferences.

- Tainted strings caused instance error, converted tainted strings
  back to strings.

- Small fix to Selection Field Validators, whose 'validate' functions
  failed if items values are stored as unicode

- update imports needed by the file system Formulator form
  representation, if CMF is installed.  Now both CMF 1.x (for Plone
  2.x) and CMF 2.x (for Plone 3.x) should work.  Patch provided by
  "lcanacheu".

- checkbox fields and multicheckboxfield items are now rendered with
  labels around them.

1.11.3
------

Bugs fixed:

- Field Validators 'validate' functions did not accept unicode
  values as input on fields that require unicode.

- Zope 2.10 compatibility: "MessageIDFactory" got renamed to
  "MessageFactory"; same for "MessageID"; the monkey to allow
  this class got influenced, too, so all ZODB importing that
  class need to be updated, too (Problem reported by Yinghoong
  Chan and Josef Meile)

- Zope 2.10 event handling. Formulator now uses Zope 3 style
  event handling so that no deprecation warnings are seen
  anymore.

- in Zope 2.10 copy & paste of fields did not work anymore, as
  apparently Zope now requires permission info in the data
  structure returned by all_meta_types. We have created a new
  permission "Add Formulator Fields" which is checked when you
  create a formulator field, or copy & paste it.

  Note that there is still a "cosmetic" security issue if a
  non-manager user tries to add a formulator field. "Add and
  Edit" works, but "Add" gives a login dialog. Actually the
  field *did* get added, but the URL to which the system tries
  to return afterwards does not allow access.

1.11.2
------

Bugs fixed:

- Copied fix from the 1.10 branch, TypeError when passing something other
  than a string into the Validator.

1.11.1
------

Bugs fixed

- Shut up startup warnings about security declarations in Zope
  2.8.5.

1.11
----

Features Added:

- Formulator now needs Zope 2.8.4 + Five 1.2. It uses Five's i18n
  architecture instead of PlacelessTranslationService.  Five 1.2 can
  be downloaded at http://codespeak.net/z3/five

  If you do not want to install Five 1.2 for some reason, simply
  remove 'configure.zcml' in the Formulator package. Formulator will
  then work (but not have i18n support) in a plain Zope 2.8
  installation.

- Radiobuttons are now rendered with a label around their field value,
  allowing to click on the value instead of the radio button itself.
  (Patch from Bertrand Croq).

Bugs fixed:

- Fixed unicode issues in FormToXML, when the form was in unicode mode
  and message fields contained non-ascii chars, XML serialization
  didn't work.

1.10
----

Features Added:

- Allow to group fields of the ZMI form for each field
  into more groups than the default "widget" and "validator"
  (Patch from Mikael Barbero)

Bugs fixed:

- Fixed AttributeError (on __call__) on DummyMessageID.

1.9.0
-----

Features Added:

- Added the 'modules' namespace for TALES expresions.

- when reordering a field in the "Order" tab the current field
  is "sticky" for faster moving up and down.
  (Patch from Sebastien Robin)

- Addes serializeValue and deserializeValue methods to the
  validator classes. The former takes a sax handler as an argument
  and sends it sax events to serialize the field value, the latter
  takes serialized values and massages them back into valid formulator
  values. These methods are not used within formulator itself, and
  introduce no new dependencies.

- A new flag to the DateTimeField widget allows to hide the day,
  allowing to specify month and year only. The day defaults to the
  first day of the month in this case.
  (Patch from Ian Duggan)

Bugs Fixed:

- Fixed issue for render_view of list fields with no default
  value.

- Fixed issue with non-ascii characters in the title of a newly
  created form or field if the unicode property has been set
  (Patch from Bertrand Croq)

- Calling "validate" on LabelField directly failed with a
  KeyError: 'external_validator' (Patch from Reinout van Rees)

- A PatternField may have returned garbled results if the pattern
  has several 'e' or 'f' in the pattern and 'd', 'e' of 'f' in the
  field value

1.8.0
-----

Features Added:

- Remove i18n prefix and message id generation strategy from
  Formulator.  It is cleaner to do this with i18n:translate in
  ZPT. Extraction of messages can be done from .form XML files
  (though this functionality is not yet part of Formulator).

- Introduce message id markers and .po file for Formulator generated
  error messages. These can be made translated in your own
  page templates like this::

     <p i18n:domain="formulator" i18n:translate=""
        tal:content="my_error_text"></p>

- Test framework now uses (and requires) ZopeTestCase. This allowed
  some testing setup cruft to be removed.

Bugs Fixed:

- Added explicit security declaration for the "fieldAdd" DTML-file.
  This fixed a problem with copy & paste fields in Zope 2.7.3.

- Fields having been removed via the XML tab in the ZMI still
  showed up in the "Contents" tab.

- As a convenience TALES expressions now may return "None" for
  the default value, which is rendered as the empty string.
  (previously it has been rendered as "value".)

1.7.0
-----

Features Added:

- Added FormulatorFormFile, which can be used to load XML
  representations of forms from filesystem code like PageTemplateFile.

- i18n-id and i18n-domain support for forms, including descriptions,
  error-messages, etc.

Bugs Fixed:

- changed way selection fields check whether their items property is a
  list or single item.

- Made system not reregister help for Fields which already have help,
  to avoid ZODB writes on startup.

- Fixed singleton submit button that wasn't properly closed.

- Zope 2.7 compatibility: In Zope 2.7 the behaviour when trying to
  construct invalid DateTime object changed from raising string
  exceptions to class based exceptions. This has caused the
  DateTimeField's to pass through the new exceptions instead of
  converting them to ValidationError.

- PatternFields are no longer documented as "experimental" in the Help
  system.

- DateTime values field values (like start or end time) have been
  wrongly represented as strings in the XML representation.

- Fixed bug with rendering of ListField's similar to the "single
  element list with one two-char string" bug fixed for validation in
  1.6.2.

- Fixed bug in DateTime field where a set "default to now" overwrote
  values in the request.

- Severel spelling bugs.

- Fixed bug where a set "default" for a checkbox field would always
  render a checked checkbox, even if redisplaying a submitted form
  where the user has unchecked the checkbox Actually the works only if
  the opening ``<form>`` tag is rendered by the ``form.header()`` method, or
  if a hidden field "formulator_submission" is included manually in
  the form.

- Added tests for the LinesValidator.

- Fixed bug with ``render_from_request`` LinesField, which splitted
  strings coming in as raw unvalidated data from the request into many
  lines with one single character on each line

- Fixed bug where entering non ascii values in the ListField items has
  not been handled properly in unicode mode

- Worked around Zope2.7/python2.3 compatibility bug.  If a character
  like "<" has inserted in a string field this triggered an obscure
  Zope bug when feeding this value into the ``string.strip()`` function
  on validation.


1.6.2
-----

Bugs Fixed:

- Fixed bug which caused validation of listfields to throw an
  exception when a list of strings was used as the value of
  ``<items>`` and one of the elements was 2 characters long.

- Formulator should now work again in Zope 2.7; Zope 2.7 has a change
  to the way it retrieved the character set it used to to display the
  ZMI. This interacted badly with the recent changes in Formulator to
  support unicode.

- Added 'refresh.txt'. I don't consider it a bug if this doesn't work
  for you though -- I'm not using it. :)

- XML representation of method-values attributes did not work.

- python 2.1.3 compatibility: boolean values like "required" are
  translated to int on XML serializations/deserialization.

  The last two fixes are due to Sebastien Robin

- render_hidden of DateTimeField's and fields allowing multiple
  selections did not lead to something useful for validation.

- RadioField and ListField did not display the text but the value in
  ``render_view``.

Other:

- Whitespace normalization in sources.

1.6.1
-----

Bugs Fixed:

- Adding Fields to empty Groups had not been possible.

- ZMI "Order" tab of an empty form did raise an exception.

1.6.0
-----

Features Added:

- FileSystemSite/DirectoryView improvements:

  * XML filesystem representation of Formulator forms can now
    also be used with CMF (if FileSystemSite is not installed).

  * FSForm gets automatically registered with the directory
    view system if CMF or FileSystemSite is installed.

- Infrastructure for Validators not to get taken into account in
  validation procedures (``need_validate``).

- A new label field. Doesn't participate in validation. It shows
  its text as a label in the form.

- Unicode mode. A form can now be put in 'unicode mode', which
  means it stores all its textual data as unicode strings. This
  allows for easier integration with Zope systems that use unicode
  internally, such as Silva.

- Disabling of fields. A field can now be disabled from being
  displayed or validated by unchecking the 'Enabled' validator
  property. This can be done dynamically as well using TALES
  overrides.

Bugs Fixed:

- The css_class value of a DateTime field had been ignored.  It
  is now properly passed down to its subfields, so all subfield
  elements are rendered with the given css_class value.

1.5.0
-----

Features Added:

- Added ProductForm, which provides a wrapping around
  Formulator.BasicForm, allowing it to be created inside a
  product but used outside it.

- Allow turning off of XML prologue section.

- Optimization of TALESMethod by caching compiled expression.
  This speeds SilvaMetadata indexing up by a lot if a fallback
  on default is made, especially in the case of Python
  expressions, as it avoids lots of compilation overhead.

- Extra attribute defined for list/multicheckbox/radio fields
  called 'extra_item', which allows setting HTML attributes to
  individual list item/checkbox/radio button.

Bugs Fixed:

- XML serialization should be more consistent now; field properties
  are now ordered by name upon serialization.

- Allow XML export of BasicForm.

1.4.2
-----

Bugs Fixed:

- Sticky forms should now work correctly in the presence of unicode.
  Encoded data is automatically converted to unicode if the information
  is pulled from the REQUEST form.

1.4.1
-----

Bugs Fixed

- It was not possible to make DateTime fields not required when
  ``allow_empty_time`` was enabled. Fixed.

1.4.0
-----

Features Added

- Added limited ability to output unicode for selected
  fields. Only works properly in Zope 2.6.x, and the HTML pages
  these forms are in need an output encoding set (such as
  UTF-8, which is also Formulator's default encoding). If
  'unicode' checkbox is checked Formulator will try to interpret
  its input in the Form's encoding (default is UTF-8). It will
  also try to display its values in that encoding. Note that
  only field values and items currently work with unicode -- the
  rest of the textual properties of a field are still stored as
  8-bits. If you make sure that these properties are encoded as
  UTF-8 (or whatever encoding you choose for the form) things
  should be okay, however.

- Can now also change forms using XML (not just view it).

- DateTime fields can now optionally input AM/PM.

- DateTime fields can now optionally be set to allow time to
  be left empty.

- 'whitespace_preserve' option on string type fields. If turned on,
  whitespace will not be automatically stripped and will count as
  input.

- 'render_view' method on fields to render the value outside a
  widget.

- Added some code support used by SilvaMetadata to enable rendering
  of fields with Zope's ':record' syntax.

Bugs Fixed:

- Fixed a Python2.2 compatibility bug in ``XMLObjects.py``.

- DateTimeField now picks up default values from REQUEST
  properly if necessary.

- XML representation of the LinkField "check_timeout" value
  messed the type="float" attribute.

- Additional unit tests.

1.3.1 (2002/12/20)
------------------

Features Added:

- Error messages can now be included in the XML serialization.

- Ability to encode lists as a special type in values.

Bugs Fixed:

- Some more proper encodings.

- Handle case where group has no field.

- Handle DateTime field better.

1.3.0 (2002/11/26)
------------------

Features Added:

- FormToXML and XMLToForm modules have functions to serialize
  (most of) form to XML and read it in again (over an existing
  form).

- New XML tab for forms which shows the XML serialization (no
  saving option yet).

- FSForm.py uses XML serialization to provide a formulator form
  version for FileSystemSite. It does not get imported by
  default.

Bugs Fixed:

- The email validator has an improved regular expression.

- Fix error that occured when trying to render DateTimeField as
  hidden.

1.2.0 (2002/03/06)
------------------

Features Added:

- Changes to exception infrastructure so errors can now be
  imported and caught in a through the web Python script. Example::

    from Products.Formulator.Errors import ValidationError, FormValidationError

- added ``__getitem__`` to Field so instead of using ``get_value()`` you can
  also do this in Python: form.field['title'], and in ZPT you can
  use this in path expressions: form/field/title

- made a start with Formulator unit tests; some validators get
  automatically tested now.

Bugs Fixed:

- Removed dependencies of the name of 'Add and Edit' button to make
  internationalization of the management interface easier.

- added permission to make ZClasses work a bit better (but they
  still don't cooperate well with Formulator, I think. I don't use
  ZClasses, so I hope to hear from this from ZClass users)

- Form's properties tab now visible and form tabs stopped
  misbehaving.

- Lists and such should handle multiple items with the same value
  a bit better, selecting only one.

- the LinkField now checks site-internal links better.

1.1.0 (2001/10/26)
------------------

Bugs Fixed:

- Fixed bug in form settings tab.

- the LinkField now checks site-internal links better.

1.0.9 (2001/10/05)
------------------

Features Added:

- New TALES tab for fields as a more powerful Override tab;
  PageTemplates needs to be installed to make it work.

- added 'name' attribute for forms. When the form header is
  rendered, name will be an attribute. This can be used to
  control forms with Javascript.

Bugs Fixed:

- More compliance with Zope product guidelines; moved dtml
  files from www dir to dtml dir.

- Fixed a bug in that form titles would not work. Forms now have
  titles, and you can change them in the settings tab. (Formulator
  does not use the title property internally though)

1.0.1 (2001/07/27)
------------------

Bugs Fixed:

- Fixed bug with renaming groups. Previously, renamed groups were not
  properly stored in the ZODB.

- Made MultiSelectionValidator (used by MultiListField among others)
  deal better with integer values.

- Hacked around CopySupport changes in Zope 2.4.0; renames work
  again now.

1.0 (2001/07/10)
----------------

Features Added:

- New field: RawTextAreaField. A textarea field that doesn't
  do a lot of processing on the text input.

- Checked in BSD license text.

Bugs Fixed:

- Fixed minor bug in year handling of DateTimeField.

- Now hidden fields also take text from 'extra' property.

- Fixed bug in MultiItemsWidget; would not deal with only a
  single item being selected.

0.9.5 (2001/06/27)
------------------

Features Added:

- Added FileField (with browse button). Can be used to upload
  files if form is set to multipart/form-data.

- Added LinkField for URLs.

- Made ListField and RadioField more tolerant of integer
  (and possibly other) values, not only strings.

- Made ListField and RadioField happy to deal with non-tuples too in the
  items list. In this case, the item text and value will be identical.

- Refactored ListWidget and RadioWidget so they share code; they both
  inherit from SingleItemsWidget now.

- Added LinesField to submit a list of lines in a textarea.

- Added MultiListField and MultiCheckBoxField, both use new
  MultiItemsWidget and MultiSelectionValidator.

- Added EXPERIMENTAL PatternField.

0.9.4 (2001/06/20)
------------------

Features Added:

- Added API docs for Form, BasicForm and ZMIForm.

- Renamed the confusingly named PythonForm and PythonField to
  ZMIForm and ZMIField, as they are used from the Zope Management
  Interface and not from Python.

- Added render() method to form for basic form rendering.

- Added Formulator HOWTO document.

Bugs Fixed:

- Removed some validation code that wasn't in use anymore (items_method).

- Removed 'has_field_id' in Form as this duplicated
  the functionality of 'has_field'.

- Turned <br> in Python sources to <br /> for XHTML compliance.

- Tweaked radiobutton; text is now closer to the button itself,
  different buttons are further apart.

0.9.3 (2001/06/12)
------------------

Features Added:

- added RadioField for simple display of radio buttons.

- added action, method and enctype property to form settings.
  These are displayed using the special form.header() and form.footer()
  methods.

- added override tab to allow all properties to be overridden by
  method calls instead. 'items_method' in ListField went
  away.

- added ability to display DateTimeFields using drop down lists
  instead of text input. Added some other bells and whistles to
  DateTimeField. Changed some of the inner workings of composite
  fields; component fields are now unique per field instance
  instead of shared between them.

- is_required() utility method on field to check whether a field
  is required.

- some internal features, such the ability to have a method
  called as soon as a property has changed.

Bugs Fixed:

- Fixed typos in security assertions.

- use REQUEST.form instead of REQUEST where possible.

- display month and day with initial zero in DateTimeField.

- Fixed bug in validate_all_to_request(); what can be validated
  will now be added to REQUEST if possible, even if a
  FormValidationError is raised.

0.9.2 (2001/05/23)
------------------

Features Added:

- Ability to rename groups, including the first 'Default' group.

- Improved support for sticky forms; form.render() can now
  take an optional second argument, REQUEST, which can come
  from a previous form submit. Even unvalidated fields will
  then be sticky.

- fields can call an extra optional external validation
  function (such as a Python script).

- New alternate name property: the alternate name is added to
  the result dictionary or REQUEST object after validation. This
  can be useful to support field names which wouldn't be valid
  field names, which can occur in some locales.

- New extra property; can be used to add extra attributes to
  a HTML tag.

- Some IntegerField properties can now be left empty if
  no value is required, instead of having to set them to 0.

- Merged functionality of RangedIntegerField into IntegerField.
  RangedIntegerField is not addable anymore, though supported
  as a clone of IntegerField for backwards compatibility. Leaving
  'start' and 'end' empty in the new IntegerField will mean those
  checks will not be performed.

Bugs Fixed:

- Added more missing security declarations.

- html_quote added in various places to make fields display
  various HTML entities the right way.

0.9.1 (2001/05/13)
------------------

Features Added:

- Widgets now have a 'hidden' property. If set, the widget is
  drawn as a 'hidden' field. 'hidden' fields do get validated
  normally, however.

- Changed API of Widget and Validator slightly; render() and
  validate() methods now take an extra 'key' argument indicating
  the name the field should have in the form. This is necessarily
  to handle sub fields of composite fields.

- Added EmailField and FloatField.

- Added some infrastructure to support 'composite fields'; fields
  composed out of multiple sub fields.

- Added DateTimeField, the first example of a composite field
  (field made of other fields).

Bugs Fixed:

- General code cleanups; removed some unused methods.

- Fixed security assertion for validate_all_to_request() method.

- MethodFields now check whether they have 'View' permission to
  execute listed Python Script or DTML Method.

- RangedInteger is now < end, instead of <=, compatible with the
  documentation.

0.9 (2001/04/30)
----------------

- Initial public release of Formulator.
