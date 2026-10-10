from pathlib import Path
import secrets
root=Path(__file__).resolve().parents[1]
if (root/'.env').exists():raise SystemExit('.env already exists; edit it explicitly')
text=(root/'.env.example').read_text().replace('POSTGRES_PASSWORD=CHANGE_ME','POSTGRES_PASSWORD='+secrets.token_hex(24)).replace('GRAFANA_PASSWORD=CHANGE_ME','GRAFANA_PASSWORD='+secrets.token_hex(24))
token=secrets.token_hex(24);text=text.replace('METRICS_TOKEN=','METRICS_TOKEN='+token)
(root/'.env').write_text(text);(root/'.env').chmod(0o600)
(root/'infra/metrics-token').write_text(token)
print('Configuration created. Edit provider keys and mode in .env.')
