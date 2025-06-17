select
    s.id
    , s.created_at_local as created_at
    , m.entity_id
    , m.uom
    , s.start_at_local as start_at
    , s.mean
    , s.min
    , s.max
    , s.sum
    , s.last_reset_at_local as last_reset_at
    , s.state

from {{ ref('int_statistics') }} as s

left outer join {{ ref('int_statistics_meta') }} as m
on s.metadata_id = m.id