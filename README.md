# Kalshi API Scripts

Small Python workspace for testing Kalshi API workflows.

Each script either fetches data from the API or sends requests to it, mainly around combo markets, RFQs, and ticker discovery.

## Files

- `auth.py` – authentication helper
- `create_combo.py` – create combo markets
- `find_combo_legs.py` – inspect combo legs / inputs
- `mve_tester.py` – test multivariate event endpoints
- `rfq_creation.py` – create RFQs
- `rfq_watcher.py` – watch RFQ activity
- `ticker_finder.py` – find relevant tickers
- `watch_my_rfq.py` – monitor my submitted RFQs

## Notes

- Uses local credentials for authenticated requests
- Built for experimentation and workflow understanding, not production use
