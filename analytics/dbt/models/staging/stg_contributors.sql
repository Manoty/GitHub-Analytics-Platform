-- analytics/dbt/models/staging/stg_contributors.sql

with source as (
    select * from {{ source('public', 'contributors') }}
)
select
    id                                      as contributor_id,
    repository_id,
    github_login,
    avatar_url,
    contributions_count,
    commits_count,
    pull_requests_count,
    issues_count,
    additions,
    deletions,
    first_contribution_at,
    last_contribution_at,
    activity_score,
    created_at                              as record_created_at
from source