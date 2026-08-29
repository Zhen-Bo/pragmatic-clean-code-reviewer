# Finding schema

Write every active or dismissed finding once in a Markdown shard. Use the fixed field names and section headings below so the validator can read the record without a second data format.

~~~~markdown
## F-17 — Account loader is too long

- `status`: `active`
- `rule`: `code.long-function`
- `evidence_rank`: `mechanical`
- `location`: `src/services/account.py:42`

### Evidence

load_account has 84 non-blank, non-comment lines; the small profile threshold is 60.

### Snippet

```python
def load_account(account_id: str) -> Account:
    row = db.fetch_account(account_id)
    if row is None:
        raise AccountNotFound(account_id)
    …
```

### Consequence

A reader cannot hold the whole function in mind, so every change needs a full re-read.
~~~~

Repeat the `location` field for each additional repo-relative `path:line`. Use `### Removal reason` instead of `### Consequence` for a dismissed finding. A snippet contains at most 10 source lines; longer spans show the head plus `…`.

## Fields

| field | required | content |
| --- | --- | --- |
| heading id | yes | global `F-n`, assigned after merge and sort |
| heading title | yes | plain-language headline |
| `status` | yes | `active` or `dismissed` |
| `rule` | yes | registry rule key |
| `evidence_rank` | yes | `mechanical`, `semantic`, or `estimate` |
| `location` | yes | one or more repo-relative `path:line` values |
| `Evidence` | yes | measurement or semantic basis |
| `Snippet` | yes | verbatim source, at most 10 lines |
| `Consequence` | active | maintainer cost supported by the evidence |
| `Removal reason` | dismissed | registry exception or semantic rejection reason |

Do not invent severity because the schema has none.

## Ordering and ids

Merge and deduplicate first. Sort active records before dismissed records, then by first location path, line, rule key, and id. Assign `F-1…F-n` once across the full run. Shards preserve these ids; no shard restarts numbering.
