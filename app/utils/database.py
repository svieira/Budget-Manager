def generate_result_set(query, method="all", include_headers=True):
    """Takes a SQLAlchemy query and returns the results

    This function includes the column names by default.
    Note: If ``method`` is not found on ``query`` only the headers are returned."""

    headers = []

    if include_headers:
        headers = [[desc["name"] for desc in query.column_descriptions]]

    return headers + getattr(query, method, lambda: [])()
