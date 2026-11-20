import contextlib
import errno
import importlib.util
import io
import json
import os
import pathlib
import signal
import time
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

    def flaky(self, errors):
        """urlopen that raises each of errors once, then answers; returns (urlopen, calls, sleeps)."""
        calls, sleeps = [], []

        def urlopen(req, timeout):
            calls.append(req)
            if len(calls) <= len(errors):
                raise errors[len(calls) - 1]
            return reply("stop", '{"summary": "ok", "findings": []}')
        return urlopen, calls, sleeps

    def run_flaky(self, errors):
        urlopen, calls, sleeps = self.flaky(errors)
        env = {"MODEL": "m", "LLM_URL": "http://llm/v1/chat/completions"}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), mock.patch.object(ai_review.urllib.request, "urlopen", urlopen), \
                mock.patch.object(ai_review.time, "sleep", sleeps.append), contextlib.redirect_stdout(out):
            try:
                result = ai_review.ask_model([])
            except Exception as e:
                result = e
        self.out = out.getvalue()
        return result, calls, sleeps

    def test_name_lookup_failure_then_success_yields_a_verdict(self):
        dns = ai_review.urllib.error.URLError(ai_review.socket.gaierror(-2, "Name or service not known"))
        result, calls, sleeps = self.run_flaky([dns])
        self.assertEqual(result, {"summary": "ok", "findings": []})
        self.assertEqual((len(calls), sleeps), (2, [5]))
        self.assertIn("retrying in 5s", self.out)
        # The retry re-sends the same prompt, not a consumed or empty body.
        self.assertEqual(json.loads(calls[1].data), json.loads(calls[0].data))
        self.assertEqual(json.loads(calls[1].data)["max_tokens"], ai_review.MAX_OUTPUT_TOKENS)

    def test_refused_or_unroutable_connection_is_retried(self):
        refused = ai_review.urllib.error.URLError(ConnectionRefusedError(errno.ECONNREFUSED, "refused"))
        unroutable = ai_review.urllib.error.URLError(OSError(errno.EHOSTUNREACH, "No route to host"))
        result, calls, sleeps = self.run_flaky([refused, unroutable])
        self.assertEqual(result, {"summary": "ok", "findings": []})
        self.assertEqual((len(calls), sleeps), (3, [5, 15]))

    def test_other_os_errors_are_not_retried(self):
        reset = ai_review.urllib.error.URLError(OSError(errno.ECONNRESET, "Connection reset"))
        result, calls, sleeps = self.run_flaky([reset])
        self.assertIs(result, reset)
        self.assertEqual((len(calls), sleeps), (1, []))

    def test_connect_retries_are_bounded_and_fail_closed(self):
        dns = ai_review.urllib.error.URLError(ai_review.socket.gaierror(-2, "Name or service not known"))
        result, calls, sleeps = self.run_flaky([dns] * 10)
        self.assertIsInstance(result, ai_review.urllib.error.URLError)
        self.assertEqual(len(calls), len(ai_review.CONNECT_RETRY_DELAYS) + 1)
        self.assertEqual(sleeps, list(ai_review.CONNECT_RETRY_DELAYS))

    def test_timeouts_and_http_errors_are_not_retried(self):
        timeout = ai_review.urllib.error.URLError(TimeoutError("timed out"))
        http = ai_review.urllib.error.HTTPError("http://llm", 502, "Bad Gateway", {}, None)
        for error in (timeout, http, TimeoutError("read timed out")):
            result, calls, sleeps = self.run_flaky([error])
            self.assertIs(result, error)
            self.assertEqual((len(calls), sleeps), (1, []))

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
            result, _, _ = self.call(None, ok)
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

    def test_reasoning_leaked_past_a_quoted_think_tag_is_ignored(self):
        leaked = ('", "", text)` is unchanged; the check {"x": 1} is fine.\n</think>\n\n'
                  '{"summary": "ok", "findings": []}')
        self.assertEqual(self.call("stop", leaked)[0]["summary"], "ok")

    def test_verdict_quoting_a_think_tag_survives(self):
        quoted = '{"summary": "the parser strips </think> blocks", "findings": [{"id": "F1"}]}'
        result = self.call("stop", quoted)[0]
        self.assertEqual(result["summary"], "the parser strips </think> blocks")
        self.assertEqual(result["findings"], [{"id": "F1"}])

    def test_malformed_final_verdict_fails_even_after_a_valid_draft(self):
        text = ('draft {"summary": "draft", "findings": []} more thought\n</think>\n'
                '{"summary": "final", "findings": [')
        self.assertIsInstance(self.call("stop", text)[0], ValueError)

    def test_inner_verdict_of_an_unfinished_object_fails(self):
        text = '{"summary": "real", "findings": [], "note": {"summary": "inner", "findings": []}'
        self.assertIsInstance(self.call("stop", text)[0], ValueError)

    def test_fenced_verdict_parses(self):
        text = '```json\n{"summary": "ok", "findings": []}\n```\n'
        self.assertEqual(self.call("stop", text)[0]["summary"], "ok")

    def test_last_verdict_wins_over_a_leaked_draft(self):
        text = ('draft {"summary": "draft", "findings": []} more thought\n</think>\n'
                '{"summary": "final", "findings": []}')
        self.assertEqual(self.call("stop", text)[0]["summary"], "final")

    def test_empty_answer_fails_closed(self):
        result, _, _ = self.call("stop", None)
        self.assertIsInstance(result, ValueError)
        self.assertIn("no JSON object", str(result))

    def test_cap_can_be_set_per_repo(self):
        with mock.patch.dict(os.environ, {**ENV, "MAX_OUTPUT_TOKENS": "1234"}):
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        self.assertEqual(module.MAX_OUTPUT_TOKENS, 1234)


class MainCutOff(unittest.TestCase):
    def test_cut_off_review_posts_the_cap_status_and_exits(self):
        pr = {"head": {"sha": "abc123"}, "state": "open", "title": "t", "body": ""}

        def api(method, path, data=None, raw=False):
            return "diff --git a/x b/x\n" if raw else pr

        statuses = []
        with (mock.patch.dict(os.environ, {**ENV, "PR": "7"}),
              mock.patch.object(ai_review, "api", api),
              mock.patch.object(ai_review, "pages", lambda path: iter(())),
              mock.patch.object(ai_review, "repo_rules", lambda: ""),
              mock.patch.object(ai_review, "set_status", lambda *a: statuses.append(a)),
              mock.patch.object(ai_review, "ask_model", side_effect=ai_review.CutOff("cut off")),
              self.assertRaises(SystemExit)):
            ai_review.main()
        self.assertEqual(statuses[-1][1], "error")
        self.assertIn("split the PR or raise MAX_OUTPUT_TOKENS", statuses[-1][2])


PR = {"head": {"sha": "abc123"}, "state": "open", "title": "t", "body": ""}


class MainFailsClosed(unittest.TestCase):
    def run_main(self, set_status, **patches):
        def api(method, path, data=None, raw=False):
            return "diff --git a/x b/x\n" if raw else (PR if method == "GET" else {})

        with (mock.patch.dict(os.environ, {**ENV, "PR": "7"}),
              mock.patch.object(ai_review, "api", patches.pop("api", api)),
              mock.patch.object(ai_review, "pages", lambda path: iter(())),
              mock.patch.object(ai_review, "repo_rules", lambda: ""),
              mock.patch.object(ai_review, "set_status", set_status),
              contextlib.redirect_stdout(io.StringIO()),
              mock.patch.multiple(ai_review, **patches),
              self.assertRaises(SystemExit) as raised):
            ai_review.main()
        return raised.exception

    def test_slow_model_hits_the_deadline_and_sets_an_error_status(self):
        statuses = []
        started = time.monotonic()
        self.run_main(lambda *a: statuses.append(a), MODEL_DEADLINE=1, STARTED=started,
                      ask_model=lambda messages: time.sleep(5))
        self.assertLess(time.monotonic() - started, 4)
        self.assertEqual(statuses[-1][1], "error")
        self.assertIn("deadline; re-run when the Studio is idle", statuses[-1][2])
        self.assertEqual(signal.alarm(0), 0)

    def test_deadline_status_names_the_limit(self):
        statuses = []
        self.run_main(lambda *a: statuses.append(a), MODEL_DEADLINE=2400,
                      ask_model=mock.Mock(side_effect=ai_review.Deadline("slow")))
        self.assertIn("passed its 40-minute deadline", statuses[-1][2])

    def test_deadline_counts_from_the_start_and_is_off_before_the_status(self):
        alarms = []
        with mock.patch.object(ai_review.signal, "alarm", side_effect=alarms.append):
            self.run_main(lambda *a: None, MODEL_DEADLINE=600, STARTED=time.monotonic() - 500,
                          ask_model=mock.Mock(side_effect=RuntimeError("x")))
        self.assertTrue(95 <= alarms[0] <= 100, alarms)
        self.assertEqual(alarms[-1], 0)

    def test_deadline_override_cannot_pass_the_job_limit(self):
        for value, expected in (("3600", 2400), ("600", 600)):
            with mock.patch.dict(os.environ, {**ENV, "MODEL_DEADLINE_SECONDS": value}):
                spec = importlib.util.spec_from_file_location("ai_review_deadline", SCRIPT)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            self.assertEqual(module.MODEL_DEADLINE, expected)

    def test_deadline_is_not_wrapped_by_urllib(self):
        self.assertFalse(issubclass(ai_review.Deadline, OSError))

    def test_deadline_during_the_comment_write_reports_the_deadline(self):
        statuses = []

        def api(method, path, data=None, raw=False):
            if method != "GET":
                raise ai_review.Deadline("slow")
            return "diff --git a/x b/x\n" if raw else PR

        self.run_main(lambda *a: statuses.append(a), MODEL_DEADLINE=2400, api=api,
                      ask_model=mock.Mock(return_value={"findings": []}),
                      validate=lambda result, files, prior: result, render=lambda result, sha: "body")
        self.assertIn("deadline", statuses[-1][2])

    def test_bad_comment_response_sets_an_error_status(self):
        statuses = []

        def api(method, path, data=None, raw=False):
            if method != "GET":
                raise json.JSONDecodeError("truncated", "", 0)
            return "diff --git a/x b/x\n" if raw else PR

        self.run_main(lambda *a: statuses.append(a), api=api,
                      ask_model=mock.Mock(return_value={"findings": []}),
                      validate=lambda result, files, prior: result, render=lambda result, sha: "body")
        self.assertEqual(statuses[-1][1:], ("error", "Review ran but its comment could not be saved; re-run"))

    def test_unexpected_error_still_sets_an_error_status(self):
        statuses = []
        self.run_main(lambda *a: statuses.append(a), ask_model=mock.Mock(side_effect=RuntimeError("x")))
        self.assertEqual(statuses[-1], ("abc123", "error",
                                        "Review could not run: RuntimeError; re-run or reply to retry"))

    def test_failed_final_status_fails_the_job(self):
        def set_status(sha, state, description):
            if state != "pending":
                raise OSError("forgejo down")

        exit_ = self.run_main(set_status, ask_model=mock.Mock(return_value={"findings": []}),
                              validate=lambda result, files, prior: result,
                              render=lambda result, sha: "body")
        self.assertIn("status could not be set", str(exit_.code))


if __name__ == "__main__":
    unittest.main()
