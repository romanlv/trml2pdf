Open source implementation of RML (Report Markup Language) from ReportLab

[RML User Guide](http://www.reportlab.com/docs/rml2pdf-userguide.pdf)  (or [beginner tutorial](http://www.reportlab.com/docs/rml-for-idiots.pdf))

Not all tags are supported, but most of them work.
 
Install
------- 
`pip install trml2pdf`


Examples
--------

Create a PDF file:

```python
import trml2pdf
print trml2pdf.parseString(file('file.rml','r').read())
```
 
If you are using this for Django you can dynamically create an .rml file with the template system and then render it.


```python
from django.template.loader import get_template
from django.template.context import Context

data = {'key1': 'foo'}
template = get_template('template.rml')
context = Context(data)
xmlstring = template.render(context)
pdfstr = trml2pdf.parseString(xmlstring)
```

# Looking for maintainer 
I no longer use this library in my own projects, so there is no interest in adding new feature or improving things. If you are intersted in taking it over or being actively involved, please let me know
