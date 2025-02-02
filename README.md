# Echo Discord bot collection

The Echo project is a collection of discord bots that share code and run on the same machine. Most bots are designed 
specifically for a server.  

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

## Important links

The Pivotal tracker project link containing all the plans for the codebase
<https://www.pivotaltracker.com/n/projects/2462509>

## Change Log

### 4.2.1 / Cleanup & minor improvements, strucuting & documenting of sunreek

* Improve consistency, python style-guide adherance, ...
* Increase runtime safety.
* Improve in-code documention.
* Slight Structure changes for reduced mental overhead.

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
