from setuptools import find_packages, setup

# upload
# python setup.py sdist upload -r pypi
setup(
    name='trml2pdf',
    version='0.5.0',
    description='''Tiny RML2PDF is a tool to easily create PDF document using special HTML-like markup language. It converts a RML, an XML dialect that lets you define the precise appearance of a printed document, to a PDF.''',
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
