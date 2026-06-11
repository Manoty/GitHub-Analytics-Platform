-- analytics/dbt/models/staging/stg_issues.sql

with source as (
    select * from {{ source('public', 'issues') }}
)
select
    id                                      as issue_id,
    repository_id,
    github_issue_number,
    title,
    state,
    author_login,
    labels,
    comments_count,
    time_to_close_hours,
    github_created_at,
    github_closed_at,
    date(github_created_at)                 as created_date,
    date(github_closed_at)                  as closed_date,
    created_at                              as record_created_at
from source
where github_created_at is not null