# -*- coding: utf-8 -*-

# trml2pdf - An RML to PDF converter
# Copyright (C) 2003, Fabien Pinckaers, UCL, FSA
# Contributors
#     Richard Waid <richard@iopen.net>
#     Klaas Freitag <freitag@kde.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# 1. system
import sys
from six import text_type
# 2. 3rd parties
from reportlab import platypus
from reportlab.graphics.barcode import code39
import reportlab
# 3. local
from . import canv, utils


def _child_get(node, childs):
    clds = []
    for n in node.childNodes:
        if (n.nodeType == n.ELEMENT_NODE) and (n.localName == childs):
            clds.append(n)
    return clds


class RmlFlowable(object):

    def __init__(self, doc):
        self.doc = doc
        self.styles = doc.styles

    def __name(self, node):
        self.styles.names[node.getAttribute('id')] = node.getAttribute('value')

    def _textual(self, node):
        rc = ''
        for n in node.childNodes:
            if n.nodeType == node.ELEMENT_NODE:
                if n.localName == 'getName':
                    new_node = self.doc.dom.createTextNode(
                        self.styles.names.get(n.getAttribute('id'), 'Unknown name'))
                    node.insertBefore(new_node, n)
                    node.removeChild(n)
                if n.localName == 'pageNumber':
                    rc += '<pageNumber/>'  # TODO: change this !
                else:
                    self._textual(n)
                rc += n.toxml()
            elif n.nodeType == node.CDATA_SECTION_NODE:
                rc += n.data
            elif n.nodeType == node.TEXT_NODE:
                rc += n.toxml()
        return text_type(rc)

    def _list(self, node):
        if node.hasAttribute('style'):
            list_style = self.styles.list_styles[node.getAttribute('style')]
        else:
            list_style = platypus.flowables.ListStyle('Default')

        list_items = []
        for li in _child_get(node, 'li'):
            flow = []
            for n in li.childNodes:
                if n.nodeType == node.ELEMENT_NODE:
                    flow.append(self._flowable(n))
            if not flow:
                if li.hasAttribute('style'):
                    li_style = self.styles.styles[
                        li.getAttribute('style')]
                else:
                    li_style = reportlab.lib.styles.getSampleStyleSheet()['Normal']

                flow = platypus.paragraph.Paragraph(self._textual(li), li_style)

            list_item = platypus.ListItem(flow)
            list_items.append(list_item)

        return platypus.ListFlowable(list_items, style=list_style, start=list_style.__dict__.get('start'))

    def _table(self, node):
        length = 0
        colwidths = None
        rowheights = None
        data = []
        for tr in _child_get(node, 'tr'):
            data2 = []
            for td in _child_get(tr, 'td'):
                flow = []
                for n in td.childNodes:
                    if n.nodeType == node.ELEMENT_NODE:
                        flow.append(self._flowable(n))
                if not len(flow):
                    flow = self._textual(td)
                data2.append(flow)
            if len(data2) > length:
                length = len(data2)
                for ab in data:
                    while len(ab) < length:
                        ab.append('')
            while len(data2) < length:
                data2.append('')
            data.append(data2)
        if node.hasAttribute('colWidths'):
            assert length == len(node.getAttribute('colWidths').split(','))
            colwidths = [
                utils.unit_get(f.strip()) for f in node.getAttribute('colWidths').split(',')]
        if node.hasAttribute('rowHeights'):
            rowheights = [
                utils.unit_get(f.strip()) for f in node.getAttribute('rowHeights').split(',')]
        table = platypus.Table(data=data, colWidths=colwidths, rowHeights=rowheights, **(
            utils.attr_get(node, ['splitByRow'], {'repeatRows': 'int', 'repeatCols': 'int'})))
        if node.hasAttribute('style'):
            table.setStyle(
                self.styles.table_styles[node.getAttribute('style')])
        return table

    def _illustration(self, node):
        class Illustration(platypus.flowables.Flowable):

            def __init__(self, nod, styles):
                self.node = nod
                self.styles = styles
                self.width = utils.unit_get(nod.getAttribute('width'))
                self.height = utils.unit_get(nod.getAttribute('height'))

            def wrap(self, *args):
                return self.width, self.height

            def draw(self):
                # canvas = self.canv
                drw = canv.RmlDraw(self.node, self.styles)
                drw.render(self.canv, None)

        return Illustration(node, self.styles)

    def __keep_in_frame(self, node):
        kwargs = {
            "maxWidth": 0,
            "maxHeight": 0,
            "content": self.render(node),
        }
        mode = node.getAttribute("onOverflow")
        if mode:
            kwargs["mode"] = mode
        name = node.getAttribute("id")
        if name:
            kwargs["name"] = name
        kwargs.update(
            utils.attr_get(node, ['maxWidth', 'maxHeight', 'mergeSpace'],
                           {'maxWidth': 'int', 'maxHeight': 'int'}))
        return platypus.KeepInFrame(**kwargs)

    def _flowable(self, node):
        """
        FIXME: mk dict
        """
        if node.localName == 'para':
            return platypus.Paragraph(self._textual(node), self.styles.para_style_get(node), **(utils.attr_get(node, [], {'bulletText': 'str'})))
        elif node.localName == 'name':
            return self.__name(node)
        elif node.localName == 'xpre':
            return platypus.XPreformatted(self._textual(node), self.styles.para_style_get(node), **(utils.attr_get(node, [], {'bulletText': 'str', 'dedent': 'int', 'frags': 'int'})))
        elif node.localName == 'pre':
            return platypus.Preformatted(self._textual(node), self.styles.para_style_get(node), **(utils.attr_get(node, [], {'bulletText': 'str', 'dedent': 'int'})))
        elif node.localName == 'illustration':
            return self._illustration(node)
        elif node.localName == 'blockTable':
            return self._table(node)
        elif node.localName == 'title':
            return platypus.Paragraph(self._textual(node), reportlab.lib.styles.getSampleStyleSheet()['Title'], **(utils.attr_get(node, [], {'bulletText': 'str'})))
        elif node.localName == 'h1':
            return platypus.Paragraph(self._textual(node), reportlab.lib.styles.getSampleStyleSheet()['Heading1'], **(utils.attr_get(node, [], {'bulletText': 'str'})))
        elif node.localName == 'h2':
            return platypus.Paragraph(self._textual(node), reportlab.lib.styles.getSampleStyleSheet()['Heading2'], **(utils.attr_get(node, [], {'bulletText': 'str'})))
        elif node.localName == 'h3':
            return platypus.Paragraph(self._textual(node), reportlab.lib.styles.getSampleStyleSheet()['Heading3'], **(utils.attr_get(node, [], {'bulletText': 'str'})))
        elif node.localName == 'image':
            return platypus.Image(node.getAttribute('file'), mask=(250, 255, 250, 255, 250, 255), **(utils.attr_get(node, ['width', 'height', 'preserveAspectRatio', 'anchor'])))
        elif node.localName == 'spacer':
            return platypus.Spacer(width=utils.unit_get(node.getAttribute('width') if node.hasAttribute('width') else '1cm'), height=utils.unit_get(node.getAttribute('length')))
        elif node.localName == 'barCode':
            return code39.Extended39(self._textual(node))
        elif node.localName in ['pageBreak', 'nextPage']:
            return platypus.PageBreak()
        elif node.localName == 'condPageBreak':
            return platypus.CondPageBreak(**(utils.attr_get(node, ['height'])))
        elif node.localName == 'setNextTemplate':
            return platypus.NextPageTemplate(str(node.getAttribute('name')))
        elif node.localName == 'nextFrame':
            return platypus.CondPageBreak(1000)  # TODO: change the 1000 !
        elif node.localName == 'ul':
            return self._list(node)
        elif node.localName == 'keepInFrame':
            return self.__keep_in_frame(node)
        else:
            sys.stderr.write(
                'Warning: flowable not yet implemented: %s !\n' % (node.localName,))

    def render(self, node_story):
        story = []
        node = node_story.firstChild
        while node:
            if node.nodeType == node.ELEMENT_NODE:
                flow = self._flowable(node)
                if flow:
                    story.append(flow)
            node = node.nextSibling
        return story
