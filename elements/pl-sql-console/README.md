# `pl-sql-console`

`pl-sql-console` is a small direct-SQL companion to the English-to-code custom
element. It accepts one SQLite `SELECT` or `WITH` query, runs it against
CSV-backed tables in an in-memory database, previews the result on **Save**, and
grades result rows on **Save & Grade**.

```html
<pl-sql-console
  answers-name="analysis_sql"
  database-schema="database_schema.json"
  reference-name="reference_sql"
  row-limit="20"
  weight="1">
</pl-sql-console>
```

`database-schema` uses the same JSON table format as
`pl-intent-console-dictionary`. The question's `server.py` must put a reference
query in `data["correct_answers"]` under `reference-name`.

The element accepts read-only queries only. SQLite authorizer callbacks deny
writes and non-query operations, and SQL length, result size, input row, column,
and instruction limits constrain execution. Grading compares row values and
multiplicity while ignoring row order and column labels.
