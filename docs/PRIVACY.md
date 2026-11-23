# Echo Web Admin Privacy Policy

This policy covers the "Echo Web Admin" Discord application, a login
gate for the administrative website of the Echo Discord bots. The panel
is operated by the maintainers of the bot instance you log into, usually
the staff of that Discord server.

## What the login gives us

The login uses only the `identify` OAuth scope. Discord hands us your
Discord user ID and your display name. Nothing else. We do not request
email, connections, guild lists or any other scope.

## Information from the bot itself

Beyond the login, the panel reads what the bot already knows from being
a member of your server: server names, member IDs, roles and the feature
data the bot stores (settings and content that you or others configured
through Discord or the panel). This is what the pages are rendered from
and what access decisions are based on. Nothing new is fetched about you
from anywhere else.

## Where things are stored

All data below lives on the machine the bot runs on, in plain files, and
nowhere else:

* **Session cookie**: a cookie in your browser that holds only a random
  session id. It is cryptographically signed, The actual session
  (your user ID, display name and a form token) is kept in the bot's memory 
  on the server. It expires after 7 days, when you log out
  (logging out also revokes a cookie stolen before it), or when the bot
  restarts, in which case you simply log in again.
* **Audit log** (`logs/web_admin.log`): every login, logout and admin
  action is recorded here with the timestamp, your user ID, your display
  name at the time and details of the change.
* **Granted users** (`data/web_admin.json`): per server lists of user
  IDs that a server admin explicitly granted panel access to.
* **Panel content**: anything configured through the panel is stored in
  the bot's data files and displayed in Discord by the bot itself.

## What we never do

* No analytics, ads or tracking of any kind.
* No third parties, no data selling, no profiling.
* No cloud services; there is no external server involved.

## Access and retention

Panel pages are only served to logged-in users who have admin or
granted access to that server. Audit entries and configuration data are
kept locally for as long as the operators run the bot. Session data
lives in your browser until it expires or you clear it.

Your Discord account itself remains subject to Discord's own privacy
policy; we have no control over it and never act on its behalf.

## Contact

For data questions, contact the staff of the Discord server whose bot
instance you use, or open an issue in the Echo repository.
