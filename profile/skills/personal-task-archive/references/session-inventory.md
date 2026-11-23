# Product inventory and runtime evidence

Use native list_threads history pagination for the selected host and archive
state. For explicitly requested complete inventories, follow nextCursor to
exhaustion; otherwise state the range actually reviewed. Recent lists and pinned
lists can complement an inventory but are not proof of complete coverage.

Use read_thread for the latest substantive outcome and ownership. Use a compact
wait_threads snapshot when execution status remains relevant and unclear.
notLoaded from an independent app-server does not establish that another
instance has stopped execution. Missing pin, unread, Goal, or automation fields
remain unknown; do not invent their values or repeatedly rediscover the same gap.

Keep host identity and exact task ID together. Connected remote hosts can be
handled through native tools when the user selects them; do not transfer private
history files or inspect auth/session stores. Do not start a second app-server or
scan raw rollouts merely to produce exhaustive statistics for routine archival.

A missing record is a lookup limitation, not a target for blind mutation. After
archiving, verify the exact target with the native product surface. Do not read
all excluded chats again just to demonstrate that they were left untouched.
