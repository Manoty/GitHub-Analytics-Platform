-- analytics/dbt/models/marts/fact_commit_daily.sql

select
    {{ generate_surrogate_key(['repository_id', 'commit_date::varchar']) }}
                                            as fact_key,
    repository_id,
    commit_date,
    daily_commits,
    daily_authors,
    daily_additions,
    daily_deletions,
    daily_changes,
    rolling_30d_commits
from {{ ref('int_commit_metrics') }}