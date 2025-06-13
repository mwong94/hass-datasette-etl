/* ---------- 0.  (OPTIONAL) run everything ON CLUSTER ---------- */
/* If you run a multi-node cluster managed by ON CLUSTER,         */
/* uncomment ‘ON CLUSTER <cluster>’ in every DDL.                 */
/*  -- ON CLUSTER 'my_cluster'                                    */

/* ---------- 1.  Hardened settings profile (read-only) ---------- */
CREATE SETTINGS PROFILE IF NOT EXISTS readonly_profile
    SETTINGS
        readonly = 1         -- disallows all data-modification queries
        , max_threads = 2;   -- example safety limit
-- GRANT -- settings profile is just a container, no GRANT needed

/* ---------- 2.  Role with read-only privileges ---------------- */
CREATE ROLE IF NOT EXISTS role_read_raw_hass;      -- 1 role  →  many users

/* Current and FUTURE tables are covered by db.* wildcards.     */
/* SELECT automatically implies SHOW privilege on those objects. */
GRANT SELECT ON raw.*  TO role_read_raw_hass;      --  [oai_citation:0‡clickhouse.com](https://clickhouse.com/docs/sql-reference/statements/create/role?utm_source=chatgpt.com)
GRANT SELECT ON hass.* TO role_read_raw_hass;      --  [oai_citation:1‡clickhouse.com](https://clickhouse.com/docs/sql-reference/statements/create/role?utm_source=chatgpt.com)

/* Optional: allow the role to list all DBs (handy for BI tools) */
GRANT SHOW DATABASES ON *.* TO role_read_raw_hass; --  [oai_citation:2‡clickhouse.com](https://clickhouse.com/docs/sql-reference/statements/grant?utm_source=chatgpt.com)

/* ---------- 3.  User definition -------------------------------- */
CREATE USER IF NOT EXISTS hex
    IDENTIFIED WITH sha256_hash BY '2b784a6c7cb888b10e02c553bd2ac7e87743a65912c2543efa1472542bdf93b6'  -- change me!
    DEFAULT ROLE role_read_raw_hass                                -- auto-applied at login  [oai_citation:3‡clickhouse.com](https://clickhouse.com/docs/en/sql-reference/statements/create/role)
    SETTINGS PROFILE 'readonly_profile'
    /* Optional network hardening — only allow trusted hosts   */
    HOST IP '3.129.36.245',
         IP '3.13.16.99',
         IP '3.18.79.139',
         IP '192.168.1.0/24',
         IP '192.168.2.0/24',
         IP '192.168.3.0/24';

/* ---------- 4.  Tie everything together ----------------------- */
GRANT role_read_raw_hass TO hex;   -- assigns role (already defaulted)

/* ---------- 5.  (Optional) check what the user really got ----- */
SHOW GRANTS FOR hex;

/* ---------- 6.  If you later add more read-only DBs ----------- */
/* just:   GRANT SELECT ON newdb.* TO role_read_raw_hass;         */