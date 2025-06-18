select
    toUInt32(ed.data_id) as id
    , toString(ed.hash) as hash
    , toString(ed.shared_data) as shared_data
    , simpleJSONExtractString(shared_data, 'domain') as domain
    , simpleJSONExtractString(shared_data, 'service') as service
    , simpleJSONExtractRaw(shared_data, 'service_data') as service_data
    , simpleJSONExtractString(service_data, 'entity_id') as entity_id
    , ed.loaded_at

from {{ source('raw', 'event_data') }} as ed