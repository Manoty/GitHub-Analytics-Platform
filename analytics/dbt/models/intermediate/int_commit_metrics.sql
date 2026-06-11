-- analytics/dbt/models/intermediate/int_commit_metrics.sql

with commits as (
    select * from {{ ref('stg_commits') }}
),
daily_agg as (
    select
        repository_id,
        commit_date,
        count(*)                            as daily_commits,
        count(distinct author_github_login) as daily_authors,
        sum(additions)                      as daily_additions,
        sum(deletions)                      as daily_deletions,
        sum(total_changes)                  as daily_changes
    from commits
    group by repository_id, commit_date
)
select
    repository_id,
    commit_date,
    daily_commits,
    daily_authors,
    daily_additions,
    daily_deletions,
    daily_changes,
    sum(daily_commits) over (
        partition by repository_id
        order by commit_date
        rows between 29 preceding and current row
    )                                       as rolling_30d_commits
from daily_agg