def matches_status(issue, value):
    if value is None:
        return True
    return issue["status"] == value


def matches_priority(issue, value):
    if value is None:
        return True
    return issue["priority"] == value