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
import copy
import sys
# 2. 3rd parties
from reportlab import platypus
import reportlab.lib.enums
import reportlab.lib.styles
# 3. local
from . import color, utils


def _box_style_get(node):
    class BoxStyle(reportlab.lib.styles.PropertySet):
        pass

    return BoxStyle(node.getAttribute('name'), **utils.attr_get(
        node,
        ('fontSize', 'labelFontSize', 'boxWidth', 'boxHeight'),
        {
            'parent': 'str',
            'alias': 'str',
            'fontName': 'str',
            'labelFontName': 'str',
            'textColor': 'str',
            'boxStrokeColor': 'str',
            'boxFillColor': 'str',
            'labelTextColor': 'str',
        }))


def _para_style_update(style, node):
    for attr in ['textColor', 'backColor', 'bulletColor']:
        if node.hasAttribute(attr):
            style.__dict__[attr] = color.get(node.getAttribute(attr))
    for attr in ['fontName', 'bulletFontName', 'bulletText']:
        if node.hasAttribute(attr):
            style.__dict__[attr] = node.getAttribute(attr)
    for attr in ['fontSize', 'leftIndent', 'rightIndent', 'spaceBefore', 'spaceAfter', 'firstLineIndent',
                 'bulletIndent', 'bulletFontSize', 'leading']:
        if node.hasAttribute(attr):
            if attr == 'fontSize' and not node.hasAttribute('leading'):
                style.__dict__['leading'] = utils.unit_get(
                    node.getAttribute(attr)) * 1.2
            style.__dict__[attr] = utils.unit_get(node.getAttribute(attr))
    if node.hasAttribute('alignment'):
        align = {
            'right': reportlab.lib.enums.TA_RIGHT,
            'center': reportlab.lib.enums.TA_CENTER,
            'justify': reportlab.lib.enums.TA_JUSTIFY
        }
        style.alignment = align.get(
            node.getAttribute('alignment').lower(), reportlab.lib.enums.TA_LEFT)
    return style


def _list_style_update(style, node):
    for attr in ['bulletColor']:
        if node.hasAttribute(attr):
            style.__dict__[attr] = color.get(node.getAttribute(attr))
    for attr in ['bulletType', 'bulletFontName', 'bulletDir', 'bulletFormat', 'start']:
        if node.hasAttribute(attr):
            style.__dict__[attr] = node.getAttribute(attr)
    for attr in ['leftIndent', 'rightIndent', 'bulletFontSize', 'bulletOffsetY', 'bulletDedent']:
        if node.hasAttribute(attr):
            style.__dict__[attr] = utils.unit_get(node.getAttribute(attr))
    if node.hasAttribute('bulletAlign'):
        align = {
            'right': reportlab.lib.enums.TA_RIGHT,
            'center': reportlab.lib.enums.TA_CENTER,
            'justify': reportlab.lib.enums.TA_JUSTIFY
        }
        style.alignment = align.get(
            node.getAttribute('alignment').lower(), reportlab.lib.enums.TA_LEFT)
    return style


def _table_style_get(style_node):
    styles = []
    for node in style_node.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            start = utils.tuple_int_get(node, 'start', (0, 0))
            stop = utils.tuple_int_get(node, 'stop', (-1, -1))
            if node.localName == 'blockValign':
                styles.append(
                    ('VALIGN', start, stop, str(node.getAttribute('value'))))
            elif node.localName == 'blockFont':
                styles.append(
                    ('FONT', start, stop, str(node.getAttribute('name'))))
            elif node.localName == 'blockSpan':
                styles.append(('SPAN', start, stop))
            elif node.localName == 'blockTextColor':
                styles.append(
                    ('TEXTCOLOR', start, stop, color.get(str(node.getAttribute('colorName')))))
            elif node.localName == 'blockLeading':
                styles.append(
                    ('LEADING', start, stop, utils.unit_get(node.getAttribute('length'))))
            elif node.localName == 'blockAlignment':
                styles.append(
                    ('ALIGNMENT', start, stop, str(node.getAttribute('value'))))
            elif node.localName == 'blockLeftPadding':
                styles.append(
                    ('LEFTPADDING', start, stop, utils.unit_get(node.getAttribute('length'))))
            elif node.localName == 'blockRightPadding':
                styles.append(
                    ('RIGHTPADDING', start, stop, utils.unit_get(node.getAttribute('length'))))
            elif node.localName == 'blockTopPadding':
                styles.append(
                    ('TOPPADDING', start, stop, utils.unit_get(node.getAttribute('length'))))
            elif node.localName == 'blockBottomPadding':
                styles.append(
                    ('BOTTOMPADDING', start, stop, utils.unit_get(node.getAttribute('length'))))
            elif node.localName == 'blockBackground':
                styles.append(
                    ('BACKGROUND', start, stop, color.get(node.getAttribute('colorName'))))
            if node.hasAttribute('size'):
                styles.append(
                    ('FONTSIZE', start, stop, utils.unit_get(node.getAttribute('size'))))
            elif node.localName == 'lineStyle':
                kind = node.getAttribute('kind')
                kind_list = ['GRID', 'BOX', 'OUTLINE', 'INNERGRID',
                             'LINEBELOW', 'LINEABOVE', 'LINEBEFORE', 'LINEAFTER']
                assert kind in kind_list
                thick = 1
                if node.hasAttribute('thickness'):
                    thick = float(node.getAttribute('thickness'))
                styles.append(
                    (kind, start, stop, thick, color.get(node.getAttribute('colorName'))))
    return platypus.tables.TableStyle(styles)


class RmlStyles(object):

    def __init__(self, nodes):
        self.styles = {}
        self.names = {}
        self.table_styles = {}
        self.list_styles = {}
        self.box_styles = {}
        for node in nodes:
            for style in node.getElementsByTagName('blockTableStyle'):
                self.table_styles[
                    style.getAttribute('id')] = _table_style_get(style)
            for style in node.getElementsByTagName('listStyle'):
                self.list_styles[
                    style.getAttribute('name')] = self._list_style_get(style)
            for style in node.getElementsByTagName('paraStyle'):
                self.styles[
                    style.getAttribute('name')] = self._para_style_get(style)
            for style in node.getElementsByTagName('boxStyle'):
                self.box_styles[
                    style.getAttribute('name')] = _box_style_get(style)
            for variable in node.getElementsByTagName('initialize'):
                for name in variable.getElementsByTagName('name'):
                    self.names[name.getAttribute('id')] = name.getAttribute('value')

    def _list_style_get(self, node):
        style = reportlab.lib.styles.ListStyle('Default')
        if node.hasAttribute("parent"):
            parent = node.getAttribute("parent")
            parent_style = self.styles.get(parent)
            if not parent_style:
                raise Exception("parent style = '%s' not found" % parent)
            style.__dict__.update(parent_style.__dict__)
            style.alignment = parent_style.alignment
        _list_style_update(style, node)
        return style

    def _para_style_get(self, node):
        styles = reportlab.lib.styles.getSampleStyleSheet()
        style = copy.deepcopy(styles["Normal"])
        if node.hasAttribute("parent"):
            parent = node.getAttribute("parent")
            parent_style = self.styles.get(parent)
            if not parent_style:
                raise Exception("parent style = '%s' not found" % parent)
            style.__dict__.update(parent_style.__dict__)
            style.alignment = parent_style.alignment
        _para_style_update(style, node)
        return style

    def para_style_get(self, node):
        style = False
        if node.hasAttribute('style'):
            if node.getAttribute('style') in self.styles:
                style = copy.deepcopy(self.styles[node.getAttribute('style')])
            else:
                sys.stderr.write(
                    'Warning: style not found, %s - setting default!\n' % (node.getAttribute('style'),))
        if not style:
            styles = reportlab.lib.styles.getSampleStyleSheet()
            style = copy.deepcopy(styles['Normal'])
        return _para_style_update(style, node)
