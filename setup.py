# upload
# python setup.py sdist upload -r pypi

import os
from setuptools import setup, find_packages


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='trml2pdf',
    version='0.6',
    description='Tiny RML2PDF is open source implementation of RML (Report Markup Language) from ReportLab',
    keywords='pdf reportlab',
    platforms=["any"],
    license='GNU LESSER GENERAL PUBLIC LICENSE',
    author='Fabien Pinckaers',
    author_email='fp@tiny.be',
    maintainer='Roman Lyashov',
    maintainer_email='romitch@gmail.com',
    url='http://github.com/romanlv/trml2pdf/',
    install_requires=['reportlab>=3.2.0', 'six>=1.9.0'],
    # dependency_links=[],
    include_package_data=True,
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'trml2pdf = trml2pdf:main',
        ],
    },
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
