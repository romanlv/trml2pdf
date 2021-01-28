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
import io
import sys
# 2. 3rd parties
from six.moves import urllib
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128, qr
# 3. local
from . import color, flowable, utils

encoding = 'UTF-8'


class RmlCanvas(object):

    def __init__(self, canvas, doc_tmpl=None, doc=None):
        self.canvas = canvas
        self.styles = doc.styles
        self.doc_tmpl = doc_tmpl
        self.doc = doc

    def _textual(self, node):
        rc = ''
        for n in node.childNodes:
            if n.nodeType == n.ELEMENT_NODE:
                if n.localName == 'pageNumber':
                    counting_from = utils.tuple_int_get(n, 'countingFrom', default=[0])[0]
                    rc += str(self.canvas.getPageNumber() + counting_from)
            elif n.nodeType == node.CDATA_SECTION_NODE:
                rc += n.data
            elif n.nodeType == node.TEXT_NODE:
                rc += n.data
        return rc.encode(encoding)

    def _drawString(self, node):
        self.canvas.drawString(
            text=self._textual(node), **utils.attr_get(node, ['x', 'y']))

    def _drawCenteredString(self, node):
        self.canvas.drawCentredString(
            text=self._textual(node), **utils.attr_get(node, ['x', 'y']))

    def _drawRightString(self, node):
        self.canvas.drawRightString(
            text=self._textual(node), **utils.attr_get(node, ['x', 'y']))

    def _rect(self, node):
        if node.hasAttribute('round'):
            self.canvas.roundRect(radius=utils.unit_get(node.getAttribute(
                'round')), **utils.attr_get(node, ['x', 'y', 'width', 'height'], {'fill': 'bool', 'stroke': 'bool'}))
        else:
            self.canvas.rect(
                **utils.attr_get(node, ['x', 'y', 'width', 'height'], {'fill': 'bool', 'stroke': 'bool'}))

    def _ellipse(self, node):
        x1 = utils.unit_get(node.getAttribute('x'))
        x2 = utils.unit_get(node.getAttribute('width'))
        y1 = utils.unit_get(node.getAttribute('y'))
        y2 = utils.unit_get(node.getAttribute('height'))
        self.canvas.ellipse(
            x1, y1, x2, y2, **utils.attr_get(node, [], {'fill': 'bool', 'stroke': 'bool'}))

    def _curves(self, node):
        line_str = utils.text_get(node).split()
        while len(line_str) > 7:
            self.canvas.bezier(*[utils.unit_get(l) for l in line_str[0:8]])
            line_str = line_str[8:]

    def _lines(self, node):
        line_str = utils.text_get(node).split()
        lines = []
        while len(line_str) > 3:
            lines.append([utils.unit_get(l) for l in line_str[0:4]])
            line_str = line_str[4:]
        self.canvas.lines(lines)

    def _grid(self, node):
        xlist = [utils.unit_get(s) for s in node.getAttribute('xs').split(',')]
        ylist = [utils.unit_get(s) for s in node.getAttribute('ys').split(',')]
        self.canvas.grid(xlist, ylist)

    def _translate(self, node):
        dx = 0
        dy = 0
        if node.hasAttribute('dx'):
            dx = utils.unit_get(node.getAttribute('dx'))
        if node.hasAttribute('dy'):
            dy = utils.unit_get(node.getAttribute('dy'))
        self.canvas.translate(dx, dy)

    def _transform(self, node):
        # FIXME: any whitespaces
        args = []
        for i in self._textual(node).lstrip().rstrip().split(' '):
            args.append(float(i))
            sys.stderr.write(str(float(i)) + '\n')
        self.canvas.transform(*args)

    def _circle(self, node):
        self.canvas.circle(x_cen=utils.unit_get(node.getAttribute('x')), y_cen=utils.unit_get(node.getAttribute(
            'y')), r=utils.unit_get(node.getAttribute('radius')),
                           **utils.attr_get(node, [], {'fill': 'bool', 'stroke': 'bool'}))

    def _place(self, node):
        flows = flowable.RmlFlowable(self.doc).render(node)
        infos = utils.attr_get(node, ['x', 'y', 'width', 'height'])
        infos['y'] += infos['height']
        for flow in flows:
            w, h = flow.wrap(infos['width'], infos['height'])
            if w <= infos['width'] and h <= infos['height']:
                infos['y'] -= h
                flow.drawOn(self.canvas, infos['x'], infos['y'])
                infos['height'] -= h
            else:
                raise ValueError("Not enough space")

    def _line_mode(self, node):
        ljoin = {'round': 1, 'mitered': 0, 'bevelled': 2}
        lcap = {'default': 0, 'round': 1, 'square': 2}
        if node.hasAttribute('width'):
            self.canvas.setLineWidth(
                utils.unit_get(node.getAttribute('width')))
        if node.hasAttribute('join'):
            self.canvas.setLineJoin(ljoin[node.getAttribute('join')])
        if node.hasAttribute('cap'):
            self.canvas.setLineCap(lcap[node.getAttribute('cap')])
        if node.hasAttribute('miterLimit'):
            self.canvas.setDash(
                utils.unit_get(node.getAttribute('miterLimit')))
        if node.hasAttribute('dash'):
            dashes = node.getAttribute('dash').split(',')
            for x in range(len(dashes)):
                dashes[x] = utils.unit_get(dashes[x])
            self.canvas.setDash(dashes)

    def _image(self, node):
        u = urllib.request.urlopen("file:" + str(node.getAttribute('file')))
        s = io.BytesIO()
        s.write(u.read())
        s.seek(0)
        img = ImageReader(s)
        (sx, sy) = img.getSize()
        args = {}
        for tag in ('width', 'height', 'x', 'y'):
            if node.hasAttribute(tag):
                # if not utils.unit_get(node.getAttribute(tag)):
                #     continue
                args[tag] = utils.unit_get(node.getAttribute(tag))
        if node.hasAttribute("preserveAspectRatio"):
            args["preserveAspectRatio"] = True
        if node.hasAttribute('mask'):
            args['mask'] = node.getAttribute('mask')
        if ('width' in args) and ('height' not in args):
            args['height'] = sy * args['width'] / sx
        elif ('height' in args) and ('width' not in args):
            args['width'] = sx * args['height'] / sy
        elif ('width' in args) and ('height' in args) and (not args.get("preserveAspectRatio", False)):
            if (float(args['width']) / args['height']) > (float(sx) > sy):
                args['width'] = sx * args['height'] / sy
            else:
                args['height'] = sy * args['width'] / sx
        self.canvas.drawImage(img, **args)

    def _barcode(self, node):
        createargs = {}
        drawargs = {}
        code_type = node.getAttribute('code')
        for tag in ('x', 'y'):
            if node.hasAttribute(tag):
                drawargs[tag] = utils.unit_get(node.getAttribute(tag))
        if code_type == 'Code128':
            for tag in ('barWidth', 'barHeight'):
                if node.hasAttribute(tag):
                    createargs[tag] = utils.unit_get(node.getAttribute(tag))
            barcode = code128.Code128(self._textual(node), **createargs)
        elif code_type == "QR":
            for tag in ('width', 'height'):
                if node.hasAttribute(tag):
                    createargs[tag] = utils.unit_get(node.getAttribute(tag))
            barcode = qr.QrCode(node.getAttribute('value'), **createargs)
        barcode.drawOn(self.canvas, **drawargs)

    def _path(self, node):
        self.path = self.canvas.beginPath()
        self.path.moveTo(**utils.attr_get(node, ['x', 'y']))
        for n in node.childNodes:
            if n.nodeType == node.ELEMENT_NODE:
                if n.localName == 'moveto':
                    vals = utils.text_get(n).split()
                    self.path.moveTo(
                        utils.unit_get(vals[0]), utils.unit_get(vals[1]))
                elif n.localName == 'curvesto':
                    vals = utils.text_get(n).split()
                    while len(vals) > 5:
                        pos = []
                        while len(pos) < 6:
                            pos.append(utils.unit_get(vals.pop(0)))
                        self.path.curveTo(*pos)
            elif n.nodeType == node.TEXT_NODE:
                # Not sure if I must merge all TEXT_NODE ?
                data = n.data.split()
                while len(data) > 1:
                    x = utils.unit_get(data.pop(0))
                    y = utils.unit_get(data.pop(0))
                    self.path.lineTo(x, y)
        if (not node.hasAttribute('close')) or utils.bool_get(node.getAttribute('close')):
            self.path.close()
        self.canvas.drawPath(
            self.path, **utils.attr_get(node, [], {'fill': 'bool', 'stroke': 'bool'}))

    def _letterBoxes(self, node):
        # 1. get args (args.update(style))
        attrs = utils.attr_get(
            node,
            ('x', 'y', 'boxWidth', 'boxHeight', 'lineWidth', 'fontSize', 'labelFontSize', 'labelOffsetX',
             'labelOffsetY'),
            {
                'style': 'str',
                'count': 'int',
                'boxStrokeColor': 'str',
                'boxFillColor': 'str',
                'textColor': 'str',
                'fontName': 'str',
                'label': 'str',
                'labelTextColor': 'str',
                'labelFontName': 'str',
            })
        # 2. apply style (hack)
        if 'style' in attrs:
            # FIXME: error
            args = copy.deepcopy(self.styles.box_styles[attrs['style']].__dict__)
            # args = copy.deepcopy(self.box_styles[attrs['style']].__dict__)
            args.update(attrs)
        else:
            args = attrs
        # 3. draw: rect (x, y, width, height, stroke:bool, fill=bool) + setFillColor(color) + setStrokeColor(color) +
        # setLineWidth(lineWidth) drawString: x, y + setFont(name, size)|setFontSize()|canvas._fontsize +
        # setFillColor(textColor)
        #
        self.canvas.saveState()
        if 'lineWidth' in args:
            self.canvas.setLineWidth(args['lineWidth'])
        if ('fontSize' in args) and not ('fontName' in args):
            self.canvas.setFontSize(args['fontSize'])
        # print "FONT NAME:", self.canvas._fontname
        elif 'fontName' in args:
            self.canvas.setFont(args['fontName'], args.get('fontSize'), self.canvas._fontsize)  # hack
        # 4. calc: boxWidth, boxHeight
        if not ('boxWidth' in args):
            args['boxWidth'] = self.canvas.stringWidth('W', self.canvas._fontname, self.canvas._fontsize)
        if not ('boxHeight' in args):
            args['boxHeight'] = self.canvas._fontsize + 2
        text = str(self._textual(node))
        x = args['x']
        y = args['y']
        w = args['boxWidth']
        h = args['boxHeight']
        dy = (0.5 * h) - (0.25 * self.canvas._fontsize)
        # 5. let's go
        for i in range(args['count']):
            x1 = x + i * w
            # 5.1. rect
            self.canvas.saveState()
            if 'boxFillColor' in args:
                self.canvas.setFillColor(color.get(args['boxFillColor']))
            if 'boxStrokeColor' in args:
                self.canvas.setStrokeColor(color.get(args['boxStrokeColor']))
            self.canvas.rect(x=x1, y=y, width=w, height=h, fill=('boxFillColor' in args))
            self.canvas.restoreState()
            # 5.2. symbol
            self.canvas.saveState()
            if 'textColor' in args:
                self.canvas.setFillColor(color.get(args['textColor']))
            if i < len(text):
                self.canvas.drawCentredString(float(x1 + (float(w) / 2.0)), float(y) + dy, text=text[i])
            self.canvas.restoreState()
        self.canvas.restoreState()
        # 5.3. label
        if 'label' in args:
            self.canvas.saveState()
            if ('labelFontSize' in args) and not ('labelFontName' in args):
                self.canvas.setFontSize(args['labelFontSize'])
            elif 'labelFontName' in args:
                self.canvas.setFont(args['labelFontName'], args.get('labelFontSize'), self.canvas._fontsize)  # hack
            if 'labelTextColor' in args:
                self.canvas.setFillColor(color.get(args['labelTextColor']))
            y += args.get('labelOffsetY', 0)
            self.canvas.drawString(x=x + args.get('labelOffsetX', 0), y=y + args.get('labelOffsetY', 0),
                                   text=args['label'])
            # TODO: align, default OffsetX
            self.canvas.restoreState()

    def render(self, node):
        tags = {
            'drawCentredString': self._drawCenteredString,
            'drawCenteredString': self._drawCenteredString,
            'drawRightString': self._drawRightString,
            'drawString': self._drawString,
            'rect': self._rect,
            'ellipse': self._ellipse,
            'lines': self._lines,
            'grid': self._grid,
            'curves': self._curves,
            'fill': lambda node: self.canvas.setFillColor(color.get(node.getAttribute('color'))),
            'stroke': lambda node: self.canvas.setStrokeColor(color.get(node.getAttribute('color'))),
            'setFont': lambda node: self.canvas.setFont(node.getAttribute('name'),
                                                        utils.unit_get(node.getAttribute('size'))),
            'place': self._place,
            'circle': self._circle,
            'lineMode': self._line_mode,
            'path': self._path,
            'rotate': lambda node: self.canvas.rotate(float(node.getAttribute('degrees'))),
            'translate': self._translate,
            'transform': self._transform,
            'image': self._image,
            'barCode': self._barcode,
            'letterBoxes': self._letterBoxes,
        }
        for nd in node.childNodes:
            if nd.nodeType == nd.ELEMENT_NODE:
                for tag in tags:    # FIXME: too slow?
                    if nd.localName == tag:
                        tags[tag](nd)
                        break


class RmlDraw(object):

    def __init__(self, node, styles):
        self.node = node
        self.styles = styles
        self.canvas = None

    def render(self, canvas, doc):
        canvas.saveState()
        cnv = RmlCanvas(canvas, None, self)  # can be (canvas, doc, self)?
        cnv.render(self.node)
        canvas.restoreState()
