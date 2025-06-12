-- ──────────────────────────────────────────────────────────────────────
-- clickhouse syntax for creating tables in hass database
-- ──────────────────────────────────────────────────────────────────────
create database if not exists raw;

------------------------------------------------------------------------
-- statistics table
------------------------------------------------------------------------
create or replace table raw.statistics
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
) engine = MergeTree()
primary key (metadata_id, start_ts)
comment 'home-assistant aggregated sensor statistics';

-- (optional) sorting can help for date-range queries
-- order by (start_ts);

------------------------------------------------------------------------
-- statistics_meta table
------------------------------------------------------------------------
create or replace table raw.statistics_meta
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
) engine = MergeTree()
primary key (id)
comment 'metadata describing every statistic_id present in home-assistant';
