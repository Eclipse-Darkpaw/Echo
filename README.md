# Echo Discord bot collection

The Echo project is a collection of discord bots that share code and run on
the same machine. Most bots are designed specifically for a server.  

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

`requirements.txt` mirrors the `dependencies` in `pyproject.toml`: whenever
you change one, update the other to match. Copy `.env.example` to `.env`
and fill in the guardian user IDs and the `<BOTNAME>_TOKEN` /
`<BOTNAME>_PREFIX` values of the bots you want to run.

Also fetch the used spaCy models :

```bash
.venv/bin/python -m spacy download en_core_web_md
.venv/bin/python -m spacy download xx_sent_ud_sm
```

## Running

```bash
.venv/bin/python sunreek.py
```

Optional flags:

* `--test-bot` — use the `*_TEST_TOKEN` / `*_TEST_PREFIX` variables instead
* `--no-notif` — skip the startup DM to the guardians

## Repo modifications

If you modify any functions or method, please document in the following format

```python
"""
Description
Last docstring edit: -name Vx.x.x
Last method edit: -name Vx.x.x
:param:
:return:
"""
```

as well as adding all changes to the change log below

## Change Log

### 5.0.1 / Startup guard, packaging & dependency updates

* Guard startup notifications so reconnecting bots do not DM guardians repeatedly.
* Migrate packaging from Poetry to PEP 621/`setuptools` metadata (Python 3.14+, maintainer info) and replace the poetry-exported `requirements.txt` with a minimal, hand-maintained one for plain pip installs.
* Pin `pydantic<2.12` in `pyproject.toml` (spaCy model loading is broken on pydantic 2.12 and newer).
* Enable the Artfight cog in Sunreek.
* Remove the outdated Pivotal Tracker link from the README.
* Document environment setup in the README.
* Update dependencies: `aiohttp`, `idna`, `urllib3`, `pygments` and `requests`.

### 5.0.0 / Woof, Truth or Dare & semantic matching

* Add `woof.py` bot running the truth-or-dare module, with a 'do you remember' easter egg.
* Add truth-or-dare module and repository: random `/dare`, add/remove dares with a confirmation view, periodic queue cleanup and ephemeral deferral for slash usage.
* Add spaCy-based semantic similarity checks with tuned per-language thresholds.

### 4.5.0 / Purge tooling & Artfight refinements

* Add purge module for listing inactive members and managing survivors.
* Add a `survive` button UI for members to opt out of purges.
* Add a progress-tracker utility for long-running operations.
* Add Artfight `list_players` command and expand the Hall of Fame leaderboards.
* Improve Artfight submissions: early cancel, prompt-less entries, dropdown navigation, multi-user support and victim pings.
* Fix Artfight prompt-day calculation, background bonus scoring and friendly-fire mentions.

### 4.4.0 / Ban management & Artfight UI

* Add ban import/export commands for moderators.
* Rebuild the Artfight UI with configuration, join button, daily messages/status, member sync and submission flows.
* Fix unhandled forbidden errors when DMing users and crashes on unknown guardians.

### 4.3.0 / Refactoring, Fancy Logging & File Watching/Observing

* Refactor Structure
* Add Fancy (& file) logging support
* Add non-breaking, optimised & threaded file watching support
* Improve consistency, python style-guide adherance, ...
* Increase runtime safety.
* Improve in-code documention.

### 4.2.0

* Misc QoL features & improvement
* Sunreek, invite watching _(when using discord pause)_
* Env vars usage improvements
* Minor phrassing changes

### 4.1.0 / Artfight update

* Updated the artfight code to use slash commands.
* Misc QoL features & imrpovements
* Team balancing mechanism

### 4.0.0 / Slash command update

* Added slash command support.
* Minor UI modications

### 3.5.2

* removed `fuck` command from bots
* removed profiles from `global_files.json`
* grammar formatting changes

### 3.5.0

* Restructured files and moved the heirarchy

### V3.4.1

* Attempted to fix bug in `Verification.py` that would cause applications to be dropped

### V3.0.0

* began overhaul
* added error logging
* added server setup
* fixed verification
* reduced duplicate code in the files

### V2.0.2/Anti-scam V2.1.0

Author - Autumn\
Branch - anti-scam/feature/verification

* Added `>verify` feature to `anti-scam.py`

### V2.0.1/Refbot V2.1.0

Author - Autumn

* Reformatted `refbot.py`
* Removed ununsed methods from

### V2.0.0

Author - Autumn

* Updated README
* Updated version_num in `anti-scam.py`, `echo.py`, `main.py`, `gardenbot.py`, `refbot.py`, and `sunreek.py`
