import os

from setuptools import setup, find_packages
from stubolib import version_info

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'requests>=2.4.3',
     # Testing dependencies
    'coverage',       
    'nose',          
    'nosexcover',    
    'mock',          
    ]

setup(name='stubolib',
      version=".".join(map(str, version_info)),
      description='Stubo Python Client Library',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        ],
      url='',
      keywords='stubo testing library',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="stubolib",
      entry_points = """\
      [console_scripts]
      """      
      )

