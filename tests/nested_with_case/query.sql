SELECT *
FROM (
  WITH test_cte_1 AS (
    SELECT id AS user_id
    FROM test_table_1
    WHERE 1 = 1
  )

  SELECT *
  FROM test_cte_1
)
