import Globals
from AccessControl import ClassSecurityInfo

from Products.FileSystemSite.Permissions import View
from Products.FileSystemSite.FSObject import FSObject
from Products.FileSystemSite.DirectoryView import registerFileExtension,\
     registerMetaType, expandpath

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

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
        s = open(expandpath(self._filepath),"rb").read()
	startenc = s.find('encoding="') + len('encoding="')
	xmlencoding = s[startenc:s.find('"',startenc + 2)]
	if xmlencoding.lower() == "utf-8":
	    for e in ("utf-8","iso-8859-1"):
		try:
		    s = unicode(s,e).encode('utf-8') # is it realy utf-encoded
		    break
		except:
		    pass
	    
        # update the form with the xml data
        try:
            XMLToForm(s, self)
        except:
            # bare except here, but I hope this is ok, as the
            # exception should be reraised
            # (except if the LOG raises another one ... should we be more paranoid here?)
            import zLOG
            zLOG.LOG('Formulator.FSForm',zLOG.ERROR,
                     'error reading form from file '+expandpath(self._filepath))
            raise
        

    def old_readFile(self, reparse):
        f = open(expandpath(self._filepath), 'rb')
        # update the form with the xml data
        try:
            XMLToForm(f.read(), self)
        except:
            # bare except here, but I hope this is ok, as the
            # exception should be reraised
            # (except if the LOG raises another one ... should we be more paranoid here?)
            import zLOG
            zLOG.LOG('Formulator.FSForm',zLOG.ERROR,
                     'error reading form from file '+expandpath(self._filepath))
            raise
        
        f.close()
        
Globals.InitializeClass(FSForm)

registerFileExtension('form', FSForm)
registerMetaType('FSForm', FSForm)
