select
    *

from {{ ref('stg_statistics') }} as s

qualify row_number() over(partition by id order by loaded_at desc) = 1