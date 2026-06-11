-- analytics/dbt/models/intermediate/int_issue_metrics.sql

with issues as (
    select * from {{ ref('stg_issues') }}
)
select
    repository_id,
    date_trunc('week', github_created_at)   as week_start,
    count(*)                                as issues_opened,
    count(*) filter (where state = 'closed') as issues_closed,
    avg(time_to_close_hours) filter (
        where state = 'closed'
    )                                       as avg_close_hours,
    percentile_cont(0.5) within group (
        order by time_to_close_hours
    ) filter (where state = 'closed')       as median_close_hours
from issues
group by repository_id, date_trunc('week', github_created_at)