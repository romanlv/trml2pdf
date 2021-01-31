Open source implementation of RML (Report Markup Language) from ReportLab

[![Build Status](https://travis-ci.org/romanlv/trml2pdf.svg?branch=master)](https://travis-ci.org/romanlv/trml2pdf)

[RML User Guide](http://www.reportlab.com/docs/rml2pdf-userguide.pdf)  (or [beginner tutorial](http://www.reportlab.com/docs/rml-for-idiots.pdf))

Not all tags are implemented, but the main ones are. [List of implemented tags](https://github.com/romanlv/trml2pdf/blob/master/doc/Done.md)
 
Install
------- 
`pip install trml2pdf`


Examples
--------

Create a PDF file:

```python
import trml2pdf
print trml2pdf.parseString(open('file.rml','rt').read())
```
 
If you are using this for Django you can dynamically create an .rml file with the template system and then render it.

```python
from django.template.loader import get_template
from django.template.context import Context
import trml2pdf

data = {'key1': 'foo'}
template = get_template('template.rml')
context = Context(data)
xmlstring = template.render(context)
pdfstr = trml2pdf.parseString(xmlstring)
```
