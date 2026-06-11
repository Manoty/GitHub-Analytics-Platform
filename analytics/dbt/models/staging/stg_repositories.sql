-- analytics/dbt/models/staging/stg_repositories.sql

with source as (
    select * from {{ source('public', 'repositories') }}
)
select
    id                                      as repository_id,
    owner_id,
    github_id,
    full_name,
    name,
    description,
    language                                as primary_language,
    stars_count,
    forks_count,
    watchers_count,
    open_issues_count,
    size_kb,
    is_private,
    is_fork,
    is_archived,
    is_connected,
    sync_status,
    last_synced_at,
    github_created_at,
    github_updated_at,
    created_at                              as record_created_at
from source
where is_connected = true