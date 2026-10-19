# fgmonitoringservice40270840

A monitor for QUBCloud-FraudGuard. It sends a known test batch through the real system, checks the decisions against expected results, times it, and alerts when something is wrong.

Part of [QUBCloud-FraudGuard](https://github.com/QUBFraudGuard).

## What it does

- **On demand:** `GET /check` runs the test batch now and returns the actual and expected decisions, whether it passed, and the duration.
- **Periodic:** a background thread runs the same check every 60 seconds, alongside on-demand checks.
- **Alerts:** a failed check (wrong decision, or a network or backend error) logs an `[ALERT]` line. Passing checks log `[INFO]`.

Checks go through the proxy to both screening services, so they exercise the same path as real traffic, including routing and the circuit breaker.

## Example response

```json
{
  "passed": true,
  "duration": 0.32,
  "actual": ["OK", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS"],
  "expected": ["OK", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS"]
}
```

## Limitations

Alerts only appear in the pod logs, so someone has to be watching. Production would need push notifications. Results aren't stored.

## Run it

```bash
git clone https://github.com/QUBFraudGuard/fgmonitoringservice40270840.git
cd fgmonitoringservice40270840
pip install -r requirements.txt
python monitor.py
```
