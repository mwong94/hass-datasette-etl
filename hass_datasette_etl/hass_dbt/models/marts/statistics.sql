select
    *

from {{ ref('stg_statistics') }} as s

qualify row_number() over(partition by id order by loaded_ts desc) = 1