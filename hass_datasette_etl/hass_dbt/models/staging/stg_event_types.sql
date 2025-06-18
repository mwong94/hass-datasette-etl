select
    toUInt32(et.event_type_id) as id
    , toString(et.event_type) as event_type
    , et.loaded_at

from {{ source('raw', 'event_types') }} as et

final