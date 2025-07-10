CREATE TEMP FUNCTION ADD_ONE(x INT64) AS (x + 1);

CREATE TEMP TABLE temp_table AS (
  SELECT
    id,
    name
  FROM users
);

WITH first_cte AS (
  SELECT * FROM table1
)

SELECT * FROM first_cte
INNER JOIN table2 ON first_cte.id = table2.id;

WITH second_cte AS (
  SELECT * FROM table3
  UNION ALL
  SELECT * FROM table4
)

SELECT * FROM second_cte
LEFT JOIN table5 ON second_cte.id = table5.id;
