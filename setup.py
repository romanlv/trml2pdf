import os
 
from distutils.core import setup
 
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == "":
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
 
package_dir = "trml2pdf"
 
packages = []
for dirpath, dirnames, filenames in os.walk(package_dir):
    # ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        packages.append(".".join(fullsplit(dirpath)))
 
setup(
    name = 'trml2pdf',
    version = '0.1',
    description = 'Tiny RML2PDF is a tool to easily create PDF document without programming.',
    keywords = 'django apps pdf reportlab',
    license = 'GNU LESSER GENERAL PUBLIC LICENSE',
    author = 'Fabien Pinckaers',
    author_email = 'fp@tiny.be',
    maintainer = 'Joe Yates',
    maintainer_email = 'joe.g.yates@gmail.com',
    url = 'http://github.com/joeyates/trml2pdf/',
    dependency_links = [],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = packages,
    include_package_data = True,
)

