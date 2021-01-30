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
import io
import xml.dom.minidom
# 2. 3rd parties
from reportlab import platypus
from reportlab.pdfgen import canvas
# 3. local
from . import canv, flowable, styles, utils


def docinit(els):
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for node in els:
        for font in node.getElementsByTagName('registerFont'):
            name = font.getAttribute('fontName')
            fname = font.getAttribute('fontFile')
            pdfmetrics.registerFont(TTFont(name, fname))
        for font in node.getElementsByTagName('registerTTFont'):
            name = font.getAttribute('faceName')
            fname = font.getAttribute('fileName')
            pdfmetrics.registerFont(TTFont(name, fname))  # , subfontIndex=subfontIndex
        for font_family in node.getElementsByTagName('registerFontFamily'):
            normal = font_family.getAttribute('normal')
            bold = font_family.getAttribute('bold')
            italic = font_family.getAttribute('italic')
            bold_italic = font_family.getAttribute('boldItalic')
            addMapping(normal, 0, 0, normal)  # normal
            addMapping(normal, 1, 0, bold)  # bold
            addMapping(normal, 0, 1, italic)  # italic
            addMapping(normal, 1, 1, bold_italic)  # italic and bold


class RmlDoc(object):

    def __init__(self, data: str):
        self.dom = xml.dom.minidom.parseString(data)
        self.filename = self.dom.documentElement.getAttribute('filename')
        self.canvas = None
        self.styles = None

    def render(self, out):
        el = self.dom.documentElement.getElementsByTagName('docinit')
        if el:
            docinit(el)
        el = self.dom.documentElement.getElementsByTagName('stylesheet')
        self.styles = styles.RmlStyles(el)
        el = self.dom.documentElement.getElementsByTagName('template')
        if len(el):
            pt_obj = RmlTemplate(out, el[0], self)
            pt_obj.render(
                self.dom.documentElement.getElementsByTagName('story')[0])
        else:
            self.canvas = canvas.Canvas(out)
            pd = self.dom.documentElement.getElementsByTagName(
                'pageDrawing')[0]
            pd_obj = canv.RmlCanvas(self.canvas, None, self)
            pd_obj.render(pd)
            self.canvas.showPage()
            self.canvas.save()


class RmlTemplate(object):

    def __init__(self, out, node, doc):
        if not node.hasAttribute('pageSize'):
            page_size = (utils.unit_get('21cm'), utils.unit_get('29.7cm'))
        else:
            ps = [x.strip() for x in node.getAttribute('pageSize').replace(')', '').replace(
                '(', '').split(',')]
            page_size = (utils.unit_get(ps[0]), utils.unit_get(ps[1]))
        # cm = reportlab.lib.units.cm
        self.doc_tmpl = platypus.BaseDocTemplate(out, pagesize=page_size, **utils.attr_get(
            node,
            ['leftMargin', 'rightMargin', 'topMargin', 'bottomMargin'],
            {'allowSplitting': 'int', 'showBoundary': 'bool', 'title': 'str', 'author': 'str', 'rotation': 'int'}))
        self.page_templates = []
        self.styles = doc.styles
        self.doc = doc
        pts = node.getElementsByTagName('pageTemplate')
        for pt in pts:
            frames = []
            for frame_el in pt.getElementsByTagName('frame'):
                frame = platypus.Frame(**(utils.attr_get(
                    frame_el,
                    ['x1', 'y1', 'width', 'height', 'leftPadding', 'rightPadding', 'bottomPadding', 'topPadding'],
                    {'id': 'text', 'showBoundary': 'bool'})))
                frames.append(frame)
            gr = pt.getElementsByTagName('pageGraphics')
            if len(gr):
                drw = canv.RmlDraw(gr[0], self.doc.styles)
                self.page_templates.append(platypus.PageTemplate(
                    frames=frames, onPage=drw.render, **utils.attr_get(pt, [], {'id': 'str'})))
            else:
                self.page_templates.append(
                    platypus.PageTemplate(frames=frames, **utils.attr_get(pt, [], {'id': 'str'})))
        self.doc_tmpl.addPageTemplates(self.page_templates)

    def render(self, node_story):
        r = flowable.RmlFlowable(self.doc)
        fis = r.render(node_story)
        self.doc_tmpl.build(fis)
