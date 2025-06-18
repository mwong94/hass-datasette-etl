select
    toUInt32(e.event_id) as id
    , toUInt8OrNull(e.origin_idx) as origin_idx
    , toDateTime64(time_fired_ts, 3) as time_fired_at_utc
    , toTimezone(time_fired_at_utc, 'America/Los_Angeles') as time_fired_at_local
    , toUInt32OrNull(trim(simpleJSONExtractRaw(e.data_id, 'value'))) as data_id
    , toUInt32OrNull(trim(simpleJSONExtractRaw(e.event_type_id, 'value'))) as event_type_id
    , e.loaded_at

from {{ source('raw', 'events') }} as e

final