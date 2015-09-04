import os
import unittest

from six import text_type

import trml2pdf  # dev mode: python setup.py develop


EXAMPLES_DIR = "../examples"


# sys.path.append(EXAMPLES_DIR)

class Test(unittest.TestCase):
    """run pdf genration using all files in examples."""

    def test_run_all(self):
        try:

            # change current dir, there are relative references to images in rmls
            work_dir = os.getcwd()
            os.chdir(EXAMPLES_DIR)
            self._run_all_examples()
        finally:
            os.chdir(work_dir)

    def _run_all_examples(self):
        for name in os.listdir('.'):
            if name.endswith(".rml"):
                path = name  # '{}/{}'.format(EXAMPLES_DIR, name)
                print('running: {}'.format(path))
                output = trml2pdf.parseString(text_type(open(path, "r").read()))
                self.assertIsNotNone(output)


if __name__ == "__main__":
    unittest.main()
