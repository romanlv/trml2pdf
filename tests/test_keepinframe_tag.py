import unittest

import trml2pdf
from reportlab.platypus.doctemplate import LayoutError


class TestKeepInFrame(unittest.TestCase):
    def test_error_mode(self):
        """ Tests that a LayoutError is raised if the onOverflow
        attribute for a keepInFrame tag is set to "error" and the
        content does not fit in the frame.
        """
        rml = """
        <!DOCTYPE document SYSTEM "rml.dtd">
        <document>
            <template pageSize="(8.5in, 11in)" showBoundary="1">
                <pageTemplate id="main">
                    <frame id="i" x1="1in" y1="9in" width="2in" height="1in"/>
                </pageTemplate>
            </template>
            <stylesheet>
            </stylesheet>
            <story>
                <keepInFrame onOverflow="error">
                    <para fontSize="30">
                        This should raise a LayoutError!!!!!!!!!!!!
                    </para>
                </keepInFrame>
            </story>
        </document>
        """
        with self.assertRaises(LayoutError):
            trml2pdf.parseString(rml)
