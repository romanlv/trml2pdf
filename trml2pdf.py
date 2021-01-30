#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# trml2pdf - An RML to PDF converter
# Copyright (C) 2003, Fabien Pinckaers, UCL, FSA
# Contributors
#     Richard Waid <richard@iopen.net>
#     Klaas Freitag <freitag@kde.org>

import os
import sys

import trml2pdf

__help = \
    "Usage: trml2pdf input.rml >output.pdf\n\
Render the standard input (RML) and output a PDF file"


def main():
    if len(sys.argv) == 1 or sys.argv[1] == '--help':
        print(__help)
        sys.exit(0)
    else:
        # print(parseString(open(sys.argv[1], 'r').read()))
        os.write(1, trml2pdf.parseString(open(sys.argv[1], 'rt').read()))


if __name__ == "__main__":
    main()
