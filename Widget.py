import string
from DummyField import fields

class Widget:
    """A field widget that knows how to display itself as HTML.
    """
    
    property_names = ['title', 'description',
                      'default', 'widget_name', 'css_class']

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

    widget_name = fields.StringField('widget_name',
                                     title='Widget name',
                                     description=(
        "The name of the field in the form. If left blank, the field "
        "name is constructed from the id instead, which is usually "
        "fine. If however you need field names with special characters in "
        "them that are not accepted in Zope ids, this can be useful. Note "
        "that no check for uniqueness is made, so be careful."),
                                     default="",
                                     required=0)
    
    css_class = fields.StringField('css_class',
                                   title='CSS class',
                                   description=(
        "The CSS class of the field. This can be used to style your "
        "formulator fields using cascading style sheets. Not required."),
                                   default="",
                                   required=0)
    
    def render(self, field, value=None):
        """Renders this widget as HTML using property values in field.
        """
        return "[widget]"
    
class TextWidget(Widget):
    """Text widget
    """
    property_names = Widget.property_names +\
                     ['display_width', 'display_maxwidth']

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
        "Required. If set to 0, there is no maximum. Note that is "
        "client side behavior only."),
                                           default=0,
                                           required=1)
    
    def render(self, field, value=None):
        """Render text input field.
        """
        if value == None:
            value = field.get_value('default')
        display_maxwidth = field.get_value('display_maxwidth')
        if display_maxwidth > 0:
            return render_element("input",
                                  type="text",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth)
        else:
            return render_element("input",
                                  type="text",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'))

TextWidgetInstance = TextWidget()

class PasswordWidget(TextWidget):
    def render(self, field, value=None):
        """Render password input field.
        """
        if value == None:
            value = field.get_value('default')
        display_maxwidth = field.get_value('display_maxwidth')
        if display_maxwidth > 0:
            return render_element("input",
                                  type="password",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth)
        else:
            return render_element("input",
                                  type="password",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'))

PasswordWidgetInstance = PasswordWidget()

class CheckBoxWidget(Widget):
    property_names = Widget.property_names +\
                     []

    default = fields.CheckBoxField('default',
                                   title='Default',
                                   description=(
        "Default setting of the widget; either checked or unchecked. "
        "(true or false)"),
                                   default=0)
    
    def render(self, field, value=None):
        """Render checkbox.
        """
        if value == None:
            value = field.get_value('default')
        if value:
            return render_element("input",
                                  type="checkbox",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'),
                                  checked=None)
        else:
            return render_element("input",
                                  type="checkbox",
                                  name=field.get_field_key(),
                                  css_class=field.get_value('css_class'))

CheckBoxWidgetInstance = CheckBoxWidget()

class TextAreaWidget(Widget):
    """Textarea widget
    """
    property_names = Widget.property_names +\
                     ['width', 'height']
    
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

    def render(self, field, value=None):
        if value == None:
            value = field.get_value('default')
        width = field.get_value('width')
        height = field.get_value('height')
            
        return render_element("textarea",
                              name=field.get_field_key(),
                              css_class=field.get_value('css_class'),
                              cols=width,
                              rows=height,
                              contents=value)
            
TextAreaWidgetInstance = TextAreaWidget()

class ListWidget(Widget):
    """List widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'items_method', 'size']
    
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
        "If an items_method is supplied, the contents of items will "
        "be ignored."), 
                                     default=[],
                                     width=20,
                                     height=5,
                                     required=0)

    items_method = fields.MethodField('items_method',
                                      title='Items Method',
                                      description=(
        "When a method name is supplied, the "
        "field will try to call the (acquired) method of this name. "
        "The method should return a list of tuples. Each tuple is a list "
        "item and should contain two elements. The first element of the "
        "tuple should be the display value, and the second element of the "
        "tuple should be the value of the item. Overrides the "
        "items property if it is supplied. NOTE: "
        "experimental"),
                                      default="",
                                      required=0)
    
    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)
                          
    def render(self, field, value=None):
        if value == None:
            value = field.get_value('default')

        # we always need a string value
        value = str(value)
            
        # call items method if one is supplied, otherwise get default list
        items_method = field.get_value('items_method')
        if items_method:
            items = items_method()
        else:
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
                              name=field.get_field_key(),
                              css_class=field.get_value('css_class'),
                              size=field.get_value('size'),
                              contents=string.join(options, "\n"))
                              
ListWidgetInstance = ListWidget()

def render_tag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it.
    """
    attr_list = []

    # special case handling for css_class
    if kw.has_key('css_class'):
        if kw['css_class'] != "":
            attr_list.append('class="%s"' % kw['css_class'])
        del kw['css_class']
        
    # handle other attributes
    for key, value in kw.items():
        if value == None:
            value = key
        attr_list.append('%s="%s"' % (key, value))
            
    attr_str = string.join(attr_list, " ")
    return "<%s %s" % (tag, attr_str)

def render_element(tag, **kw):
    if kw.has_key('contents'):
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (apply(render_tag, (tag,), kw), contents, tag)
    else:
        return apply(render_tag, (tag,), kw) + " />"
         






