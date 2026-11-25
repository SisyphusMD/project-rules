import base64
import contextlib
import errno
import importlib.util
import io
import json
import os
import pathlib
import re
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

    def test_cut_off_keeps_the_end_of_its_reasoning_for_the_retry(self):
        tail = "x" * ai_review.RESTATE_REASONING_CHARS
        choices = [{"finish_reason": "length", "message": {"content": "", "reasoning_content": "early " + tail}}]
        result, _, _ = self.call(None, None, choices=choices)
        self.assertIsInstance(result, ai_review.ReasoningCutOff)
        self.assertEqual(result.raw, {"reasoning": tail})
        # Reasoning left in the content, closed or not, is quoted the same way.
        self.assertEqual(self.call("length", "<think>half a thought")[0].raw, {"reasoning": "<think>half a thought"})
        self.assertIsInstance(self.call("length", "<think>a</think> ")[0], ai_review.ReasoningCutOff)
        self.assertIsNone(self.call("length", "")[0].raw)

    def test_cut_off_mid_answer_is_not_retried(self):
        # A finding already written could be lost by a retry, so these fail closed in main.
        for result in (self.call("length", '<think>a</think>{"summary": "s", "findings": [{"id": "F1"')[0],
                       self.call(None, None, choices=[{"finish_reason": "length"}])[0]):
            self.assertIsInstance(result, ai_review.CutOff)
            self.assertNotIsInstance(result, ai_review.ReasoningCutOff)

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
        # Named ValueErrors, which the retry puts back to the model, never a KeyError or TypeError.
        self.assertRegex(str(self.call("stop", "", choices=[])[0]), "no choices")
        self.assertRegex(str(self.call("stop", "", choices=["x"])[0]), "no choices")
        self.assertRegex(str(self.call("stop", "", choices=[{"finish_reason": "stop"}])[0]), "no message")

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


PR = {"head": {"sha": "abc123"}, "state": "open", "title": "t", "body": ""}


class MainCutOff(unittest.TestCase):
    def test_cut_off_mid_answer_posts_the_cap_status_and_exits(self):
        def api(method, path, data=None, raw=False):
            return "diff --git a/x b/x\n" if raw else PR

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
        self.assertIn("cap mid-answer: split the PR or raise MAX_OUTPUT_TOKENS", statuses[-1][2])


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


GOOD = {"id": "F1", "file": "x", "line": 3, "severity": "suggestion", "status": "open",
        "title": "good one", "detail": "d", "response": ""}
BAD = {"id": "F5", "file": "x", "line": 3, "severity": "major", "status": "open",
       "title": "bad one", "detail": "d", "response": ""}


def answer(*findings):
    return {"summary": "s", "findings": list(findings)}


class MainReasks(unittest.TestCase):
    """A malformed answer is put back to the model once; a second one fails the check but is shown."""

    def run_main(self, answers, prior=None, comments=None):
        posted, statuses, asked = [], [], []
        self.schemas = []
        replies = iter(answers)

        def ask(messages, schema=None):
            asked.append(messages)
            self.schemas.append(schema)
            item = next(replies)
            if isinstance(item, Exception):
                raise item
            return item

        def api(method, path, data=None, raw=False):
            if method != "GET":
                posted.append(data["body"])
                return {}
            return "diff --git a/x b/x\n" if raw else PR

        comments = comments or []
        if prior is not None:
            state = base64.b64encode(json.dumps(prior).encode()).decode()
            comments = [{"id": 1, "user": {"login": ai_review.BOT},
                         "body": f"{ai_review.MARKER}\n<!-- ai-review-state {state} -->"}]
        out = io.StringIO()
        with (mock.patch.dict(os.environ, {**ENV, "PR": "7"}),
              mock.patch.object(ai_review, "api", api),
              mock.patch.object(ai_review, "pages", lambda path: iter(comments)),
              mock.patch.object(ai_review, "repo_rules", lambda: ""),
              mock.patch.object(ai_review, "set_status", lambda *a: statuses.append(a)),
              mock.patch.object(ai_review, "ask_model", ask),
              contextlib.redirect_stdout(out)):
            try:
                ai_review.main()
                code = 0
            except SystemExit as e:
                code = e.code
        return code, statuses, posted, asked

    def test_invalid_severity_is_put_back_to_the_model_once(self):
        code, statuses, posted, asked = self.run_main([answer(GOOD, BAD), answer(GOOD, {**BAD, "severity": "blocking",
                                                                                          "line": None})])
        self.assertEqual(len(asked), 2)
        retry = asked[1][-1]["content"]
        self.assertIn("finding F5 has an invalid severity or status", retry)
        self.assertEqual(asked[1][:-1], asked[0])
        self.assertEqual((code, statuses[-1][1]), (0, "success"))
        self.assertIn("good one", posted[0])

    def test_blocking_finding_still_fails_the_check_without_a_retry(self):
        blocker = {**GOOD, "id": "F2", "severity": "blocking"}
        code, statuses, _, asked = self.run_main([answer(blocker)])
        self.assertEqual((code, len(asked), statuses[-1][1:]), (1, 1, ("failure", "1 blocking: F2")))

    def test_an_id_that_is_not_a_string_is_put_back_like_any_other_malformed_finding(self):
        code, statuses, _, asked = self.run_main([answer({**GOOD, "id": {}}), answer(GOOD)])
        self.assertEqual((code, len(asked), statuses[-1][1]), (0, 2, "success"))

    def test_finding_without_an_id_twice_is_named_in_the_comment(self):
        nameless = {k: v for k, v in GOOD.items() if k != "id"}
        code, statuses, posted, _ = self.run_main([answer(nameless), answer(nameless)])
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("finding without an id", posted[0])

    def test_both_errors_and_the_blocking_ids_are_reported(self):
        blocker = {**GOOD, "id": "F2", "severity": "blocking"}
        gone = ValueError("no JSON object in the model's answer")
        _, statuses, posted, _ = self.run_main([gone, answer(blocker, BAD)])
        self.assertIn("F5", posted[0])
        self.assertIn("blocking: F2", statuses[-1][2])
        self.assertNotIn("No findings.", posted[0])

    def test_retry_cut_off_at_its_cap_fails_and_keeps_the_first_answers_findings(self):
        code, statuses, posted, _ = self.run_main([answer(GOOD, BAD), ai_review.CutOff("cut off at 16000")])
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("good one", posted[0])
        self.assertIn("second answer: cut off at 16000", posted[0])

    def test_reasoning_cut_off_at_the_cap_is_retried_under_the_schema(self):
        # A small PR whose review only reasoned until the cap (k8s#2688) passes on the retry.
        cut = ai_review.ReasoningCutOff("cut off at 40000", {"reasoning": "F1 looks real"})
        code, statuses, posted, asked = self.run_main([cut, answer(GOOD)])
        self.assertEqual((code, statuses[-1][1:]), (0, ("success", "No blocking findings (1 total, after a retry)")))
        self.assertEqual(self.schemas, [None, ai_review.ANSWER_SCHEMA])
        note = asked[1][-1]["content"]
        self.assertIn("Review the whole diff again", note)
        self.assertIn("F1 looks real", note)
        self.assertIn("good one", posted[0])

    def test_a_cut_off_with_no_reasoning_is_retried_without_a_quote(self):
        code, _, _, asked = self.run_main([ai_review.ReasoningCutOff("cut off at 40000"), answer()])
        self.assertEqual(code, 0)
        self.assertNotIn("The rejected answer was", asked[1][-1]["content"])

    def test_cut_off_twice_fails_the_check_and_says_why(self):
        code, statuses, posted, _ = self.run_main([ai_review.ReasoningCutOff("cut off at 40000"),
                                                    ai_review.ReasoningCutOff("cut off at 16000")])
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("first answer: cut off at 40000", posted[0])
        self.assertIn("second answer: cut off at 16000", posted[0])

    def test_a_finding_the_retry_leaves_out_still_counts(self):
        blocker = {**GOOD, "id": "F2", "severity": "blocking"}
        code, statuses, posted, _ = self.run_main([answer(blocker, BAD), answer(GOOD)])
        self.assertEqual((code, statuses[-1][1:]), (1, ("failure", "1 blocking: F2")))
        state = json.loads(base64.b64decode(posted[0].split("ai-review-state ")[1].split(" ")[0]))
        self.assertEqual(sorted(f["id"] for f in state), ["F1", "F2"])

    def test_a_finding_restated_by_the_retry_is_taken_from_the_retry(self):
        first = {**GOOD, "title": "first wording"}
        code, _, posted, _ = self.run_main([answer(first, BAD), answer({**GOOD, "title": "second wording"})])
        self.assertEqual(code, 0)
        self.assertIn("second wording", posted[0])
        self.assertNotIn("first wording", posted[0])

    def test_a_finding_the_retry_resolves_stays_resolved(self):
        saved = {**GOOD, "id": "F2", "severity": "blocking"}
        code, statuses, _, _ = self.run_main([answer(BAD), answer({**saved, "status": "resolved"})], prior=[saved])
        self.assertEqual((code, statuses[-1][1]), (0, "success"))

    def test_a_success_after_a_retry_says_so_in_the_status(self):
        _, statuses, _, _ = self.run_main([ValueError("no JSON object in the model's answer"), answer()])
        self.assertEqual(statuses[-1][1:], ("success", "No blocking findings (0 total, after a retry)"))

    def test_a_retry_with_a_bad_server_reply_still_fails_closed(self):
        _, statuses, posted, _ = self.run_main([answer(BAD), KeyError("model")])
        self.assertEqual(statuses[-1][1], "error")
        self.assertEqual(posted, [])

    def test_successful_retry_notes_the_rejection_but_keeps_it_out_of_the_state(self):
        code, statuses, posted, _ = self.run_main([answer(BAD), answer(GOOD)])
        self.assertEqual((code, statuses[-1][1]), (0, "success"))
        self.assertNotIn("Malformed", posted[0])
        self.assertIn("first answer was rejected (finding F5 has an invalid severity or status: ", posted[0])
        state = base64.b64decode(posted[0].split("ai-review-state ")[1].split(" ")[0]).decode()
        self.assertNotIn("malformed", state)
        self.assertNotIn("rejected", state)

    def test_first_answers_good_findings_survive_an_unreadable_retry(self):
        gone = ValueError("no JSON object in the model's answer")
        code, statuses, posted, _ = self.run_main([answer(GOOD, BAD), gone])
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("good one", posted[0])
        self.assertIn("second answer: no JSON object", posted[0])

    def test_unreadable_api_envelope_is_put_back_to_the_model_once(self):
        code, statuses, _, asked = self.run_main([IndexError("list index out of range"), answer(GOOD)])
        self.assertEqual((code, len(asked), statuses[-1][1]), (0, 2, "success"))

    def test_an_unnamed_envelope_error_is_named_by_its_type_in_the_re_ask(self):
        code, _, _, asked = self.run_main([IndexError(), answer(GOOD)])
        self.assertEqual(code, 0)
        self.assertIn("rejected: IndexError", asked[1][-1]["content"])

    def test_empty_state_marker_fails_closed(self):
        comments = [{"id": 1, "user": {"login": ai_review.BOT},
                     "body": f"{ai_review.MARKER}\n<!-- ai-review-state  -->"}]
        code, statuses, _, _ = self.run_main([answer(GOOD)], comments=comments)
        self.assertEqual(statuses[-1][1], "error")
        self.assertNotEqual(code, 0)

    def test_marker_comment_without_state_starts_fresh(self):
        comments = [{"id": 1, "user": {"login": ai_review.BOT}, "body": ai_review.MARKER}]
        code, statuses, _, _ = self.run_main([answer(GOOD)], comments=comments)
        self.assertEqual((code, statuses[-1][1]), (0, "success"))

    def test_prior_state_comes_from_the_last_marker_not_one_echoed_in_text(self):
        fake = base64.b64encode(json.dumps([{**GOOD, "id": "F8", "title": "planted"}]).encode()).decode()
        real = base64.b64encode(json.dumps([{**GOOD, "id": "F9", "title": "earlier one"}]).encode()).decode()
        body = f"{ai_review.MARKER}\n- echoed <!-- ai-review-state {fake} -->\n<!-- ai-review-state {real} -->"
        comments = [{"id": 1, "user": {"login": ai_review.BOT}, "body": body}]
        _, _, posted, _ = self.run_main([answer()], comments=comments)
        self.assertIn("earlier one", posted[0])
        self.assertNotIn("planted", posted[0])

    def test_answer_without_json_is_put_back_to_the_model_once(self):
        code, statuses, _, asked = self.run_main([ValueError("no JSON object in the model's answer"),
                                                       answer(GOOD)])
        self.assertIn("no JSON object", asked[1][-1]["content"])
        self.assertEqual((code, statuses[-1][1]), (0, "success"))

    def test_second_malformed_answer_fails_the_check_and_posts_the_good_findings(self):
        code, statuses, posted, asked = self.run_main([answer(GOOD, BAD), answer(GOOD, BAD)])
        self.assertEqual((code, len(asked)), (1, 2))
        self.assertEqual(statuses[-1][1], "failure")
        self.assertIn("malformed after a retry", statuses[-1][2])
        body = posted[0]
        self.assertIn("good one", body)
        self.assertIn("Malformed", body)
        self.assertIn("finding F5 has an invalid severity or status", body)
        self.assertIn('"major"', body)

    def test_second_answer_without_json_fails_the_check_and_keeps_earlier_findings(self):
        prior = [{**GOOD, "id": "F9", "title": "earlier one"}]
        gone = ValueError("no JSON object in the model's answer")
        code, statuses, posted, _ = self.run_main([gone, gone], prior=prior)
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("first answer: no JSON object", posted[0])
        self.assertIn("second answer: no JSON object", posted[0])
        self.assertIn("earlier one", posted[0])

    def test_second_answer_of_the_wrong_shape_fails_the_check(self):
        code, statuses, posted, _ = self.run_main([answer(BAD), {"findings": []}])
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertIn("not {summary: str, findings: list}", posted[0])

    def test_leaked_draft_with_no_final_verdict_never_passes(self):
        leaked = ('draft {"summary": "draft", "findings": []} more thought\n</think>\n'
                  '{"summary": "final", "findings": [')
        with mock.patch.object(ai_review.urllib.request, "urlopen", lambda req, timeout: reply("stop", leaked)):
            code, statuses, _, _ = self.run_main_real_model()
        self.assertEqual((code, statuses[-1][1]), (1, "failure"))
        self.assertNotIn("success", [s[1] for s in statuses])

    def run_main_real_model(self):
        statuses, posted = [], []

        def api(method, path, data=None, raw=False):
            if method != "GET":
                posted.append(data["body"])
                return {}
            return "diff --git a/x b/x\n" if raw else PR

        with (mock.patch.dict(os.environ, {**ENV, "PR": "7", "MODEL": "m", "LLM_URL": "http://llm/v1"}),
              mock.patch.object(ai_review, "api", api),
              mock.patch.object(ai_review, "pages", lambda path: iter(())),
              mock.patch.object(ai_review, "repo_rules", lambda: ""),
              mock.patch.object(ai_review, "set_status", lambda *a: statuses.append(a)),
              contextlib.redirect_stdout(io.StringIO())):
            try:
                ai_review.main()
                code = 0
            except SystemExit as e:
                code = e.code
        return code, statuses, posted, None


class Restate(unittest.TestCase):
    """The retry restates the first answer under ANSWER_SCHEMA, so its shape cannot be wrong."""

    run_main = MainReasks.run_main

    def test_only_the_retry_is_constrained_to_the_schema(self):
        code, _, _, asked = self.run_main([ai_review.NoJSON({"content": "", "reasoning": ""}), answer(GOOD)])
        self.assertEqual(code, 0)
        self.assertEqual(self.schemas, [None, ai_review.ANSWER_SCHEMA])
        self.assertIn("Restate the review", asked[1][-1]["content"])

    def test_restate_quotes_the_answer_text_and_the_end_of_the_reasoning(self):
        raw = {"content": "F1 is a real bug in x", "reasoning": "long thought ... so the verdict is F1"}
        _, _, _, asked = self.run_main([ai_review.NoJSON(raw), answer(GOOD)])
        self.assertIn("F1 is a real bug in x", asked[1][-1]["content"])
        self.assertIn("so the verdict is F1", asked[1][-1]["content"])

    def test_a_server_error_body_is_put_back_once(self):
        empty = ValueError('model reply has no choices: {"error": "overloaded"}')
        code, statuses, _, asked = self.run_main([empty, answer(GOOD)])
        self.assertEqual((code, len(asked), statuses[-1][1]), (0, 2, "success"))

    def test_a_broken_script_is_an_error_not_a_malformed_answer(self):
        code, statuses, posted, asked = self.run_main([KeyError("MODEL")])
        self.assertEqual((len(asked), statuses[-1][1]), (1, "error"))
        self.assertNotEqual(code, 0)
        self.assertEqual(posted, [])

    def test_long_answers_keep_the_end_of_the_text_and_reasoning(self):
        text = "x" * 20000 + " TEXT VERDICT F1"
        reasoning = "y" * 50000 + " REASONED VERDICT F1"
        raw = {"content": ai_review.clip(text, ai_review.RESTATE_CONTENT_CHARS),
               "reasoning": reasoning[-ai_review.RESTATE_REASONING_CHARS:]}
        _, _, _, asked = self.run_main([ai_review.NoJSON(raw), answer(GOOD)])
        note = asked[1][-1]["content"]
        self.assertIn("TEXT VERDICT F1", note)
        self.assertIn("REASONED VERDICT F1", note)
        self.assertLess(len(note), ai_review.RESTATE_CONTENT_CHARS + ai_review.RESTATE_REASONING_CHARS + 600)

    def test_a_long_parsed_answer_is_clipped_in_the_quote(self):
        huge = {**BAD, "detail": "d" * 30000 + " END"}
        _, _, _, asked = self.run_main([answer(huge), answer(GOOD)])
        note = asked[1][-1]["content"]
        self.assertLess(len(note), ai_review.RESTATE_CONTENT_CHARS + 1200)
        self.assertIn("END", note)

    def test_a_refused_schema_still_reviews_end_to_end(self):
        seen = []

        def ask(messages, schema=None):
            seen.append(schema)
            if len(seen) == 1:
                raise ai_review.NoJSON({"content": "prose", "reasoning": ""})
            if schema:
                raise ai_review.urllib.error.HTTPError("u", 400, "bad", {},
                                                       io.BytesIO(b"response_format unsupported"))
            return answer(GOOD)

        with mock.patch.object(ai_review, "get_result", ai_review.get_result):
            code, statuses, posted = self.main_with(ask)
        self.assertEqual((code, statuses[-1][1]), (0, "success"))
        self.assertEqual(seen, [None, ai_review.ANSWER_SCHEMA, None])
        self.assertIn("first answer was rejected", posted[0])

    def main_with(self, ask):
        posted, statuses = [], []

        def api(method, path, data=None, raw=False):
            if method != "GET":
                posted.append(data["body"])
                return {}
            return "diff --git a/x b/x\n" if raw else PR

        with (mock.patch.dict(os.environ, {**ENV, "PR": "7"}),
              mock.patch.object(ai_review, "api", api),
              mock.patch.object(ai_review, "pages", lambda path: iter(())),
              mock.patch.object(ai_review, "repo_rules", lambda: ""),
              mock.patch.object(ai_review, "set_status", lambda *a: statuses.append(a)),
              mock.patch.object(ai_review, "ask_model", ask),
              contextlib.redirect_stdout(io.StringIO())):
            try:
                ai_review.main()
                code = 0
            except SystemExit as e:
                code = e.code
        return code, statuses, posted

    def refused(self, code, body):
        calls = []

        def ask(messages, schema=None):
            calls.append(schema)
            if schema:
                raise ai_review.urllib.error.HTTPError("u", code, "refused", {}, io.BytesIO(body))
            return answer(GOOD)

        with mock.patch.object(ai_review, "ask_model", ask), contextlib.redirect_stdout(io.StringIO()):
            result = ai_review.restate([], "note")
        return result, calls

    def test_a_server_that_refuses_the_schema_gets_a_free_retry(self):
        for code in (400, 422):
            result, calls = self.refused(code, b'{"error": "response_format json_schema is not supported"}')
            self.assertEqual((result, calls), (answer(GOOD), [ai_review.ANSWER_SCHEMA, None]))

    def test_a_400_for_another_reason_is_not_retried_without_the_schema(self):
        with self.assertRaises(ai_review.urllib.error.HTTPError):
            self.refused(400, b'{"error": "prompt is longer than the context window"}')

    def test_other_http_errors_on_the_retry_still_fail_closed(self):
        def ask(messages, schema=None):
            raise ai_review.urllib.error.HTTPError("u", 502, "bad gateway", {}, None)

        with mock.patch.object(ai_review, "ask_model", ask), self.assertRaises(ai_review.urllib.error.HTTPError):
            ai_review.restate([], "note")

    def test_schema_allows_exactly_what_validate_accepts(self):
        item = ai_review.ANSWER_SCHEMA["properties"]["findings"]["items"]
        self.assertEqual(set(item["properties"]["severity"]["enum"]), {"blocking", "suggestion"})
        self.assertEqual(set(item["properties"]["status"]["enum"]), {"open", "resolved", "withdrawn"})
        self.assertIn("id", item["required"])
        pattern = item["properties"]["id"]["pattern"]
        self.assertIsNone(re.search(pattern, "   "))
        self.assertIsNone(re.search(pattern, ""))
        self.assertIsNotNone(re.search(pattern, "F1"))
        self.assertEqual(ai_review.ANSWER_SCHEMA["required"], ["summary", "findings"])
        # A finding the grammar can produce passes validate untouched.
        self.assertEqual(ai_review.validate(answer(GOOD), {"x"}, [])["findings"], [GOOD])


class AskModelSchema(unittest.TestCase):
    def ask(self, message, schema=None):
        sent = []

        def urlopen(req, timeout):
            sent.append(json.loads(req.data))
            return reply(None, None, usage={}, choices=[{"finish_reason": "stop", "message": message}])

        env = {"MODEL": "m", "LLM_URL": "http://llm/v1/chat/completions"}
        with mock.patch.dict(os.environ, env), mock.patch.object(ai_review.urllib.request, "urlopen", urlopen), \
                contextlib.redirect_stdout(io.StringIO()):
            try:
                return ai_review.ask_model([], schema=schema), sent
            except ValueError as e:
                return e, sent

    def test_a_schema_is_sent_as_a_strict_response_format(self):
        _, sent = self.ask({"content": '{"summary": "s", "findings": []}'}, schema=ai_review.ANSWER_SCHEMA)
        fmt = sent[0]["response_format"]
        self.assertEqual((fmt["type"], fmt["json_schema"]["strict"]), ("json_schema", True))
        self.assertEqual(fmt["json_schema"]["schema"], ai_review.ANSWER_SCHEMA)

    def test_no_schema_sends_no_response_format(self):
        _, sent = self.ask({"content": '{"summary": "s", "findings": []}'})
        self.assertNotIn("response_format", sent[0])

    def test_an_answer_without_json_keeps_its_text_and_reasoning_tail(self):
        reasoning = "x" * (ai_review.RESTATE_REASONING_CHARS + 50) + "THE END"
        e, _ = self.ask({"content": "prose only", "reasoning_content": reasoning})
        self.assertIsInstance(e, ai_review.NoJSON)
        self.assertEqual(str(e), "no JSON object in the model's answer")
        self.assertEqual(e.raw["content"], "prose only")
        self.assertTrue(e.raw["reasoning"].endswith("THE END"))
        self.assertEqual(len(e.raw["reasoning"]), ai_review.RESTATE_REASONING_CHARS)

    def test_a_schema_request_gets_the_smaller_output_cap(self):
        _, sent = self.ask({"content": '{"summary": "s", "findings": []}'}, schema=ai_review.ANSWER_SCHEMA)
        self.assertEqual(sent[0]["max_tokens"], ai_review.RESTATE_OUTPUT_TOKENS)
        _, sent = self.ask({"content": '{"summary": "s", "findings": []}'})
        self.assertEqual(sent[0]["max_tokens"], ai_review.MAX_OUTPUT_TOKENS)

    def test_long_text_keeps_its_start_and_end(self):
        clipped = ai_review.clip("A" + "x" * 10000 + "Z", 100)
        self.assertTrue(clipped.startswith("A") and clipped.endswith("Z"))
        self.assertLess(len(clipped), 120)
        self.assertEqual(ai_review.clip("short", 100), "short")

    def test_a_server_error_body_raises_an_unreadable_error(self):
        sent = []

        def urlopen(req, timeout):
            sent.append(1)
            return mock.MagicMock(__enter__=lambda s: io.BytesIO(b'{"error": "overloaded"}'),
                                  __exit__=lambda *a: False)

        env = {"MODEL": "m", "LLM_URL": "http://llm/v1/chat/completions"}
        with (mock.patch.dict(os.environ, env), mock.patch.object(ai_review.urllib.request, "urlopen", urlopen),
              self.assertRaisesRegex(ValueError, "no choices")):
            ai_review.ask_model([])


class ValidateFindings(unittest.TestCase):
    def test_strict_still_raises_on_the_first_malformed_finding(self):
        with self.assertRaisesRegex(ValueError, "F5 has an invalid severity"):
            ai_review.validate(answer(GOOD, BAD), {"x"}, [])

    def test_lenient_keeps_the_good_findings_and_names_each_bad_one(self):
        nameless = {"file": "x", "severity": "blocking"}
        result = ai_review.validate(answer(GOOD, BAD, nameless, "text"), {"x"}, [], lenient=True)
        self.assertEqual([f["id"] for f in result["findings"]], ["F1"])
        self.assertEqual(len(result["malformed"]), 3)
        self.assertIn("F5", result["malformed"][0])
        self.assertIn("without an id", result["malformed"][1])

    def test_a_blocking_finding_needs_an_integer_line_not_a_bool(self):
        for line, severity in ((True, "suggestion"), (3.0, "suggestion"), (3, "blocking")):
            f = dict(GOOD, severity="blocking", line=line)
            self.assertEqual(ai_review.validate(answer(f), {"x"}, [])["findings"][0]["severity"], severity, line)

    def test_a_carried_blocker_saved_with_a_bool_line_is_held_to_the_check(self):
        saved = dict(GOOD, id="F9", severity="blocking", line=True)
        kept = dict(GOOD, id="F8", severity="blocking", line=4, file="gone")
        carried = {f["id"]: f for f in ai_review.validate(answer(GOOD), {"x"}, [saved, kept])["findings"]}
        self.assertEqual(carried["F9"]["severity"], "suggestion")
        self.assertEqual(saved["severity"], "blocking")
        self.assertEqual(carried["F8"], kept)

    def test_the_schema_line_is_an_integer_like_validate(self):
        item = ai_review.ANSWER_SCHEMA["properties"]["findings"]["items"]
        self.assertEqual(item["properties"]["line"], {"type": "integer"})


class BoundReplies(unittest.TestCase):
    def test_short_threads_pass_unchanged(self):
        self.assertEqual(ai_review.bound_replies(["a", "b"]), ["a", "b"])
        self.assertEqual(ai_review.bound_replies([]), [])

    def test_a_long_reply_keeps_its_start_and_its_conclusion(self):
        long = "START" + "x" * ai_review.MAX_REPLY_CHARS + "CONCLUSION"
        (only,) = ai_review.bound_replies([long])
        self.assertTrue(only.startswith("START") and only.endswith("CONCLUSION"))
        self.assertIn("[...]", only)
        self.assertLess(len(only), ai_review.MAX_REPLY_CHARS + 10)

    def test_the_oldest_replies_go_first_and_the_total_stays_bounded(self):
        replies = [f"{i}:" + "y" * (ai_review.MAX_REPLY_CHARS - 10) for i in range(20)]
        kept = ai_review.bound_replies(replies)
        self.assertRegex(kept[0], r"^\[\d+ older replies omitted\]$")
        self.assertTrue(kept[-1].startswith("19:"))
        self.assertEqual([r.split(":")[0] for r in kept[1:]],
                         [str(i) for i in range(20 - len(kept) + 1, 20)])
        self.assertLessEqual(sum(map(len, kept[1:])), ai_review.MAX_REPLIES_CHARS)


class MainBoundsReplies(unittest.TestCase):
    run_main = MainReasks.run_main

    def test_the_prompt_carries_only_the_newest_replies_within_the_bound(self):
        comments = [{"user": {"login": "maintainer"}, "created_at": f"t{i}",
                     "body": f"reply {i} " + "z" * ai_review.MAX_REPLY_CHARS} for i in range(20)]
        code, _, _, asked = self.run_main([answer(GOOD)], comments=comments)
        self.assertEqual(code, 0)
        prompt = asked[0][1]["content"]
        section = prompt.split("Replies on the PR, oldest first:\n", 1)[1].split("\n\nDiff:\n", 1)[0]
        self.assertIn("older replies omitted", section)
        self.assertIn("reply 19 ", section)
        self.assertNotIn("reply 0 ", section)
        self.assertLess(len(section), ai_review.MAX_REPLIES_CHARS + 500)


class ReviewWorkflow(unittest.TestCase):
    TEXT = (SCRIPT.parents[1] / "workflows/ai-review.yml").read_text()

    def test_the_job_skips_the_same_login_the_script_treats_as_its_own(self):
        skipped = re.search(r"comment\.user\.login != '([^']+)'", self.TEXT).group(1)
        configured = re.search(r"(?m)^ +BOT_LOGIN: (\S+)$", self.TEXT).group(1)
        self.assertEqual(skipped, configured)
        # The script's own default (read from its source, so an ambient BOT_LOGIN cannot interfere),
        # so a shared typo in both cannot pass.
        default = re.search(r'os\.environ\.get\("BOT_LOGIN", "([^"]+)"\)', SCRIPT.read_text()).group(1)
        self.assertEqual(configured, default)

    def test_the_checkout_is_the_base_commit_without_saved_credentials(self):
        step = re.search(r"(?ms)uses: actions/checkout@\S+.*?(?=\n      - )", self.TEXT).group(0)
        self.assertIn("ref: ${{ github.sha }}", step)
        self.assertIn("persist-credentials: false", step)


class SharedReviewWorkflow(ReviewWorkflow):
    # The job repos call (#78) must hold the same pins as the copied one.
    TEXT = (SCRIPT.parents[1] / "workflows/review.yml").read_text()


if __name__ == "__main__":
    unittest.main()
