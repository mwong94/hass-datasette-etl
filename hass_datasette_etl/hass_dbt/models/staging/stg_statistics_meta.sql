select
    toUInt32(m.id) as id
    , toString(m.statistic_id) as entity_id
    , toString(m.source) as recorder
    , toString(m.unit_of_measurement) as uom
    , toBool(m.has_sum) as has_sum
    , toUInt8(m.mean_type) as has_mean
    , toDateTime64(m.loaded_at, 3) as loaded_at_utc
    , toTimezone(loaded_at_utc, 'America/Los_Angeles') as loaded_at_local

from {{ source('raw', 'statistics_meta') }} as m