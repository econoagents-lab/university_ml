from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from marts.build_demo_marts import build_project_month_demo, build_market_demo

if __name__ == "__main__":
    # Yo genero marts seguros para poder ejecutar el trabajo final sin exponer CRM real.
    build_project_month_demo()
    build_market_demo()
    print("OK: economic marts generados.")
