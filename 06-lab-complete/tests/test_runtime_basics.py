import importlib
import pathlib
import sys
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_UTILS_MODULE = PROJECT_ROOT / "utils" / "mock_llm.py"


class RuntimeBasicsTests(unittest.TestCase):
    def test_app_main_imports_from_lab_directory(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            module = importlib.import_module("app.main")
        finally:
            sys.path.pop(0)

        self.assertEqual(module.__name__, "app.main")

    def test_utils_module_resolves_inside_lab(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            module = importlib.import_module("utils.mock_llm")
        finally:
            sys.path.pop(0)

        self.assertEqual(pathlib.Path(module.__file__).resolve(), EXPECTED_UTILS_MODULE)


if __name__ == "__main__":
    unittest.main()
