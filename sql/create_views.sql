{#create or replace view hass.v_statistics as#}
       select
           toInt8(id) as id

       from raw.statistics;