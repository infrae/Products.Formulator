import Globals
from AccessControl import ClassSecurityInfo

from Products.FileSystemSite.Permissions import View
from Products.FileSystemSite.FSObject import FSObject
from Products.FileSystemSite.DirectoryView import registerFileExtension,\
     registerMetaType, expandpath

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLSerialize import XMLToForm

class FSForm(FSObject, ZMIForm):
    """FSForm."""

    meta_type = 'Filesystem Formulator Form'

    manage_options = (
        (
        {'label':'Customize', 'action':'manage_main'},
        {'label':'Test', 'action':'formTest'},
        )
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)

    def _createZODBClone(self):
        # not implemented yet
        return None

    def _readFile(self, reparse):
        f = open(expandpath(self._filepath), 'rb')
        # update the form with the xml data
        XMLToForm(f.read(), self)
        f.close()
        
Globals.InitializeClass(FSForm)

registerFileExtension('form', FSForm)
registerMetaType('FSForm', FSForm)
