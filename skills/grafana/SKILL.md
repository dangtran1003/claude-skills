---
name: grafana
description: Đọc Grafana fmon BSS ($GRAFANA_URL) — dashboard, panel query, PromQL, LogQL (Loki), alert rule đang firing. Dùng khi user hỏi về metric hạ tầng/K8s/MySQL/Kong, "grafana có gì", "alert nào đang kêu", "CPU/RAM/pod của service X", hoặc muốn biết một dashboard đang đo cái gì. Trigger - /grafana, "xem grafana", "check metric", "alert đang firing".
allowed-tools: Bash(python3 *), Bash(curl *), Read, Write
---

# Grafana — fmon BSS

Grafana 10.4.19, org `BSS-MONITORING`, base URL **có prefix path**:
`$GRAFANA_URL`. Bỏ prefix là 502 (openresty), không phải 404 — đừng đọc nhầm thành sập.

Token service-account nằm ở `~/.claude/skills/grafana/.env` (chmod 600). **Không in token ra output, không paste sang file khác, không commit.**

## Công cụ

```bash
G=~/.claude/skills/grafana/scripts/gf.py
python3 $G --help
```

| Lệnh | Việc |
|---|---|
| `datasources` | liệt kê datasource + uid |
| `dashboards [từ khoá]` | tìm dashboard (81 cái, 15 folder) |
| `panels <uid>` | dump panel + query thật của dashboard đó |
| `promql '<expr>' [--range PHÚT] [--step 60s]` | instant hoặc range query |
| `labels [tên_label]` | list label, hoặc giá trị của 1 label |
| `logql '<expr>' [--minutes N]` | query Loki |
| `alerts [--firing]` | 92 alert rule / 33 group, kèm state |

Mặc định dùng Prometheus `prometheus` và Loki `loki`; đổi bằng `--uid`.

## Datasource

| Loại | uid | Ghi chú |
|---|---|---|
| prometheus | `` | default, dùng cho hầu hết dashboard |
| prometheus | `` | `Prometheus-1` |
| loki | `` | label hạ tầng: `db_type`, `host`, `log_type`, `kubernetes_cluster_name` — log MySQL/OS |
| loki | `` | `Loki-1`, label kiểu k8s: `app`, `namespace`, `pod`… |
| tempo | `` | trace |

**Hai Loki có tập label khác hẳn nhau** — query sai datasource thì trả rỗng chứ không báo lỗi. Chạy `labels --uid <uid>` trước khi kết luận "không có log".

## Quyền của token

Đọc được: search/dashboard, datasource proxy (PromQL/LogQL), `/api/prometheus/grafana/api/v1/rules`.
**Không** đọc được `/api/v1/provisioning/alert-rules` (thiếu `alert.provisioning:read`) → muốn xem định nghĩa alert thì dùng đường `/api/prometheus/...` ở trên. `/api/user` trả rỗng vì là service account.

## Cách dùng hiệu quả

- Muốn biết một service được đo bằng metric nào: `dashboards <tên>` rồi `panels <uid>` — panel chứa query thật, copy sang `promql`/`logql` mà chạy, khỏi đoán tên metric.
- Nhiều dashboard IaaS/BSS đo qua **LogQL + `pattern`** trên log pod (vd dashboard `API` uid `lgIiq4B4z` parse status_code từ access log của `api-svc-iaas-vmware`), không phải Prometheus. Đừng mặc định cái gì cũng là metric.
- Grafana này **khác SigNoz** (`$SIGNOZ_URL`): Grafana đo hạ tầng/K8s/MySQL/Kong, SigNoz giữ trace + log ứng dụng portal. Câu hỏi về endpoint/trace/exception của portal thì sang SigNoz.

Xem thêm `references/api.md` cho các endpoint REST thô.
