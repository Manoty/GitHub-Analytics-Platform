-- analytics/dbt/models/marts/dim_repositories.sql

select
    repository_id,
    owner_id,
    github_id,
    full_name,
    name,
    primary_language,
    stars_count,
    forks_count,
    watchers_count,
    is_private,
    is_fork,
    is_archived,
    github_created_at,
    github_updated_at,
    record_created_at
from {{ ref('stg_repositories') }}