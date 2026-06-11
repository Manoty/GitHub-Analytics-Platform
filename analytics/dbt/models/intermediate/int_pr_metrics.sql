-- analytics/dbt/models/intermediate/int_pr_metrics.sql

with prs as (
    select * from {{ ref('stg_pull_requests') }}
)
select
    repository_id,
    date_trunc('week', github_created_at)   as week_start,
    count(*)                                as prs_opened,
    count(*) filter (where is_merged)       as prs_merged,
    count(*) filter (where state = 'closed' and not is_merged) as prs_closed,
    avg(time_to_merge_hours) filter (where is_merged) as avg_merge_hours,
    percentile_cont(0.5) within group (
        order by time_to_merge_hours
    ) filter (where is_merged)              as median_merge_hours
from prs
group by repository_id, date_trunc('week', github_created_at)