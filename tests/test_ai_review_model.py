import contextlib
import importlib.util
import io
import json
import os
import pathlib
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / ".forgejo/scripts/ai-review.py"
ENV = {"FORGEJO_URL": "https://forgejo.example", "REPO": "example/rules", "TOKEN": "job"}
with mock.patch.dict(os.environ, ENV):
    spec = importlib.util.spec_from_file_location("ai_review_model", SCRIPT)
    ai_review = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ai_review)


USAGE = {"prompt_tokens": 9139, "completion_tokens": 23557}


def reply(finish, content, usage=USAGE, choices=None):
    if choices is None:
        choices = [{"finish_reason": finish, "message": {"content": content}}]
    body = {"choices": choices, "usage": usage}
    return mock.MagicMock(__enter__=lambda s: io.BytesIO(json.dumps(body).encode()),
                          __exit__=lambda *a: False)


class AskModel(unittest.TestCase):
    def call(self, finish, content, **kw):
        sent, out = [], io.StringIO()

        def urlopen(req, timeout):
            sent.append(json.loads(req.data))
            return reply(finish, content, **kw)

        env = {"MODEL": "m", "LLM_URL": "http://llm/v1/chat/completions"}
        with mock.patch.dict(os.environ, env), mock.patch.object(ai_review.urllib.request, "urlopen", urlopen), \
                contextlib.redirect_stdout(out):
            try:
                return ai_review.ask_model([]), sent, out.getvalue()
            except (ValueError, ai_review.CutOff, IndexError, AttributeError) as e:
                return e, sent, out.getvalue()

    def test_requests_the_cap_and_logs_usage(self):
        result, sent, out = self.call("stop", '<think>x</think>{"summary": "ok", "findings": []}')
        self.assertEqual(result, {"summary": "ok", "findings": []})
        self.assertEqual(sent[0]["max_tokens"], ai_review.MAX_OUTPUT_TOKENS)
        self.assertIn('"completion_tokens": 23557', out)
        self.assertIn("finish_reason=stop", out)

    def test_cut_off_answer_fails_closed_and_says_why(self):
        # Even a JSON-looking fragment must not be trusted once the model was cut off.
        result, _, out = self.call("length", '{"summary": "ok", "findings": []}')
        self.assertIsInstance(result, ai_review.CutOff)
        self.assertIn("cut off", str(result))
        self.assertIn("finish_reason=length", out)

    def test_usage_at_the_cap_counts_as_cut_off_without_a_finish_reason(self):
        cap = USAGE["completion_tokens"]
        ok = '{"summary": "ok", "findings": []}'
        with mock.patch.object(ai_review, "MAX_OUTPUT_TOKENS", cap):
            result, _, out = self.call(None, ok)
            self.assertIsInstance(result, ai_review.CutOff)
            self.assertIn("cut off", str(result))
            # A server that says it stopped normally is believed.
            self.assertEqual(self.call("stop", ok)[0]["summary"], "ok")
        with mock.patch.object(ai_review, "MAX_OUTPUT_TOKENS", cap + 1):
            self.assertEqual(self.call(None, ok)[0]["summary"], "ok")

    def test_missing_usage_still_parses(self):
        result, _, out = self.call("stop", '{"summary": "ok", "findings": []}', usage=None)
        self.assertEqual(result["summary"], "ok")
        self.assertIn("model usage: {}", out)

    def test_malformed_choices_raise_handled_errors(self):
        self.assertIsInstance(self.call("stop", "", choices=[])[0], IndexError)
        self.assertIsInstance(self.call("stop", "", choices=["x"])[0], AttributeError)

    def test_empty_answer_fails_closed(self):
        result, _, _ = self.call("stop", None)
        self.assertIsInstance(result, ValueError)
        self.assertIn("no JSON object", str(result))

    def test_cap_can_be_set_per_repo(self):
        with mock.patch.dict(os.environ, {**ENV, "MAX_OUTPUT_TOKENS": "1234"}):
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        self.assertEqual(module.MAX_OUTPUT_TOKENS, 1234)


if __name__ == "__main__":
    unittest.main()
