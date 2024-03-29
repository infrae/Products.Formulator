Credits
=======

Developers:

- Martijn Faassen (faassen@vet.uu.nl) -- Main developer, design and
  implementation.

- Clemens Klein-Robbenhaar (robbenhaar at espresto.com) -- Many
  bugfixes and feature additions.

Many thanks go to:

- Kit Blake (kitblake at v2.nl) -- UI help and design help.

- Yury Don (yura at vpcit.ru) -- contributed EmailField and
  FloatField, design and implementation help.

- Stephan Richter (srichter at iuveno-net.de) -- contributed LinkField
  and FileField. Contributed PatternChecker module used by
  PatternField. Other design and implementation help.

- Nicola Larosa (nico at tekNico.net) -- feedback and bugfixes.

- Magnus Heino (magus.heino at rivermen.se) -- feedback and bugfixes.

- Joel Burton (jburton at scw.org) -- feedback and bugfixes.

- Ulrich Eck (ueck at net-labs.de) -- much help and patience with the
  TALES tab.

- Dirk Datzert (Dirk.Datzert at rasselstein-hoesch.de) -- feedback and
  bugfixes.

- Max Petrich (petrich.max at kis-solution.de) -- feedback and
  bugfixes.

- Matt Behrens (matt.behrens at kohler.com) -- feedback and bugfixes.

- Nikolay Kim (fafhrd at datacom.kz) -- code inspiration for
  XMLToForm/FormToXML.

- Godefroid Chapelle (gotcha at swing.be) -- Bugfixes.

- Alan Runyan (runyaga at runyaga.com) -- Fix to email regular expression.

- Sascha Welter (welter at network-ag.com) -- Extensive help with email
  regular expression.

- Christian Zagrodnick (cz at gocept.com) -- Unicode awareness fixes
  and XML entry form.

- Iutin Vyacheslav (iutin at whirix.com) -- am/pm feature for DateTime
  fields.

- Kapil Thangavelu (k_vertigo at objectrealms.net) -- Enabled
  ':record' rendering.

- Pierre-Julien Grizel (grizel at ingeniweb.com) -- ProductForm.

- Sebastien Robin (seb at nexedi.com) -- more consistent ordering in
  XML serialization, bugfixes

- Guido Wesdorp (guido at infrae.com) -- Added extra_item attribute on
  compound fields, bugfixes. Fixed unicode error in XMLToForm.

- Yura Petrov (ypetrov at naumen.ru) -- Various FSForm related
  improvements.

- Vladimir Voznesensky (vovic at smtp.ru) -- Enabling/disabling of fields,
  bugfix in ``render_view``.

- Jeff Kowalczyk -- Whitespace normalization of sources.

- Paul Winkler, Dieter Maurer -- help with fix so that help system
  doesn't cause ZODB writes on every startup.

- Garito (garito at sistes.net) -- bugfix with the XML serialization
  of DateTime values.

- Maciej Pietrzak (magh at apcoh.org) -- Fixes for DateTime validation
  issues in Zope 2.7.

- Patrick Earl (pat at dril.com) -- Fixes for DateTime / CheckBox
  field rendering.

- He Wei (hewei at ied.org.cn) -- ZMI and Unicode related fixes.

- Bertrand Croq (bertrand.croq at freeskop.com) -- Fixes for a Unicode
  issue related to titles of new fields and label for radiobuttons
  patch

- Ian Duggan (ian at swishmark.com) -- "Hide day" in DateTimeField
  feature

- Reinout van Rees (reinout at vanrees.org) -- LabelField validation
  bugfix.

- Mikael Barbero (mikael at emu-france.com) -- ZMI enhancement.

- Michael Howitz (mh at gocept.com) -- Run tests on GitHub Actions.

Special thanks also goes to Rik Hoekstra.

Also a thank you to those few valiant souls who suffered through the
bugs of ZFormulator, the previous implementation. Let's hope this
one's better!
