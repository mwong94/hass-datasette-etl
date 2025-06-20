select
    e.time_fired_at_local as event_time

    , et.event_type

    , ed.domain
    , ed.service
    , ed.service_data
    , ed.entity_id
    , ed.shared_data

    , e.id as event_id
    , e.data_id as event_data_id
    , e.event_type_id

from {{ ref('stg_events') }} as e

left outer join {{ ref('stg_event_data') }} as ed
on e.data_id = ed.id

left outer join {{ ref('stg_event_types') }} as et
on e.event_type_id = et.id