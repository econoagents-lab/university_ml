from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.core_value_hardening import build_capacity_based_queue, build_capacity_public_payload, build_public_dashboard_html, build_capacity_review


def main() -> None:
    # Yo reconstruyo la cola con P0/P1 por capacidad comercial.
    queue = build_capacity_based_queue()
    payload = build_capacity_public_payload(queue)
    build_public_dashboard_html(payload)
    review = build_capacity_review(queue)
    print(review)


if __name__ == "__main__":
    main()
