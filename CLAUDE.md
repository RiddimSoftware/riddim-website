# Riddim Website Agent Instructions

## Linear Access

- Use the Linear MCP tools as the default path for Linear reads and writes.
- If MCP coverage is insufficient for a needed Linear endpoint, field, or workflow operation, fetch the Linear API token from AWS Secrets Manager and use the Linear GraphQL API directly.
- Treat the Linear API token as secret material: use it ephemerally, and do not print, commit, or persist it outside the minimum local process state needed for the call.
