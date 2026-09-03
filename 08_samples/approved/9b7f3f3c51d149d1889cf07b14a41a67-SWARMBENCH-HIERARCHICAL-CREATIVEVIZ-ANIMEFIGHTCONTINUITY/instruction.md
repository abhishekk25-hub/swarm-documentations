A film archivist recovered a pile of short **eyewitness recaps** of a single anime fight between
**AKIRA** (blue) and **RYU-X** (red) - fans, analysts, and live-tweeters each describing moments
they saw, in their own words. They're at `/input_artifacts/recaps.jsonl` (one JSON object per line:
`{"id","act","text"}`). I need you to rebuild the fight from them and render it.

The same striking moment of the fight was written up by *many* different people, so **many recaps
describe the exact same moment using completely different wording**. Mixed in are lots of **one-off
moments** that only a single person mentioned (a stray throw, an improvised grab) - those are not part
of the main choreography. The `act` field tells you which phase of the fight a recap belongs to;
recaps from different acts are never the same moment.

Step 1 - Cluster the recaps
Group the recaps so that **all recaps describing the same fight moment land in the same group.** Read
the full `text` - same-moment recaps often share almost no vocabulary (one calls it "a leaping
uppercut under the chin", another "the blue fighter launched skyward and caught his jaw"), while
different moments can sound deceptively similar. A recap that stands alone (its moment was described
by no one else) is its own group of one.

Step 2 - Reconstruct the fight
The moments that **several people independently described** are the canonical **beats** of the fight;
the one-off moments are not. Work out the **order** of the beats from the momentum and position cues
in the recaps (who is winning, who is being worn down, who is pushed toward an edge, and whether a
moment reads as early, middle, or late in the bout). Produce the ordered list of beats.

Step 3 - Render the fight with the provided toolkit
A render toolkit is provided at `/input_artifacts/fightkit.py` that draws the articulated fighters,
motion, hit FX, HP/combo/timer HUD, and stitches the final video for you. Turn each reconstructed
beat into a small spec and call it:
```python
import sys; sys.path.insert(0, "/input_artifacts")
from fightkit import render_fight
render_fight(beats, "/logs/agent/final.mp4", "/logs/agent/shots")
```
where `beats` is your reconstructed fight, in order - one dict per beat:
```
{"attacker": "A"|"B", # A = AKIRA (blue), B = RYU-X (red)
 "move": "uppercut"|"straight"|"hook"|"elbow"|"palm"|"kick"|"knee"|"sweep",
 "callout": "<the move's name as the recaps describe it>",
 "hp_a": <0-1000>, "hp_b": <0-1000>, "combo": <int>, "timer": <int>, "duration": 3.0}
```
Read each beat-cluster's recaps to decide the `attacker`, the closest `move`, and a `callout`, and
derive a sensible HP/combo/timer progression across the fight. The toolkit produces one clean shot
per beat plus the stitched `final.mp4`.

Deliver (exact paths)
- `/logs/agent/output.json`:
  ```
  {"assignments": [ {"id":"r0007","group":"g1"}, ... every recap id exactly once ... ],
 "beats": [ {"group":"g1","attacker":"A","move":"uppercut","callout":"RISING DRAGON"}, ...
 the beat-groups in fight order, each with its spec ... ]}
  ```
- `/logs/agent/shots/<NN>.mp4` + `/logs/agent/final.mp4` - produced by `render_fight`.
- `/logs/agent/manifest.json` - one record per shot: `{order, group, clip}`.

Whatever you finish, always write `output.json` and call `render_fight` on the beats you reconstructed;
partial work still counts.
