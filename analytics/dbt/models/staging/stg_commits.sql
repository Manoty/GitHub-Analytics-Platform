-- analytics/dbt/models/staging/stg_commits.sql

with source as (
    select * from {{ source('public', 'commits') }}
)
select
    id                                      as commit_id,
    repository_id,
    sha,
    message,
    author_name,
    author_email,
    author_github_login,
    committed_at,
    date(committed_at)                      as commit_date,
    extract(dow from committed_at)          as day_of_week,
    extract(hour from committed_at)         as hour_of_day,
    additions,
    deletions,
    files_changed,
    additions + deletions                   as total_changes,
    created_at                              as record_created_at
from source
where committed_at is not null