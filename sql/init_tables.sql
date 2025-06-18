-- ──────────────────────────────────────────────────────────────────────
-- clickhouse syntax for creating tables in hass database
-- ──────────────────────────────────────────────────────────────────────
create database if not exists raw;

------------------------------------------------------------------------
-- statistics table
------------------------------------------------------------------------
create table if not exists raw.statistics
(
    id                 String,
    created            String,
    created_ts         String not null,
    metadata_id        String not null,
    start              String,
    start_ts           String not null,
    mean               String,
    min                String,
    max                String,
    last_reset         String,
    last_reset_ts      String,
    state              String,
    sum                String,
    mean_weight        String,
    loaded_at          Double
) engine = ReplacingMergeTree(loaded_at)
primary key (id)
order by (id)
comment 'home-assistant aggregated sensor statistics';

-- (optional) sorting can help for date-range queries
-- order by (start_ts);

------------------------------------------------------------------------
-- statistics_meta table
------------------------------------------------------------------------
create table if not exists raw.statistics_meta
(
    id                  String,              -- surrogate key
    statistic_id        String not null,     -- original ha statistic_id
    source              String,              -- e.g. 'recorder'
    unit_of_measurement String,
    has_mean            String,              -- true/false as text
    has_sum             String,              -- true/false as text
    name                String,
    mean_type           String,
    loaded_at           Double
) engine = ReplacingMergeTree(loaded_at)
primary key (id)
order by (id)
comment 'metadata describing every statistic_id present in home-assistant';

------------------------------------------------------------------------
-- events table
------------------------------------------------------------------------
create table if not exists raw.events
(
    event_id             String,
    event_type           String,
    event_data           String,
    origin               String,
    origin_idx           String,
    time_fired           String,
    time_fired_ts        String,
    context_id           String,
    context_user_id      String,
    context_parent_id    String,
    data_id              String,
    context_id_bin       String,
    context_user_id_bin  String,
    context_parent_id_bin String,
    event_type_id        String,
    loaded_at            Double
) engine = ReplacingMergeTree(loaded_at)
primary key (event_id)
order by (event_id)
comment 'every event fired in home-assistant';

------------------------------------------------------------------------
-- event_data table
------------------------------------------------------------------------
create table if not exists raw.event_data
(
    data_id     String not null,
    hash        String,
    shared_data String,
    loaded_at   Double
) engine = ReplacingMergeTree(loaded_at)
primary key (data_id)
order by (data_id)
comment 'event data shared payloads';

------------------------------------------------------------------------
-- event_types table
------------------------------------------------------------------------
create table if not exists raw.event_types  (
    event_type_id   String not null,
    event_type      String,
    loaded_at       Double
) engine = ReplacingMergeTree(loaded_at)
primary key (event_type_id)
order by (event_type_id)
comment 'event types';
