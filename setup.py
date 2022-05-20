# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import find_packages
from setuptools import setup


version = '1.16.dev0'


tests_require = [
    'infrae.wsgi [test]',
]


def read_file(filename):
    with open(filename) as data:
        return data.read() + '\n'


setup(name='Products.Formulator',
      version=version,
      description="Form library for Zope 2",
      long_description=read_file("README.rst") +
      read_file("CREDITS.rst") +
      read_file("CHANGES.rst"),
      classifiers=[
          "Framework :: Zope :: 2",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='form generator zope2',
      author='Martijn Faassen and community',
      author_email='info@infrae.com',
      url='https://github.com/infrae/Products.Formulator',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
          'zope.interface',
          'zope.component',
          'zope.i18nmessageid',
          'zope.cachedescriptors',
          'zeam.form.base',
      ],
      tests_require=tests_require,
      extras_require={
          'test': tests_require,
          'zope2': [
              'zeam.form.base < 1.4',
              'five.localsitemanager < 3',
              'grokcore.viewlet < 3',
              'grokcore.annotation < 3',
              'grokcore.site < 3',
              'grokcore.view < 3',
          ]
      },
      )
