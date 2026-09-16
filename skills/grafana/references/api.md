# Grafana REST — endpoint đã verify

Base `$B = $GRAFANA_URL`, header `Authorization: Bearer <token>`.

| Endpoint | Kết quả |
|---|---|
| `GET $B/api/health` | version 10.4.19, database ok |
| `GET $B/api/org` | `BSS-MONITORING` (id 1) |
| `GET $B/api/datasources` | 5 datasource |
| `GET $B/api/folders?limit=50` | 15 folder |
| `GET $B/api/search?type=dash-db&limit=500` | 81 dashboard |
| `GET $B/api/dashboards/uid/<uid>` | JSON đầy đủ, panel nằm ở `dashboard.panels[]`, query ở `targets[].expr` |
| `GET $B/api/prometheus/grafana/api/v1/rules` | 33 group / 92 rule, mỗi rule có `state`, `alerts[]`, `query` |
| `GET $B/api/v1/provisioning/alert-rules` | **403** — thiếu quyền `alert.provisioning:read` |
| `GET $B/api/user` | rỗng (service account) |

## Proxy xuống datasource

```
$B/api/datasources/proxy/uid/<ds_uid>/<đường dẫn gốc của datasource>
```

- Prometheus: `api/v1/query`, `api/v1/query_range`, `api/v1/labels`, `api/v1/label/<tên>/values`
- Loki: `loki/api/v1/labels`, `loki/api/v1/query_range` (start/end **nanosecond**)
- Tempo: `api/traces/<traceID>`

## Folder

`BSS`, `BSS-MIDDLEWARE-NEW`, `Fmon - Endpoint/Kafka/Kong Gateway/Kubernetes/LinuxOS/MySQL/Redis`,
`IaaS Services`, `IAAS-ID-Troubleshoot`, `IAAS-K8S`, `IAAS-PORTAL-[ByLocNP]`,
`K8S CLUSTER (ID, Stag, JP)`, `xPlat`.
