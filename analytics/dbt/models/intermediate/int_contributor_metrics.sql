-- analytics/dbt/models/intermediate/int_contributor_metrics.sql

with commits as (
    select * from {{ ref('stg_commits') }}
),
prs as (
    select * from {{ ref('stg_pull_requests') }}
),
issues as (
    select * from {{ ref('stg_issues') }}
),
commit_stats as (
    select
        repository_id,
        author_github_login     as github_login,
        count(*)                as commit_count,
        sum(additions)          as total_additions,
        sum(deletions)          as total_deletions,
        min(committed_at)       as first_commit_at,
        max(committed_at)       as last_commit_at
    from commits
    where author_github_login is not null
    group by repository_id, author_github_login
),
pr_stats as (
    select
        repository_id,
        author_login            as github_login,
        count(*)                as pr_count,
        count(*) filter (where is_merged) as merged_pr_count
    from prs
    where author_login is not null
    group by repository_id, author_login
),
issue_stats as (
    select
        repository_id,
        author_login            as github_login,
        count(*)                as issue_count
    from issues
    where author_login is not null
    group by repository_id, author_login
)
select
    c.repository_id,
    c.github_login,
    c.commit_count,
    c.total_additions,
    c.total_deletions,
    c.first_commit_at,
    c.last_commit_at,
    coalesce(p.pr_count, 0)         as pr_count,
    coalesce(p.merged_pr_count, 0)  as merged_pr_count,
    coalesce(i.issue_count, 0)      as issue_count
from commit_stats c
left join pr_stats p
    on c.repository_id = p.repository_id
    and c.github_login = p.github_login
left join issue_stats i
    on c.repository_id = i.repository_id
    and c.github_login = i.github_login