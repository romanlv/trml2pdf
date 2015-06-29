import os
 
from setuptools import find_packages, setup

# http://www.ewencp.org/blog/a-brief-introduction-to-packaging-python/ 

setup(
    name = 'trml2pdf',
    version = '0.2',
    description = 'Tiny RML2PDF is a tool to easily create PDF document without programming.',
    keywords = 'django apps pdf reportlab',
    platforms=["any"],
    license = 'GNU LESSER GENERAL PUBLIC LICENSE',
    author = 'Fabien Pinckaers',
    author_email = 'fp@tiny.be',
    maintainer = 'Roman Lyashov',
    maintainer_email = 'romitch@gmail.com',
    url = 'http://github.com/romanlv/trml2pdf/',
    install_requires = ['reportlab>=2.6'],
    dependency_links = [],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU LESSER GENERAL PUBLIC LICENSE (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(),
    include_package_data = True,
    test_suite="tests",
)

