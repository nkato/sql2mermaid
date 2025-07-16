SELECT
  `col1` AS `col1`,
  `col2` AS `col2`,
  `col3` AS `col3`,
  `col4` AS `col4`,
  `col5` AS `col5`
FROM (
  WITH cte1 AS (

    SELECT DISTINCT
      SAFE_CAST(table1.id1 AS int64) AS id1,
      DATE(table1.col1, 'UTC') AS col1,
      COALESCE(REGEXP_EXTRACT(table1.col2, r'(?:\?|&)param1=([^&|#]*)'), 'none') AS col2
    FROM
      `project1.dataset1.table1`
    WHERE
      DATE(table1.col1, 'UTC') BETWEEN CURRENT_DATE('UTC') - 4 AND CURRENT_DATE('UTC') - 1
      AND (table1.id1 IS NOT null AND table1.id1 <> '')
      AND table1.col3 = 'value1'
      AND table1.col4 = 'value2'
      AND table1.col5 IN ('value3', 'value4')

  ),

  cte2 AS (

    SELECT
      id1 AS id1,
      DATE(MIN(col1), 'UTC') AS col1,
      MAX(1) AS flag1
    FROM
      `project2.dataset2.table2`
    WHERE
      col2 = 'value5'
      AND
      DATE(col1, 'UTC') BETWEEN '2024-01-01' AND '2024-01-31'
    GROUP BY 1


  ),

  cte3 AS (

    SELECT
      id1 AS id1,
      MIN(DATE(col1, 'UTC')) AS col1,
      MAX(1) AS flag2
    FROM
      `project3.dataset3.table3`
    GROUP BY 1

  ),

  cte4 AS (

    SELECT
      t1.id1,
      t1.col1,
      t1.col2,
      t2.col1 AS col6,
      COALESCE(flag1, 0) AS flag1,
      COALESCE(t3.flag2, 0) AS flag2
    FROM
      cte1 t1
    LEFT JOIN
      cte2 t2
      ON t1.id1 = t2.id1 AND t1.col1 = t2.col1
    LEFT JOIN
      cte3 t3
      ON t1.id1 = t3.id1 AND t1.col1 = t3.col1

  )

  SELECT
    col1,
    col2,
    COUNT(DISTINCT id1) AS col3,
    SUM(flag1) AS col4,
    SUM(CASE WHEN flag1 = 1 AND flag2 = 1 THEN 1 ELSE 0 END) AS col5
  FROM cte4
  GROUP BY 1, 2
  ORDER BY 1, 2
)
LIMIT 25000
