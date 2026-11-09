FILTER_COLUMNS = {
    "garage": "garage_indicator",
    "central_air": "central_air",
}


def reference_query(filter_column):
    return f"""WITH filtered_sales AS (
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
      AND {filter_column} = 1
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
WHERE rank_in_year <= 3;"""


REFERENCE_QUERIES = {
    variant: reference_query(filter_column)
    for variant, filter_column in FILTER_COLUMNS.items()
}


def generate(data):
    variant = data["preferences"].get("problem_variant", "central_air")
    if variant not in REFERENCE_QUERIES:
        raise ValueError(f"Unknown problem_variant: {variant!r}")
    data["params"]["garage_variant"] = variant == "garage"
    data["params"]["central_air_variant"] = variant == "central_air"
    data["correct_answers"]["reference_sql"] = REFERENCE_QUERIES[variant]
