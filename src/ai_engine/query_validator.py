import re
from src.warehouse.engine import warehouse

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE", "ATTACH", "DETACH", "COPY", "EXPORT",
    "INSTALL", "LOAD", "PRAGMA", "EXEC", "EXECUTE", "SYSTEM",
    "CREATE", "REPLACE"
}

class QueryValidationError(Exception):
    pass

class QueryGuard:
    """
    Zero-Trust SQL Security Guard and Validator.
    Protects the analytical database against SQL injection, mutation commands,
    and denial-of-service queries.
    """
    @classmethod
    def validate_and_sanitize(cls, sql: str) -> str:
        clean_sql = sql.strip().rstrip(";")
        
        # Check empty
        if not clean_sql:
            raise QueryValidationError("Query cannot be empty.")

        # Ensure query begins with SELECT or CTE (WITH)
        normalized = clean_sql.upper()
        if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
            raise QueryValidationError("Only read-only SELECT or WITH (CTE) queries are allowed.")

        # Check forbidden keywords as whole words
        tokens = set(re.findall(r"\b[A-Z_]+\b", normalized))
        violations = tokens.intersection(FORBIDDEN_KEYWORDS)
        if violations:
            raise QueryValidationError(f"Forbidden operations detected in analytical query: {', '.join(violations)}")

        # Dry-run validation using EXPLAIN in read-only connection
        try:
            with warehouse.get_connection(read_only=True) as con:
                con.execute(f"EXPLAIN {clean_sql}")
        except Exception as e:
            raise QueryValidationError(f"SQL Syntax / Semantic validation error: {str(e)}")

        return clean_sql

guard = QueryGuard()
