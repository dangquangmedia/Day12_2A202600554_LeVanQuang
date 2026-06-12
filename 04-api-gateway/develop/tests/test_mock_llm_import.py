import importlib
import pathlib
import sys
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_MODULE = PROJECT_ROOT / "utils" / "mock_llm.py"


class MockLlmImportTests(unittest.TestCase):
    def test_imports_local_utils_module(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            module = importlib.import_module("utils.mock_llm")
        finally:
            sys.path.pop(0)

        self.assertEqual(pathlib.Path(module.__file__).resolve(), EXPECTED_MODULE)

    def test_ask_returns_text(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            module = importlib.import_module("utils.mock_llm")
        finally:
            sys.path.pop(0)

        self.assertIsInstance(module.ask("hello"), str)


if __name__ == "__main__":
    unittest.main()
