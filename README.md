# ESPN Fantasy Basketball Automation

## Environment setup

Run `bash scripts/setup.sh` from the repository root. It uses the workspace's
preinstalled [uv](https://docs.astral.sh/uv/) to install Python 3.12, create
`.venv`, and install the pinned dependencies from `requirements.txt`.
The script is safe to rerun.

For automatic setup on each fresh workspace start, set the workspace's saved
setup command to:

```bash
bash /workspace/espn-fantasy-basketball-automation/scripts/setup.sh
```

Use `.venv/bin/python`, or run `source .venv/bin/activate` in each new shell.
The client is [espn-api](https://github.com/cwendt94/espn-api), which supports
ESPN fantasy basketball and private-league authentication:

```python
import json
import os
from espn_api.basketball import League

with open("espn.config.json") as config_file:
    config = json.load(config_file)

league = League(
    league_id=config["leagueId"],
    year=config["seasonId"],
    espn_s2=os.environ["ESPN_S2"],
    swid=os.environ["SWID"],
)
team = next(team for team in league.teams if team.team_id == config["teamId"])
print(team.team_name)
```

## Team configuration

Use `espn.config.json` as the source of truth for future ESPN requests:

- `leagueId`: 1779277586 (Dubs on Dubs on Dubs LEAGUE)
- `teamId`: 3 (Kwaz's Kwazy Team)
- `seasonId`: 2027

Keep the season fixed at the configured value unless explicitly asked to change it.
Read authentication cookies from the `ESPN_S2` and `SWID` environment variables;
never store their values in the repository.
