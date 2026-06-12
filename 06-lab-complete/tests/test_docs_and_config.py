import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class DocsAndConfigTests(unittest.TestCase):
    def test_compose_uses_same_env_file_as_readme(self):
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        compose = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("cp .env.example .env", readme)
        self.assertIn("- .env", compose)

    def test_env_example_uses_monthly_budget_variable(self):
        env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("MONTHLY_BUDGET_USD=", env_example)

    def test_render_config_uses_monthly_budget_variable(self):
        render_yaml = (PROJECT_ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("MONTHLY_BUDGET_USD", render_yaml)


if __name__ == "__main__":
    unittest.main()
