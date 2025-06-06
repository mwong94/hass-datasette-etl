-- ──────────────────────────────────────────────────────────────────────
-- Change these to the correct database and schema before running
-- ──────────────────────────────────────────────────────────────────────
USE DATABASE HASS;
USE SCHEMA   RAW;

------------------------------------------------------------------------
-- STATISTICS  (raw.statistics)
------------------------------------------------------------------------
CREATE OR REPLACE TABLE STATISTICS
(
    ID                 TEXT,
    CREATED            TEXT,
    CREATED_TS         TEXT    NOT NULL,
    METADATA_ID        TEXT    NOT NULL,
    "START"            TEXT,
    START_TS           TEXT    NOT NULL,
    MEAN               TEXT,
    MIN                TEXT,
    MAX                TEXT,
    LAST_RESET         TEXT,
    LAST_RESET_TS      TEXT,
    STATE              TEXT,
    SUM                TEXT,
    MEAN_WEIGHT        TEXT,
    LOADED_AT          TIMESTAMP,

    CONSTRAINT PK_STATISTICS PRIMARY KEY (METADATA_ID, START_TS)
)
COMMENT = 'Home-Assistant aggregated sensor statistics';

-- (optional) clustering can help for date-range queries
-- ALTER TABLE STATISTICS CLUSTER BY (START_TS);

------------------------------------------------------------------------
-- STATISTICS_META  (raw.statistics_meta)
------------------------------------------------------------------------
CREATE OR REPLACE TABLE STATISTICS_META
(
    ID                  TEXT,              -- surrogate key
    STATISTIC_ID        TEXT    NOT NULL,  -- original HA statistic_id
    SOURCE              TEXT,              -- e.g. 'recorder'
    UNIT_OF_MEASUREMENT TEXT,
    HAS_MEAN            TEXT,              -- TRUE/FALSE as text
    HAS_SUM             TEXT,              -- TRUE/FALSE as text
    NAME                TEXT,
    MEAN_TYPE           TEXT,
    LOADED_AT          TIMESTAMP,

    CONSTRAINT PK_STATISTICS_META PRIMARY KEY (ID)
)
COMMENT = 'Metadata describing every statistic_id present in Home-Assistant';