-- analytics/dbt/models/marts/dim_contributors.sql

select
    {{ generate_surrogate_key(['repository_id', 'github_login']) }}
                                            as contributor_key,
    repository_id,
    github_login,
    commit_count,
    pr_count,
    merged_pr_count,
    issue_count,
    total_additions,
    total_deletions,
    first_commit_at,
    last_commit_at
from {{ ref('int_contributor_metrics') }}