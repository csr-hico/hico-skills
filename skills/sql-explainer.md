---
name: SQL Query Explainer
description: >
  Explains what a SQL query does in plain language, flags likely performance issues (missing
  indexes, N+1 shapes, full scans), and suggests a safer or faster rewrite when warranted.
type: skill
triggers:
  - explain this SQL
  - what does this query do
  - why is this query slow
---

# SQL Query Explainer

Given a SQL statement:

1. Summarize the intent in one sentence.
2. Walk the clauses (FROM/JOIN/WHERE/GROUP BY/HAVING/ORDER BY) in execution order.
3. Flag performance smells: leading-wildcard LIKE, functions on indexed columns, implicit casts,
   cartesian joins, SELECT * on wide tables, missing/likely-missing indexes.
4. If a clearly better rewrite exists, show it and state the tradeoff. Otherwise say it looks fine.

Never claim an index exists or a row count without evidence - ask or mark it as an assumption.
