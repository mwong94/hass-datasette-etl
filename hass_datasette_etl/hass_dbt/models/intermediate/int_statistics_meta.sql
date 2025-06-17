select
    *

from {{ ref('stg_statistics_meta') }} as m

qualify row_number() over(partition by id order by loaded_at desc) = 1