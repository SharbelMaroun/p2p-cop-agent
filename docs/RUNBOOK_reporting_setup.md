# Runbook — Gmail reporting on a fresh machine (`M7-15d`)

Five steps, reproducible by a teammate with no prior context (`G§2.1`).

**Steps 1–3 are yours to run, not an agent's.** They create a real credential on a real
Google account. Nothing in this repository creates, reads or stores one, and no automated
process should be asked to: the consent screen is where a human decides what a program may do
with their mailbox. That is why `M7-15` and `M7-15a` are the only M7 rows left unclaimed.

Everything downstream of consent — the refresh policy, the message envelope, the send gates —
is built and tested against injected doubles, which is how the rest of M7 finished with no
credential in existence.

## 1. Create the OAuth client

In the Google Cloud console, on a project you own:

1. **APIs & Services → Enable APIs** → enable the **Gmail API**.
2. **OAuth consent screen** → External → add your own address as a **test user**. Test-user
   mode is enough; the app is never published.
3. **Credentials → Create credentials → OAuth client ID → Desktop app**.
4. Download the JSON and save it to the repository root as `credentials.json`.

Ask for exactly one scope:

```
https://www.googleapis.com/auth/gmail.send
```

Rule 30 (Mandatory) requires authorised sending only, with sanction "security breach that
will lead to code disqualification". `gmail.readonly` or `gmail.modify` would let the program
read the mailbox, and nothing here needs to. `REQUIRED_SCOPE` in
`reporting/gmail_message.py` pins it and a test asserts no read or modify scope appears.

## 2. Check the credential is ignored before it exists

Run this **before** step 3 writes anything:

```bash
git check-ignore -v credentials.json token.json
```

Both must print a matching `.gitignore` line. Rule 39 (Prohibited) forbids pushing secrets
"even if it is private and shared only with the lecturer"; rule 40 (Mandatory) requires them
gitignored.

If either file is already tracked, `git rm --cached` it **and rotate the credential in the
Google console**. A key that reached a commit is compromised even after the commit is
removed — the object stays in the history of every clone, which is what
`scripts/scan_git_history.py` exists to detect.

## 3. Run the consent flow once

**There is no `p2p-cop authorize` command, and that is deliberate** — see the note above.

```bash
uv add google-auth-oauthlib
uv run python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
scope = ['https://www.googleapis.com/auth/gmail.send']
creds = InstalledAppFlow.from_client_secrets_file('credentials.json', scope).run_local_server(port=0)
open('token.json','w').write(creds.to_json())
print('token written; refresh token present:', bool(creds.refresh_token))
"
```

A browser window asks you to approve the send-only scope. Approving writes `token.json`,
holding an access token (about an hour) and a **refresh token** (months). The refresh token is
what makes the rest of a series unattended, and the line above reports whether you got one
without printing it.

Without a refresh token, `ensure_fresh` refuses once the access token expires rather than
silently skipping a Mandatory report (`AE-32`) — and you would discover that at the end of a
series, which is the worst possible moment.

## 4. Confirm the gates before the first counted game

```bash
uv run ruff check .
uv run python -m pytest -q
uv run python scripts/check_file_lengths.py
uv run python scripts/check_secrets.py
uv run python scripts/scan_git_history.py
uv run python scripts/verify_clean_clone.py
```

`check_secrets.py` scans every text file; `scan_git_history.py` scans every blob ever
committed, because rule 39 forbids secrets being *in the repository* and a credential deleted
three commits ago is still in every clone.

If either flags something, **change the value** — use a recognised placeholder (`dummy-…`,
`${VAR}`, `<replace me>`). Do not allowlist. Nothing in this project has an allowlist entry,
and the one reviewed historical finding is pinned by blob SHA, which suppresses exactly the
bytes a human read and nothing else.

## 5. Rehearse before anything counts

```bash
uv run python -m pytest tests/integration/test_series_rehearsal.py -q
uv run python -m pytest tests/integration/test_replay_of_stored_match.py -q
```

The first plays a full series through the real builders, audit and settlement. The second
reloads a stored log **by path** and re-verifies it to `Verified OK` — rule 20's threshold
condition, and the source of the screenshot p.81/189 calls absolute mandatory.

---

## If something fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `there is no refresh token` | consent granted without offline access | delete `token.json`, re-run step 3 |
| `refreshing the access token failed` | the grant was revoked in the Google account | re-run step 3 |
| `refusing to compose a report for a settlement in state …` | the audit failed, or the opponent disagreed | do **not** send. Preserve the logs and raise it with the lecturer — sending would turn their rule 19 loss into a shared rule 35 loss |
| `refusing to reveal: the log summary carries no ended_at` | `reveal_log` called mid-game | reveal only after the game ends; rule 18 keeps nonces secret until then |
| `REFUSING TO SCAN: this is a shallow clone` | `--depth 1`, or CI without `fetch-depth: 0` | `git fetch --unshallow` |
| Secret scan flags a line | a value that looks live | change the value; do not allowlist |

Nothing above prints a token. If you need to debug one, note that `TokenState.__repr__`
redacts deliberately — the realistic leak is a token reaching a log through a repr or an
exception message, not through a deliberate print.
