-- analytics/dbt/models/marts/fact_issue_summary.sql

select
    {{ generate_surrogate_key(['repository_id', 'week_start::varchar']) }}
                                            as fact_key,
    repository_id,
    week_start,
    issues_opened,
    issues_closed,
    avg_close_hours,
    median_close_hours
from {{ ref('int_issue_metrics') }}