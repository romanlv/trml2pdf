from setuptools import find_packages, setup


# http://www.ewencp.org/blog/a-brief-introduction-to-packaging-python/
setup(
    name='trml2pdf',
    version='0.4.1',
    description='''Tiny RML2PDF is a tool to easily create PDF document using special HTML-like markup language. 
It can be used as a Python library or as a standalone binary. It converts a RML, an XML dialect that lets you define the precise appearance of a printed document, to a PDF. You can use your existing tools to generate an input file  that exactly describes the layout of a printed document, and RML2PDF converts it into PDF. RML is a much more powerfull and flexible alternative to XSL:FO.
The executable read a RML file to the standard input and output a PDF file to the standard output.''',
    keywords='pdf reportlab',
    platforms=["any"],
    license='GNU LESSER GENERAL PUBLIC LICENSE',
    author='Fabien Pinckaers',
    author_email='fp@tiny.be',
    maintainer='Roman Lyashov',
    maintainer_email='romitch@gmail.com',
    url='http://github.com/romanlv/trml2pdf/',
    install_requires=['reportlab>=3.2.0', 'six>=1.9.0'],
    dependency_links=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'trml2pdf = trml2pdf.trml2pdf:main',
        ],
    },

    packages=find_packages(),
    include_package_data=True,
    test_suite="tests",
)
