"""Conformance tests for aipref_signals: every case in test_vectors.json. Run: python3 -m unittest test_aipref_signals"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aipref_signals  # noqa: E402


def load_vectors(path=os.path.join(HERE, "test_vectors.json")):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_case(module, case, bytes_arguments):
    """The function's result for one case, after a JSON round trip (tuples become lists)."""
    encode = bytes_arguments.get(case["function"], [])
    args = [arg.encode("utf-8") if index in encode else arg for index, arg in enumerate(case["args"])]
    return json.loads(json.dumps(getattr(module, case["function"])(*args)))


class ConformanceTest(unittest.TestCase):
    def test_vectors(self):
        vectors = load_vectors()
        self.assertEqual(vectors["follows"], aipref_signals.FOLLOWS)
        self.assertGreater(len(vectors["cases"]), 40)
        for case in vectors["cases"]:
            with self.subTest(function=case["function"], name=case["name"]):
                self.assertEqual(run_case(aipref_signals, case, vectors["bytes_arguments"]), case["expected"])


if __name__ == "__main__":
    unittest.main()
