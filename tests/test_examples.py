import os
import unittest

from trml2pdf import parseString  # dev mode: python setup.py develop

INPUT_DIR = "input"
OUTPUT_DIR = "output"
TESTS_DIR = os.path.dirname(os.path.realpath(__file__))


class TestExamples(unittest.TestCase):
    """run pdf genration using all files in examples."""

    def test_run_all(self):
        work_dir = os.getcwd()
        try:
            # change current dir, there are relative references to images in rmls
            os.chdir(os.path.join(TESTS_DIR, INPUT_DIR))
            self._run_all_examples()
        finally:
            os.chdir(work_dir)

    def _run_all_examples(self):
        for name in os.listdir('.'):
            if name.endswith(".rml"):
                path = name  # '{}/{}'.format(INPUT_DIR, name)
                print('running: {}'.format(path))
                with open(path, "r") as f:
                    output = parseString(f.read())
                self.assertIsNotNone(output)
                with open(os.path.join(TESTS_DIR, OUTPUT_DIR, name[:-3]+"pdf"), "wb") as of:
                    of.write(output)

# does not work, todo find a solution
# class TestOutput(unittest.TestCase):
#     def test_bug8(self):
#         with open(TESTS_DIR + '/templates/bug_8.rml', "r") as f:
#             output = parseString(f.read())
#             print(output)
#         self.assertNotIn('\\n', text_type(output))  # not so easy to test PDF content, it is encoded
#         with open(TESTS_DIR + '/templates/bug8.pdf', 'wb') as w:
#             w.write(output)


if __name__ == "__main__":
    unittest.main()
