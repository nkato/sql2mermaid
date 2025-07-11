SELECT *
FROM (
  WITH test_cte_1 AS (
    SELECT id AS user_id
    FROM test_table_1
    WHERE 1 = 1
  ),

  test_cte_2 AS (
    SELECT *
    FROM test_table_2
    WHERE
      1 = 1
      AND user_id IN (SELECT DISTINCT user_id FROM test_cte_1)
  ),

  test_cte_3 AS (
    SELECT *
    FROM test_cte_1
    GROUP BY 1
  ),

  test_cte_4 AS (
    SELECT *
    FROM test_table_3
    WHERE 1 = 1
  ),

  test_cte_5 AS (
    SELECT *
    FROM test_cte_4 AS cte_4
    GROUP BY 1
  ),

  test_cte_6 AS (
    SELECT *
    FROM test_cte_2
    GROUP BY 1
  ),

  test_cte_7 AS (
    SELECT *
    FROM test_cte_2 AS u
    JOIN test_table_4 AS ch ON u.user_id = ch.user_id
    JOIN test_cte_1 AS r ON u.user_id = r.user_id
    GROUP BY 1
    ORDER BY 1
  )

  SELECT *
  FROM test_cte_3 AS r
  LEFT JOIN test_cte_6 ON 1 = 1
  LEFT JOIN test_cte_7 ON 1 = 1
  LEFT JOIN test_cte_5 ON 1 = 1
  WHERE 1 = 1
  ORDER BY 1
)
LIMIT 500
;
