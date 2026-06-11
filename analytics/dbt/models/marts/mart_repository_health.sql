-- analytics/dbt/models/marts/mart_repository_health.sql

with health as (
    select * from {{ source('public', 'repository_health') }}
),
repos as (
    select * from {{ ref('dim_repositories') }}
)
select
    h.id                                    as health_id,
    h.repository_id,
    r.full_name,
    r.primary_language,
    r.stars_count,
    h.health_score,
    h.health_grade,
    h.commit_frequency_score,
    h.pr_merge_speed_score,
    h.issue_resolution_score,
    h.contributor_diversity_score,
    h.commits_last_30_days,
    h.avg_pr_merge_hours,
    h.avg_issue_close_hours,
    h.active_contributors_last_30_days,
    h.total_contributors,
    h.calculated_at
from health h
inner join repos r on h.repository_id = r.repository_id