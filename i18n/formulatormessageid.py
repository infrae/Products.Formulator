from Products.PlacelessTranslationService.MessageID import MessageIDFactory
from Products.PlacelessTranslationService.MessageID import MessageIDUnicode

class FormulatorMessageIDUnicode(MessageIDUnicode):
    """
    """
    __allow_access_to_unprotected_subobjects__ = 1
    def set_mapping(self, mapping):
        """Set a mapping for message interpolation
        """
        self.mapping = mapping

def FormulatorMessageIDFactory(ustr, default=None):
    return FormulatorMessageIDUnicode(ustr, domain='formulator')
    
