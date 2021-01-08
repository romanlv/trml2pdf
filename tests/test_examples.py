import os
import unittest

import trml2pdf  # dev mode: python setup.py develop

from six import text_type


EXAMPLES_DIR = "examples"
TESTS_DIR = os.path.dirname(os.path.realpath(__file__))

# sys.path.append(EXAMPLES_DIR)

class TestExamples(unittest.TestCase):
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
                with open(path, "r") as f:
                    output = trml2pdf.parseString(f.read())
                self.assertIsNotNone(output)






# does not work, todo find a solution
# class TestOutput(unittest.TestCase):
#     def test_bug8(self):
#         with open(TESTS_DIR + '/templates/bug_8.rml', "r") as f:
#             output = trml2pdf.parseString(f.read())
#             print(output)
#         self.assertNotIn('\\n', text_type(output))  # not so easy to test PDF content, it is encoded
#         with open(TESTS_DIR + '/templates/bug8.pdf', 'wb') as w:
#             w.write(output)




if __name__ == "__main__":
    unittest.main()
