#!/usr/bin/env python3
"""Verify that a successful Prepare Release dispatch recorded this exact candidate."""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

SHA = re.compile(r"[0-9a-f]{40}")
RUN = re.compile(r"[1-9][0-9]*")
CONTEXT = "Release / Qualified candidate"


def verify(server, repository, candidate, base, workflow, job_name, get):
    if not SHA.fullmatch(candidate) or not SHA.fullmatch(base):
        raise ValueError("candidate and base must be full commit SHAs")
    url_prefix = f"{server}/{repository}/actions/runs/"
    statuses = get(f"/commits/{candidate}/status?limit=50").get("statuses") or []
    urls = {
        status["target_url"] for status in statuses
        if status.get("context") == CONTEXT and status.get("status") == "success"
    }
    numbers = {url.removeprefix(url_prefix) for url in urls if url.startswith(url_prefix)}
    if len(numbers) != 1:
        raise ValueError("this PR head has no unique successful Prepare Release record")
    number = next(iter(numbers))
    if not RUN.fullmatch(number):
        raise ValueError("the Prepare Release record has an invalid run number")
    runs = get(f"/actions/runs?page=1&limit=1&run_number={number}").get("workflow_runs") or []
    if len(runs) != 1:
        raise ValueError("the Prepare Release run is unavailable")
    run = runs[0]
    if (
        run["html_url"] != url_prefix + number or run["workflow_id"] != workflow
        or run["trigger_event"] != "workflow_dispatch" or run["status"] != "success"
        or run["commit_sha"] != base or json.loads(run["event_payload"])["ref"] != "refs/heads/main"
    ):
        raise ValueError("the candidate does not match a successful Prepare Release dispatch from main")
    jobs = [
        job for job in get(f"/actions/runs/{int(run['id'])}/jobs")
        if job["name"] == job_name and job["status"] == "success"
    ]
    if len(jobs) != 1:
        raise ValueError("the successful Prepare Release job is unavailable")
    log = get(f"/actions/jobs/{int(jobs[0]['id'])}/logs", raw=True)
    record = f"Qualified release commit: {candidate}"
    if not any(line.rstrip().endswith(record) for line in log.splitlines()):
        raise ValueError("Prepare Release did not record this candidate")


class RejectRedirect(urllib.request.HTTPRedirectHandler):
    # The API and job logs are both on the primary. Keep their read credential there.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: verify-release-qualification.py CANDIDATE PREPARE_WORKFLOW PREPARE_JOB")
    candidate, workflow, job_name = sys.argv[1:]
    try:
        if not SHA.fullmatch(candidate):
            raise ValueError("candidate must be a full commit SHA")
        base = subprocess.check_output(["git", "rev-parse", f"{candidate}^"], text=True).strip()
        for name in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "FORGEJO_READ_TOKEN"):
            if not os.environ.get(name):
                raise ValueError(f"missing {name}")
        server = os.environ["GITHUB_SERVER_URL"].rstrip("/")
        repository = os.environ["GITHUB_REPOSITORY"]
        token = os.environ["FORGEJO_READ_TOKEN"]
        opener = urllib.request.build_opener(RejectRedirect())

        def get(path, raw=False):
            request = urllib.request.Request(
                f"{server}/api/v1/repos/{repository}{path}", headers={"Authorization": f"token {token}"},
            )
            with opener.open(request, timeout=30) as response:
                return response.read().decode("utf-8") if raw else json.load(response)

        verify(server, repository, candidate, base, workflow, job_name, get)
    except (AttributeError, KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"Cannot verify release qualification: {exc}")


if __name__ == "__main__":
    main()
