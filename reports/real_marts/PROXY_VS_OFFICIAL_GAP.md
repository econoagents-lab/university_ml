# Proxy vs Official Gap

Yo comparo proxies antiguos contra marts reales para decidir qué métrica ya puede defenderse con evidencia dura.

| family        | previous_metrics_status   | new_mart_status         | mart_path                                                 |   rows | gap_closed   | decision       |
|:--------------|:--------------------------|:------------------------|:----------------------------------------------------------|-------:|:-------------|:---------------|
| funnel        | ok                        | official_mart_available | data\processed\real_marts\mart_funnel_stage_month.csv     |      1 | False        | usar_mart_real |
| cobranza      | ok                        | official_mart_available | data\processed\real_marts\mart_cobranza_venta.csv         |     17 | False        | usar_mart_real |
| stock_pricing | ok                        | official_mart_available | data\processed\real_marts\mart_stock_inicial_mensual.csv  |    134 | False        | usar_mart_real |
| pricing       | unknown                   | official_mart_available | data\processed\real_marts\mart_pricing_unit_m2.csv        |   3236 | True         | usar_mart_real |
| market        | proxy                     | official_mart_available | data\processed\real_marts\mart_project_vs_market.csv      |     17 | True         | usar_mart_real |
| feedback      | ok                        | official_mart_available | data\processed\real_marts\mart_feedback_interventions.csv |     15 | False        | usar_mart_real |