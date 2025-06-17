select
    toUInt32(s.id) as id
    , toFloat64OrNull(s.created_ts) as created_ts
    , toDateTime64(created_ts, 3) as created_at_utc
    , toTimezone(created_at_utc, 'America/Los_Angeles') as created_at_local
    , toUInt32OrNull(trim(simpleJSONExtractRaw(s.metadata_id, 'value'))) as metadata_id
    , toFloat64OrNull(s.start_ts) as start_ts
    , toDateTime64(start_ts, 3) as start_at_utc
    , toTimezone(start_at_utc, 'America/Los_Angeles') as start_at_local
    , toFloat64OrNull(s.mean) as mean
    , toFloat64OrNull(s.min) as min
    , toFloat64OrNull(s.max) as max
    , toFloat64OrNull(s.last_reset_ts) as last_reset_ts
    , toDateTime64(last_reset_ts, 3) as last_reset_at_utc
    , toTimezone(last_reset_at_utc, 'America/Los_Angeles') as last_reset_at_local
    , toFloat64OrNull(s.state) as state
    , toFloat64OrNull(s.sum) as sum
    , toFloat64OrNull(s.loaded_at) as loaded_ts

from {{ source('raw', 'statistics') }} as s