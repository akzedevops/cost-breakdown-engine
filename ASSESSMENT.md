# Assessment Report: Cost Breakdown Engine (FinOps Layer)

Reviewed: Cost Breakdown Engine by Amit Kattyan (`kattyanami/cost-breakdown-engine`, commit `559073d`)
Reviewer: Aung Khant Zaw
Review fork with fixes and CI: https://github.com/akzedevops/cost-breakdown-engine
Date: June 11, 2026

**Score: 8 / 10**

---

## 1. Summary

The submission covers all six tickets from the brief (T1 to T6). I cloned it, ran the test suite, started the backend and the frontend, hit every endpoint, and recomputed all the numbers myself from the raw JSON rather than trusting the README. The numbers are correct: the total is $2,587.66 across 26 resources and every breakdown reconciles to it exactly. The code is cleanly layered and the assumptions in the README are honest. The brief asked for clean over complex, and that is what the developer built.

So why 8 and not higher? Two reasons. First, robustness: there is no input validation at all, and I found one real crash where an empty dataset turns `/api/summary` into an HTTP 500. Second, delivery: no CI, a frontend Docker build that ignored its own lockfile, and both containers running as root. The role this exercise is for is Backend DevOps, so I weigh delivery and operational gaps more heavily than I would for a pure application role.

The delivery problems (F3, F4, F5, F9) are already fixed on this fork, with a CI pipeline that's green on the latest run. Section 7 covers what was done and what the pipeline caught the first time it ran. I did not touch the aggregation logic or any test assertion. The fork keeps the two original commits untouched with my changes on top, so everything I changed is one diff away:

```
git diff 559073d..HEAD
```

or on GitHub: https://github.com/akzedevops/cost-breakdown-engine/compare/559073d...main

Overall: the engine itself is correct and well built. Everything I would change sits around it (validation, delivery, packaging), not inside it. Those fixes are minor and none of them touch the logic.

## 2. What I did

1. Read the brief and noted the mandatory items, the out-of-scope list, and the evaluation criteria.
2. Set up from scratch following only the README (local Python + Node path; the Docker path is exercised by the CI image builds).
3. Ran the shipped tests: 33/33 pass in about 0.3 seconds.
4. Hit every endpoint and recomputed the totals independently from `mock_costs.json`.
5. Probed what the test suite doesn't cover: empty dataset, invalid categories and environments, negative costs, bad query params, wrong HTTP methods.
6. Reviewed the code, the Dockerfiles, compose, and dependency management.
7. Fixed the delivery findings on this fork and let the CI runs prove it.

## 3. Validation results

The tests themselves are well built: expected values are computed from the raw data file instead of hardcoded, so they verify reconciliation rather than memorize answers. API checks:

| Check | Result |
|---|---|
| `/api/summary` vs my own sum of the raw JSON | Match. $2,587.66, 26 resources. No double counting, nothing dropped. |
| Category / service / environment sums vs total | Exact on cost. Percentages come to 99.99 on services, which is just rounding. |
| Sort order (cost desc; prod → staging → dev) | Correct. |
| `/api/resources` filters | Work, case-insensitive. An unknown value returns an empty list, not an error. |
| POST on a GET endpoint | 405, as it should be. |
| Insight rules | All fire. One detail I liked: the right-sizing threshold is 30% and the data sits at 30.7%, so that boundary is genuinely exercised, not passed by luck. |
| `INSIGHTS_*` env overrides | Confirmed working at runtime. |
| Frontend production build | Builds fine. Dashboard shows the same numbers the API returns; loading and error states handled. |

Two things the shipped tests don't cover, both confirmed by actually running them (details in section 5): an empty dataset crashes `/api/summary`, and the `Resource` model accepts invalid data silently: negative costs, unknown categories, misspelled environments.

## 4. Architecture

### What's good

- The layering is right. `models.py` holds the schema, `aggregator.py` holds pure grouping logic, `insights.py` builds rules on top, and `main.py` stays a thin HTTP layer. Not a single script, not over-engineered either.
- The data model is a flat record shaped like a Cost Explorer row, so swapping mock data for live billing only touches the loader, and there's a usable boto3 sketch in the docstring.
- Insight thresholds live in a typed Pydantic Settings class with env-var overrides. The non-prod ratio and concentration rules are signals a platform team would actually act on.
- The README's assumptions are correct about single-account-with-tags versus account-per-environment under AWS Organizations, including exactly what would change (`account_id` field, grouping by `LINKED_ACCOUNT`). That's real cost-allocation knowledge, not filler.

### Problems

- The "production swap point" is a comment, not an abstraction. Every aggregation function calls `_load_resources()` directly; nothing can be injected. That's also why the tests only run against the one shipped JSON file, and why the empty-dataset crash was never caught.
- One `/api/insights` call reads and parses the JSON four times, and `get_summary()` re-derives all three groupings internally. Invisible at 26 resources, wasteful as a pattern.
- `get_by_service()` groups by `(service, category)` pairs. In real AWS a service can span categories (EC2 spans compute and data transfer), and such a service would render as duplicate rows and break one of his own tests.
- Money is `float`. Safe here (I verified the sums reconcile), but `Decimal` or integer cents is the defensible choice in a tool whose whole job is reconciling costs.

## 5. Findings

Severity reflects production readiness, not the demo.

| # | Severity | Finding |
|---|---|---|
| F1 | High | Empty dataset crashes `/api/summary` with an unhandled `ValueError` (HTTP 500). `get_summary()` calls `max()` on an empty dict. The `_pct` helper right next to it has a zero-total guard and a test; the `max()` calls have neither. The test file docstring even claims empty-input coverage that doesn't exist. |
| F2 | High | No model validation. Negative costs, `category="not-a-category"`, a misspelled environment: all accepted, and all flow straight into the aggregates. Pydantic v2 is already there; fixing this is two `Literal` types and one `ge=0`. |
| F3 | High | No CI. The tests exist but nothing runs them on push. Fixed on this fork; see section 7. |
| F4 | Medium | Frontend image wasn't reproducible. The Dockerfile copied `package.json` only and ran `npm install`; the committed lockfile was never used. Fixed on this fork. |
| F5 | Medium | Both containers ran as root, no healthchecks, tests shipped inside the production image, `depends_on` without a condition. Fixed on this fork. |
| F6 | Medium | Service grouping uses `(service, category)` pairs. Works on this dataset, fragile against the very data model it copies. |
| F7 | Low | Money is `float`, see section 4. |
| F8 | Low | The JSON file is re-read on every request, four times for a single `/api/insights` call. Harmless at this size. It becomes a problem the day the dataset grows. |
| F9 | Low | Lint-level stuff: unused import, deprecated `Optional[X]`, unsorted imports, a dead `total` prop in `ServiceTable`. Fixed on this fork. |

## 6. Score

Scored against the brief's own five evaluation criteria:

| Criterion | Score | Note |
|---|---|---|
| Clarity and correctness of cost breakdown logic | 9 / 10 | Verified end to end; totals reconcile exactly. Only thing holding it back is float money (F7). |
| Ability to structure and aggregate data cleanly | 8 / 10 | Clean single-pass grouping. Minus for the re-load-per-request pattern (F8) and the pair-grouping fragility (F6). |
| Simplicity and usability of UI/API | 8 / 10 | Sensible endpoints, OpenAPI docs, a dashboard that works. He shipped both UI and API where the brief required one. |
| Code quality and modular design | 7 / 10 | The code is clean, but there's no data-source abstraction, no validation (F2), and the lint findings were real (F9). |
| Thoughtfulness about real-world cost scenarios | 9 / 10 | The account-model analysis in his README goes beyond what the exercise asked for. |
| **Overall** | **8 / 10** | |

I considered 9, but F1 and F2 are robustness defects in the core path, the docstring makes a test-coverage claim that isn't true, and the delivery basics were missing. I also considered 7 and decided that was unfair: everything that exists works exactly as documented, the numbers are right, and the assumption analysis shows judgment beyond what the exercise asked for. Every claim in the submission held up when I checked it, except the one about edge-case tests.

## 7. What I fixed on this fork, and the CI/CD detail

I fixed F3, F4, F5 and F9 directly instead of just recommending them, because in a real handover the pipeline is the first thing I'd put in place anyway. My commits on top of his two:

```
Add CI quality gates: linting, vuln scanning, container hardening
Fix Trivy action ref: tags are v-prefixed, pin v0.36.0
Patch frontend image: explicit non-root USER + apk upgrade
Bump checkout/setup-node/setup-python to v6 (Node 20 runner deprecation)
Add assessment report; restore original README from submission
```

The latest Actions run is green across all seven jobs: https://github.com/akzedevops/cost-breakdown-engine/actions

One disclosure: the formatting fixes touched his test files (blank lines from `ruff format`). No assertion, expected value, or aggregation logic was changed; verify with `git diff 559073d..HEAD -- backend/tests/`.

### The pipeline (`.github/workflows/ci.yml`)

Runs on push to `main` and on every pull request. Workflow-level: `permissions: contents: read` (least privilege; the token can't write anything), and a concurrency group that cancels superseded runs on the same ref so force-pushes don't stack builds. Python jobs cache pip against `requirements-dev.txt`; the Node job caches npm against the lockfile. Seven jobs:

| Job | What it runs | What fails it |
|---|---|---|
| `backend-lint` | `ruff check` (incl. bandit security rules, GitHub annotation output) + `ruff format --check` | any lint or formatting drift |
| `backend-test` | `pytest -v` on Python 3.12 | any test failure |
| `frontend` | `npm ci` → ESLint (React + hooks rules) → `npm audit` twice → `vite build` | audit policy below; build must succeed |
| `backend-dep-audit` | `pip-audit` against `requirements.txt` | any known CVE in backend deps |
| `dockerfile-lint` | hadolint on both Dockerfiles | any rule violation |
| `image-scan` | builds both images, Trivy scans each (CRITICAL/HIGH, `ignore-unfixed`, exit-code 1), action pinned to `v0.36.0`, runs only after `backend-test` and `frontend` pass | any fixable CRITICAL/HIGH in either image |
| `repo-scan` | Trivy filesystem scan, misconfig + secret scanners | any CRITICAL/HIGH misconfig or a committed secret |

The npm audit policy is two-tier on purpose: `--audit-level=high` across everything including dev tooling, then `--omit=dev --audit-level=low`, which means zero tolerance for anything that ships to the browser. The image scan uses `ignore-unfixed` so the gate only fails on CVEs that actually have a patch, which keeps it strict without being noisy.

The pipeline also got its first maintenance during the review itself: GitHub deprecated the Node 20 action runtime mid-review, so `checkout`, `setup-node` and `setup-python` are bumped to their v6 majors (Node 24) and confirmed green. The hadolint and Trivy actions are Docker/composite based and aren't affected.

### What it caught on the first run

| Source | Finding | Resolution |
|---|---|---|
| ruff | unused import, deprecated `Optional[X]`, unsorted imports, long lines | fixed |
| ESLint | dead `total` prop in `ServiceTable` | removed |
| pip-audit | 4 CVEs in the bundled pip itself | the job upgrades pip before auditing |
| npm audit | esbuild dev-server advisory in Vite 5 | upgraded to Vite 7 instead of suppressing; audit is now clean at every severity |
| Trivy (image) | missing explicit `USER` in the frontend image (DS-0002), plus a live OpenSSL CVE (CVE-2026-45447) in the nginx base image | explicit `USER nginx` + an `apk upgrade` layer; rescan clean |

That last row is the whole argument for having the pipeline: first real run, one misconfiguration and one live CVE in a base image that looked fine. Both fixed in a follow-up commit, then green.

### Containers

- Backend (`python:3.12-slim`): a dedicated `appuser` (uid 10001), `USER` set before runtime. The healthcheck probes `/health` with stdlib urllib every 30s, so the image doesn't need curl just for that.
- Frontend: multi-stage. `node:22-alpine` builder runs `npm ci` against the committed lockfile, so the image is reproducible. Runtime is `nginx-unprivileged:alpine` (nginx as uid 101 on port 8080, never root) with one `apk upgrade` layer to pick up OS patches the base image hasn't rebuilt with yet.
- Compose publishes 3000 → 8080 so nothing changes for the user, and the frontend uses `depends_on: condition: service_healthy`, so it waits for a healthy backend rather than just a started container.
- `.dockerignore` in both build contexts; tests and tooling no longer ship inside runtime images.

## 8. Roadmap for what's left

In the order I'd do it. The aggregation math itself is correct. Leave it alone.

1. Enforce model invariants (closes F2). `Literal` types for category and environment, `Field(ge=0)` on cost. Bad data should fail at load, not show up wrong in a chart.
2. Fix the empty-dataset 500 (closes F1). Guard the `max()` calls, decide what an empty response looks like, and add the empty/single-resource tests the docstring already promises.
3. Make the swap point real (closes F8, makes 1 and 2 properly testable). A `CostSource` protocol with one `get_resources()` method, a `JsonFileSource` implementation, injected via FastAPI `Depends`. One change, three payoffs: tests get fixture injection, the four-reads-per-request goes away, and the boto3 swap becomes an implementation instead of a promise.
4. Group services by name (closes F6), attributing each service's dominant category by spend, so the breakdown survives a service that spans categories.
5. Move money to `Decimal` at the model boundary (closes F7).
6. Add a `month` field and a `?month=` query param. Month-over-month is the single most useful real FinOps capability this tool is missing.

## 9. Appendix: the commands I used

Backend:

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v                       # 33 passed
ruff check . && ruff format --check .
pip-audit
```

API (server on :8000):

```bash
curl http://localhost:8000/api/summary
curl http://localhost:8000/api/costs/by-category
curl http://localhost:8000/api/costs/by-service
curl http://localhost:8000/api/costs/by-environment
curl "http://localhost:8000/api/resources?category=COMPUTE"   # case-insensitive
curl "http://localhost:8000/api/resources?category=bogus"     # empty list, no error
curl -X POST http://localhost:8000/api/summary                # 405
curl http://localhost:8000/api/insights
```

Edge-case probes (run against the modules directly):

```python
# F1
aggregator._load_resources = lambda: []
aggregator.get_summary()   # ValueError: max() iterable argument is empty

# F2
Resource(resource_id="x", name="x", service="EC2",
         category="not-a-category", environment="prod-typo",
         monthly_cost=-50.0, region="us-east-1")   # accepted
```

Frontend:

```bash
cd frontend
npm ci
npm run lint                    # clean
npm audit --audit-level=low     # 0 vulnerabilities
npm run build                   # ok
```
