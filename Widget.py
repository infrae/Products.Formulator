import string
from DummyField import fields
from DocumentTemplate.DT_Util import html_quote
from DateTime import DateTime

class Widget:
    """A field widget that knows how to display itself as HTML.
    """
    
    property_names = ['title', 'description',
                      'default', 'css_class', 'alternate_name',
                      'hidden']

    title = fields.StringField('title',
                               title='Title',
                               description=(
        "The title of this field. This is the title of the field that "
        "will appear in the form when it is displayed. Required."),
                               default="",
                               required=1)

    description = fields.TextAreaField('description',
                                       title='Description',
                                       description=(
        "Description of this field. The description property can be "
        "used to add a short description of what a field does; such as "
        "this one."),
                                       default="",
                                       width="20", height="3",
                                       required=0)
    
    css_class = fields.StringField('css_class',
                                   title='CSS class',
                                   description=(
        "The CSS class of the field. This can be used to style your "
        "formulator fields using cascading style sheets. Not required."),
                                   default="",
                                   required=0)

    alternate_name = fields.StringField('alternate_name',
                                        title='Alternate name',
                                        description=(
        "An alternative name for this field. This name will show up in "
        "the result dictionary when doing validation, and in the REQUEST "
        "if validation goes to request. This can be used to support names "
        "that cannot be used as Zope ids."),
                                        default="",
                                        required=0)
    
    hidden = fields.CheckBoxField('hidden',
                                  title="Hidden",
                                  description=(
        "This field will be on the form, but as a hidden field. The "
        "contents of the hidden field will be the default value. "
        "Hidden fields are not visible but will be validated."),
                                  default=0)

    # NOTE: for ordering reasons (we want extra at the end),
    # this isn't in the base class property_names list, but
    # instead will be referred to by the subclasses.
    extra = fields.StringField('extra',
                               title='Extra',
                               description=(
        "A string containing extra HTML code for attributes. This "
        "string will be literally included in the rendered field."
        "This property can be useful if you want "
        "to add an onClick attribute to use with JavaScript, for instance."),
                               default="",
                               required=0)
      
    def render(self, field, key, value, REQUEST):
        """Renders this widget as HTML using property values in field.
        """
        return "[widget]"
        
    def render_hidden(self, field, key, value, REQUEST):
        """Renders this widget as a hidden field.
        """
        return render_element("input",
                              type="hidden",
                              name=key,
                              value=value)
                              
class TextWidget(Widget):
    """Text widget
    """
    property_names = Widget.property_names +\
                     ['display_width', 'display_maxwidth', 'extra']

    default = fields.StringField('default',
                                 title='Default',
                                 description=(
        "You can place text here that will be used as the default "
        "value of the field, unless the programmer supplies an override "
        "when the form is being generated."),
                                 default="",
                                 required=0)

    display_width = fields.IntegerField('display_width',
                                        title='Display width',
                                        description=(
        "The width in characters. Required."),
                                        default=20,
                                        required=1)

    display_maxwidth = fields.IntegerField('display_maxwidth',
                                           title='Maximum input',
                                           description=(
        "The maximum input in characters that the widget will allow. "
        "Required. If set to 0 or is left empty, there is no maximum. "
        "Note that is client side behavior only."),
                                           default="",
                                           required=0)
   
    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="text",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="text",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))

TextWidgetInstance = TextWidget()

class PasswordWidget(TextWidget):
    
    def render(self, field, key, value, REQUEST):
        """Render password input field.
        """
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))

PasswordWidgetInstance = PasswordWidget()

class CheckBoxWidget(Widget):
    property_names = Widget.property_names + ['extra']

    default = fields.CheckBoxField('default',
                                   title='Default',
                                   description=(
        "Default setting of the widget; either checked or unchecked. "
        "(true or false)"),
                                   default=0)
    
    def render(self, field, key, value, REQUEST):
        """Render checkbox.
        """
        if value:
            return render_element("input",
                                  type="checkbox",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  checked=None,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="checkbox",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  extra=field.get_value('extra'))

CheckBoxWidgetInstance = CheckBoxWidget()

class TextAreaWidget(Widget):
    """Textarea widget
    """
    property_names = Widget.property_names +\
                     ['width', 'height', 'extra']
    
    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)
    
    width = fields.IntegerField('width',
                                title='Width',
                                description=(
        "The width (columns) in characters. Required."),
                                default=40,
                                required=1)

    height = fields.IntegerField('height',
                                 title="Height",
                                 description=(
        "The height (rows) in characters. Required."),
                                 default=5,
                                 required=1)

    def render(self, field, key, value, REQUEST):
        width = field.get_value('width')
        height = field.get_value('height')
            
        return render_element("textarea",
                              name=key,
                              css_class=field.get_value('css_class'),
                              cols=width,
                              rows=height,
                              contents=html_quote(value),
                              extra=field.get_value('extra'))
            
TextAreaWidgetInstance = TextAreaWidget()

class FileWidget(TextWidget):
    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="file",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="file",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))
        
FileWidgetInstance = FileWidget()

class ListWidget(Widget):
    """List widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'size', 'extra']
    
    default = fields.StringField('default',
                                 title='Default',
                                 description=(
        "The default value of the widget; this should be one of the "
        "elements in the list."),
                                 default="",
                                 required=0)

    first_item = fields.CheckBoxField('first_item',
                                      title="Select First Item",
                                      description=(
        "If checked, the first item will always be selected if "
        "no initial default value is supplied."),
                                      default=0)
    
    items = fields.ListTextAreaField('items',
                                     title='Items',
                                     description=(
        "List items in the field. Each row should contain a list "
        "item. Use the | (pipe) character to separate what is shown "
        "to the user from the true value. If no | is supplied, the "
        "shown value for the list item is identical to the true value. "
        "After validation this returns a list of tuples, "
        "where each tuple represents one list element. "
        "The first element of the tuple is a string that is the displayed "
        "name of the list element. The second element of tuple is the "
        "value that will be submitted. If you want to override this "
        "property you will therefore have to create a method that "
        "returns such a list."), 
                                     default=[],
                                     width=20,
                                     height=5,
                                     required=0)
    
    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)

    def render(self, field, key, value, REQUEST):
        # get items
        items = field.get_value('items')
    
        # check if we want to select first item
        if not value and field.get_value('first_item') and len(items) > 0:
            value = items[0][1]
        
        # FIXME: what if we run into multiple items with same value?
        options = []
        for item in items:
            try:
                option_text, option_value = item
            except TypeError:
                option_text = item
                option_value = item
                
            if option_value != value:
                # no selected attribute
                option = render_element('option',
                                        contents=option_text,
                                        value=option_value)
            else:
                # render with 'selected' attribute
                option = render_element('option',
                                        contents=option_text,
                                        value=option_value,
                                        selected=None)
            options.append(option)
    
        return render_element('select',
                              name=key,
                              css_class=field.get_value('css_class'),
                              size=field.get_value('size'),
                              contents=string.join(options, "\n"),
                              extra=field.get_value('extra'))
                              
ListWidgetInstance = ListWidget()

class RadioWidget(Widget):
    """List widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'orientation']
    
    default = fields.StringField('default',
                                 title='Default',
                                 description=(
        "The default value of the widget; this should be one of the "
        "elements in the list."),
                                 default="",
                                 required=0)

    first_item = fields.CheckBoxField('first_item',
                                      title="Select First Item",
                                      description=(
        "If checked, the first item will always be selected if "
        "no initial default value is supplied."),
                                      default=0)
    
    items = fields.ListTextAreaField('items',
                                     title='Items',
                                     description=(
        "List items in the field. Each row should contain a list "
        "item. Use the | (pipe) character to separate what is shown "
        "to the user from the actual value. If no | is supplied, the "
        "shown value for the list item is identical to the actual value."
        "Override this property the same way you'd override "
        "the items property of a ListField."), 
                                     default=[],
                                     width=20,
                                     height=5,
                                     required=0)

    orientation = fields.ListField('orientation',
                                   title='Orientation',
                                   description=(
        "Orientation of the radio buttons. The radio buttons will "
        "be drawn either vertically or horizontally."),
                                   default="vertical",
                                   required=1,
                                   size=1,
                                   items=[('Vertical', 'vertical'),
                                          ('Horizontal', 'horizontal')])
                                   
    def render(self, field, key, value, REQUEST):
        items = field.get_value('items')     

        # check if we want to select first item
        if not value and field.get_value('first_item') and len(items) > 0:
            value = items[0][1]

        css_class = field.get_value('css_class')
        # FIXME: what if we run into multiple items with same value?
        radios = []
        for item in items:
            try:
                radio_text, radio_value = item
            except TypeError:
                radio_text = item
                radio_value = item
                
            if radio_value != value:
                # no selected attribute
                
                radio = render_element('input',
                                       type="radio",
                                       css_class=css_class,
                                       name=key,
                                       value=radio_value)
            else:
                # render with 'checked' attribute
                radio = render_element('input',
                                       type="radio",
                                       css_class=css_class,
                                       name=key,
                                       value=radio_value,
                                       checked=None)
            text = "%s%s" % (radio, radio_text)
            radios.append(text)

        orientation = field.get_value('orientation')
        if orientation == 'horizontal':
            return string.join(radios, "&nbsp;&nbsp;")
        else:
            return string.join(radios, "<br />")
    
RadioWidgetInstance = RadioWidget()

class DateTimeWidget(Widget):
    property_names = Widget.property_names +\
                     ['default_now', 'date_separator', 'time_separator',
                      'input_style', 'input_order',
                      'date_only']

    default = fields.DateTimeField('default',
                                   title="Default",
                                   description=(
        "The default datetime."),
                                   default=None,
                                   display_style="text",
                                   display_order="ymd",
                                   input_style="text",
                                   required=0)

    default_now = fields.CheckBoxField('default_now',
                                       title="Default to now",
                                       description=(
        "Default date and time will be the date and time at showing of "
        "the form (if the default is left empty)."),
                                       default=0)
                                       
    date_separator = fields.StringField('date_separator',
                                        title='Date separator',
                                        description=(
        "Separator to appear between year, month, day."),
                                        default="/",
                                        required=0,
                                        display_width=2,
                                        display_maxwith=2,
                                        max_length=2)

    time_separator = fields.StringField('time_separator',
                                        title='Time separator',
                                        description=(
        "Separator to appear between hour and minutes."),
                                        default=":",
                                        required=0,
                                        display_width=2,
                                        display_maxwith=2,
                                        max_length=2)

    input_style = fields.ListField('input_style',
                                   title="Input style",
                                   description=(
        "The type of input used. 'text' will show the date part "
        "as text, while 'list' will use dropdown lists instead."),
                                   default="text",
                                   items=[("text", "text"),
                                          ("list", "list")],
                                   size=1)

    input_order = fields.ListField('input_order',
                                   title="Input order",
                                   description=(
        "The order in which date input should take place. Either "
        "year/month/day, day/month/year or month/day/year."),
                                   default="ymd",
                                   items=[("year/month/day", "ymd"),
                                          ("day/month/year", "dmy"),
                                          ("month/day/year", "mdy")],
                                   required=1,
                                   size=1)

    date_only = fields.CheckBoxField('date_only',
                                     title="Display date only",
                                     description=(
        "Display the date only, not the time."),
                                     default=0)

    # FIXME: do we want to handle 'extra'?
    
    def render(self, field, key, value, REQUEST):
        # FIXME: backwards compatibility hack:
        if not hasattr(field, 'sub_form'):
            from StandardFields import create_datetime_text_sub_form
            field.sub_form = create_datetime_text_sub_form()
        if value is None and field.get_value('default_now'):
            value = DateTime()
        if value is None:
            year = None
            month = None
            day = None
            hour = None
            minute = None
        else:
            year = value.year()
            month = "%02d" % value.month()
            day = "%02d" % value.day()
            hour = "%02d" % value.hour()
            minute = "%02d" % value.minute()
        
        input_order = field.get_value('input_order')
        if input_order == 'ymd':
            order = [('year', year),
                     ('month', month),
                     ('day', day)]
        elif input_order == 'dmy':
            order = [('day', day),
                     ('month', month),
                     ('year', year)]
        elif input_order == 'mdy':
            order = [('month', month),
                     ('day', day),
                     ('year', year)]
        result = []
        for sub_field_name, sub_field_value in order:
            result.append(field.render_sub_field(sub_field_name,
                                                 sub_field_value, REQUEST))
        date_result = string.join(result, field.get_value('date_separator'))
        if not field.get_value('date_only'):
            time_result = (field.render_sub_field('hour', hour, REQUEST) +
                           field.get_value('time_separator') +
                           field.render_sub_field('minute', minute, REQUEST))
            return date_result + '&nbsp;&nbsp;&nbsp;' + time_result
        else:
            return date_result
                       
DateTimeWidgetInstance = DateTimeWidget()

def render_tag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it.
    """
    attr_list = []

    # special case handling for css_class
    if kw.has_key('css_class'):
        if kw['css_class'] != "":
            attr_list.append('class="%s"' % kw['css_class'])
        del kw['css_class']

    # special case handling for extra 'raw' code
    if kw.has_key('extra'):
        extra = kw['extra'] # could be empty string but we don't care
        del kw['extra']
    else:
        extra = ""

    # handle other attributes
    for key, value in kw.items():
        if value == None:
            value = key
        attr_list.append('%s="%s"' % (key, html_quote(str(value))))
            
    attr_str = string.join(attr_list, " ")
    return "<%s %s %s" % (tag, attr_str, extra)

def render_element(tag, **kw):
    if kw.has_key('contents'):
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (apply(render_tag, (tag,), kw), contents, tag)
    else:
        return apply(render_tag, (tag,), kw) + " />"
         



