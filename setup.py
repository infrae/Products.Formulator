# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import find_packages
from setuptools import setup


version = '2.0'


tests_require = [
    'Products.PythonScripts < 5.0; python_version=="2.7"',
    'plone.testing',
]


def read_file(filename):
    with open(filename) as data:
        return data.read() + '\n'


setup(name='Products.Formulator',
      version=version,
      description="Form library for Zope 4",
      long_description=(
          read_file("README.rst")
          + read_file("CREDITS.rst")
          + read_file("CHANGES.rst")
      ),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Zope :: 4",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='form generator zope4',
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
          'grokcore.chameleon < 4.0; python_version=="2.7"',  # transitive
          'grokcore.component',
          'grokcore.component < 4.0; python_version=="2.7"',
          'grokcore.view < 4.0; python_version=="2.7"',  # transitive
          'setuptools',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.cachedescriptors',
          'zeam.form.base',
          'zeam.form.base < 1.4; python_version=="2.7"',
      ],
      tests_require=tests_require,
      extras_require={
          'test': tests_require,
      },
      )
