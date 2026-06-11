-- analytics/dbt/models/staging/stg_pull_requests.sql

with source as (
    select * from {{ source('public', 'pull_requests') }}
)
select
    id                                      as pr_id,
    repository_id,
    github_pr_number,
    title,
    state,
    author_login,
    is_merged,
    additions,
    deletions,
    changed_files,
    comments_count,
    review_comments_count,
    commits_count,
    time_to_merge_hours,
    github_created_at,
    github_closed_at,
    github_merged_at,
    date(github_created_at)                 as created_date,
    date(github_merged_at)                  as merged_date,
    created_at                              as record_created_at
from source
where github_created_at is not null