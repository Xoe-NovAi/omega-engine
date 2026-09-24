import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "screening.py"
SPEC = importlib.util.spec_from_file_location("screening", SCRIPT)
screening = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(screening)


class GeneratePayloadTests(unittest.TestCase):
    def test_think_false_is_explicit_and_bounded(self):
        payload = screening.build_generate_payload(
            model="gemma4-12b-qat",
            prompt="test",
            num_predict=321,
        )

        self.assertIs(payload["think"], False)
        self.assertEqual(payload["options"]["num_predict"], 321)
        self.assertEqual(payload["options"]["num_thread"], 8)
        self.assertEqual(payload["options"]["num_gpu"], 0)

    def test_think_true_is_explicit(self):
        payload = screening.build_generate_payload(
            model="reasoning-model",
            prompt="test",
            think=True,
        )

        self.assertIs(payload["think"], True)


class SaveResultsTests(unittest.TestCase):
    def test_protocol_records_run_configuration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "screen.json"
            screening.save_results(
                output,
                "gemma4-12b-qat",
                [],
                num_predict=512,
                think=False,
                temperatures=[0.1],
                contexts=[4096],
            )

            data = json.loads(output.read_text())

        self.assertIs(data["think"], False)
        self.assertEqual(data["num_predict"], 512)
        self.assertEqual(data["temperatures"], [0.1])
        self.assertEqual(data["contexts"], [4096])


if __name__ == "__main__":
    unittest.main()
