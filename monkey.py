from Products.PythonScripts.Utility import allow_class

def monkey_zope3_message_id():
    from zope.i18nmessageid.messageid import MessageID

    # open it up for Zope 2...
    allow_class(MessageID)

def patch_all():
    monkey_zope3_message_id()
    
