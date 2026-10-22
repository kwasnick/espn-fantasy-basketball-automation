# ESPN Fantasy Basketball Automation

## Team configuration

Use `espn.config.json` as the source of truth for future ESPN requests:

- `leagueId`: 1779277586 (Dubs on Dubs on Dubs LEAGUE)
- `teamId`: 3 (Kwaz's Kwazy Team)
- `seasonId`: 2027

Keep the season fixed at the configured value unless explicitly asked to change it.
Read authentication cookies from the `ESPN_S2` and `SWID` environment variables;
never store their values in the repository.
