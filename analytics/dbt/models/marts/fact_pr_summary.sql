-- analytics/dbt/models/marts/fact_pr_summary.sql

select
    {{ generate_surrogate_key(['repository_id', 'week_start::varchar']) }}
                                            as fact_key,
    repository_id,
    week_start,
    prs_opened,
    prs_merged,
    prs_closed,
    avg_merge_hours,
    median_merge_hours
from {{ ref('int_pr_metrics') }}