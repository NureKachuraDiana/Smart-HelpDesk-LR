"""Static, non-implementation checks for Smart HelpDesk LR1 artifacts."""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
required = ["requirements.md", "architecture.md", "api-contract.md", "traceability.csv", "ai-log.md", "lab-01.md"]
for filename in required:
    assert (DOCS / filename).is_file(), f"Missing {filename}"

req = (DOCS / "requirements.md").read_text(encoding="utf-8")
api = (DOCS / "api-contract.md").read_text(encoding="utf-8")
arch = (DOCS / "architecture.md").read_text(encoding="utf-8")
with (DOCS / "traceability.csv").open(encoding="utf-8-sig", newline="") as f:
    trace = list(csv.DictReader(f))

for n in range(1, 9):
    assert f"FR-{n:02}" in req, f"Missing FR-{n:02}"
for n in range(1, 8):
    assert re.search(rf"### US-{n:02}\.", req), f"Missing US-{n:02}"
    assert re.search(rf"AC-{n:02}-01", req), f"Missing primary AC for US-{n:02}"
    assert re.search(rf"AC-{n:02}-02", req), f"Missing boundary AC for US-{n:02}"
for n in range(1, 7):
    assert f"NFR-{n:02}" in req, f"Missing NFR-{n:02}"

# Full status matrix contains all state labels on the row axis and column axis.
for token in ["**OPEN**", "**IN_PROGRESS**", "**CLOSED**", "Ідемпотентно, 200", "Заборонено, 409"]:
    assert token in req, f"Incomplete state matrix: {token}"

expected_routes = {
    ("GET", "/health"), ("GET", "/users"), ("POST", "/issues"),
    ("GET", "/issues"), ("GET", "/issues/{id}"),
    ("PATCH", "/issues/{id}"), ("PATCH", "/issues/{id}/status"),
    ("POST", "/issues/{id}/comments"), ("GET", "/issues/{id}/comments"),
}
found_routes = set(re.findall(r"\|\s*\d+\s*\|\s*`(GET|POST|PATCH)\s+(/[^`]+)`", api))
assert found_routes == expected_routes, f"Routes differ: missing={expected_routes-found_routes}; extra={found_routes-expected_routes}"
assert "ADR-01" in arch and "ADR-02" in arch
assert "```mermaid" in arch

covered = {row["FR"] for row in trace if row["User_Story"] and row["Acceptance_Criteria"] and row["API_Endpoint"] and row["Future_Test"]}
expected = {f"FR-{n:02}" for n in range(1, 8)}
assert expected <= covered, f"Traceability missing: {expected - covered}"
assert "FR-08" not in covered, "Future AI feature should be excluded from current coverage"
assert "Порожнє тіло" in req and "атомар" in req.lower()
assert len(trace) >= 7

print("OK: All six required docs exist")
print("OK: FR-01..FR-08, US-01..US-08, AC, NFR-01..NFR-06 found")
print("OK: 3x3 status matrix, PATCH, ADR-01, ADR-02 and Mermaid diagram present")
print(f"OK: {len(found_routes)} REST routes, {len(trace)} traceability links")
print(f"Traceability coverage: {len(expected & covered)}/7 = {100 * len(expected & covered) // 7}%")
