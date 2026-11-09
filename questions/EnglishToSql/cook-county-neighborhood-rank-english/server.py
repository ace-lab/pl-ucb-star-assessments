REFERENCE_QUERIES = {
    "task_a": """WITH filtered_sales AS (
    SELECT
        sale_year,
        neighborhood_code,
        sale_price * 1.0 / building_sqft AS price_per_sqft
    FROM cook_county
    WHERE sale_year >= 2016
      AND sale_year <= 2019
      AND modeling_group = 'SF'
      AND sale_price >= 10000
      AND building_sqft > 0
      AND garage_indicator = 1
),
neighborhood_summaries AS (
    SELECT
        sale_year,
        neighborhood_code,
        COUNT(*) AS sale_count,
        ROUND(AVG(price_per_sqft), 2) AS avg_price_per_sqft
    FROM filtered_sales
    GROUP BY sale_year, neighborhood_code
    HAVING COUNT(*) >= 10
),
ranked_neighborhoods AS (
    SELECT
        sale_year,
        neighborhood_code,
        sale_count,
        avg_price_per_sqft,
        ROW_NUMBER() OVER (
            PARTITION BY sale_year
            ORDER BY avg_price_per_sqft DESC, neighborhood_code ASC
        ) AS rank_in_year
    FROM neighborhood_summaries
)
SELECT
    sale_year,
    neighborhood_code,
    sale_count,
    avg_price_per_sqft,
    rank_in_year
FROM ranked_neighborhoods
WHERE rank_in_year <= 3;""",
    "task_b": """WITH property_class_summaries AS (
    SELECT
        property_class,
        sale_year,
        COUNT(*) AS sale_count,
        ROUND(AVG(sale_price), 2) AS avg_sale_price
    FROM cook_county
    WHERE sale_year >= 2013
      AND sale_year <= 2019
      AND modeling_group = 'SF'
      AND sale_price >= 10000
      AND building_sqft > 0
      AND central_air = 1
    GROUP BY property_class, sale_year
    HAVING COUNT(*) >= 25
),
ranked_years AS (
    SELECT
        property_class,
        sale_year,
        sale_count,
        avg_sale_price,
        ROW_NUMBER() OVER (
            PARTITION BY property_class
            ORDER BY sale_count DESC, sale_year ASC
        ) AS rank_in_class
    FROM property_class_summaries
)
SELECT
    property_class,
    sale_year,
    sale_count,
    avg_sale_price,
    rank_in_class
FROM ranked_years
WHERE rank_in_class <= 2;""",
}


def generate(data):
    task = data["preferences"].get("problem_variant", "task_b")
    if task not in REFERENCE_QUERIES:
        raise ValueError(f"Unknown problem_variant: {task!r}")
    data["params"]["task_a"] = task == "task_a"
    data["params"]["task_b"] = task == "task_b"
    data["correct_answers"]["reference_sql"] = REFERENCE_QUERIES[task]
