---
name: codebase-doc
description: >
  Kiến trúc tài liệu cho codebase, chạy 2 phase độc lập. Phase SCAN quét routes rồi cập nhật
  registry trung tâm docs/ROUTE_LIST.md; phase GEN sinh tài liệu module kèm flow inventory,
  sequence diagram và known issues. Dùng khi user muốn "viết tài liệu cho codebase", "quét lại
  danh sách route", "sinh doc cho module X", hoặc cần release note theo branch.
  Trigger - /codebase-doc, /codebase-doc --scan, /codebase-doc --gen.
---

# /codebase-doc — Codebase Documentation Architect

## Tổng quan

Skill có **2 phase độc lập**:

```
Phase 1 — SCAN:  /codebase-doc --scan
  └─ Quét routes → cập nhật docs/ROUTE_LIST.md (registry trung tâm)

Phase 2 — GEN:   /codebase-doc --gen --module <tên> [options]
  └─ Đọc ROUTE_LIST.md → gen/update docs/modules/{tên}.md
```

**Registry trung tâm:** `docs/ROUTE_LIST.md`
**Module docs:** `docs/modules/{module}.md`

---

## Cấu trúc output thực tế

```
docs/
├── ROUTE_LIST.md              ← Central registry
└── modules/
    ├── alert.md
    ├── autoscaling.md
    ├── backup.md
    ├── cloud-advisor.md
    ├── custom-image.md
    ├── ddos.md
    ├── edge-gateway.md
    ├── floating-ip.md
    ├── global-search.md
    ├── iam.md
    ├── load-balancer.md
    ├── lbaas-v2.md
    ├── networks.md
    ├── nic.md
    ├── osp-native-backup.md
    ├── recent-tasks.md
    ├── s3.md
    ├── schedule.md
    ├── security-groups.md
    ├── snapshot-schedule.md
    ├── storage.md
    ├── vm.md
    ├── vm-group.md
    ├── vpnaas.md
    └── ...
```

---

## Phase 1: SCAN — `/codebase-doc --scan`

### Mục đích

Quét toàn bộ route files, cập nhật `docs/ROUTE_LIST.md`.
**Không gen module doc nào.**

### Format `docs/ROUTE_LIST.md`

Tuân thủ chính xác format hiện tại:

```markdown
# Route List — Chi tiết tất cả routes

**Service:** `portal-api-svc-iaas-vmw`
**Total:** {N} routes / {M} modules
**Legend:** ✅ Documented đầy đủ | 🟡 Partial | ❌ Chưa có docs

---

## V1 — Main API (/api/v1/)

### {STATUS} `v1/{module}` — {N} routes | Docs: {ID range} ({file}.md)

| Method | Path            |
| ------ | --------------- |
| `GET`  | `/some/path`    |
| `POST` | `/another/path` |
```

**DOC_STATUS:**

- `✅` — documented đầy đủ, tất cả flows có diagram
- `🟡` — partial, có doc nhưng còn thiếu flows
- `❌` — chưa có docs

**Docs field:**

- Có: `Docs: FIP-01→FIP-11 (floating-ip.md)`
- Partial: `Docs: AL-01→AL-06 (partial)`
- Không: `Docs: —`

### Thực hiện

**Bước 1 — Tìm route files**

```
Đọc: router registration file (__init__.py / router.go / index.ts)
Với mỗi route file:
  - Ghi FULL PATH tuyệt đối từ project root:
    ✅ portal-api-svc-iaas-vmw/service/api/v1/floating_ips/blueprint.py
    ❌ service/api/v1/floating_ips  ← thiếu prefix
  - Đọc file: method, path, handler, IAM decorator nếu có
  - Group theo blueprint/module name
  - Đếm routes
```

**Bước 2 — Nhóm theo version**

```
/api/v1/           → ## V1 — Main API
/api/v2/           → ## V2 — API v2
/api/v1/api_internal/ → ## V1 Internal
```

**Bước 3 — Check doc status**

```
Đọc docs/modules/ → biết module nào đã có
So sánh Flow Inventory trong file đó với routes scan được:
  Không có file       → ❌
  File có nhưng FLOW_PROGRESS chưa N/N → 🟡 partial
  FLOW_PROGRESS = N/N → ✅
```

**Bước 4 — Cập nhật ROUTE_LIST.md**

```
ROUTE_LIST.md đã tồn tại:
  → Chỉ thêm routes MỚI, không xóa rows cũ
  → Update DOC_STATUS cho modules có doc mới
  → Cập nhật Total count header

Chưa có: tạo mới
```

**Output sau scan:**

```
Scan hoàn tất:
  Total: 1519 routes / 148 modules
  ✅ 18 modules documented
  🟡 9 modules partial
  ❌ 121 modules chưa có docs

  Ưu tiên cao (route count):
    ❌ v1/organization     — 67 routes
    ❌ v1/public_api/common — 55 routes
    ❌ v1/contract         — 28 routes

  Chạy:
    /codebase-doc --gen --module organization
    /codebase-doc --gen --module contract
```

---

## Phase 2: GEN — `/codebase-doc --gen [options]`

### Options

| Flag                    | Tác dụng                                   |
| ----------------------- | ------------------------------------------ |
| `--module <tên>`        | Gen/update doc cho 1 module                |
| `--api <FIP-01,FIP-02>` | Gen doc cho 1-2 flows cụ thể               |
| `--update-mr`           | Gen release note từ git diff               |
| `--flows-remaining`     | Tiếp tục flows còn thiếu sau context limit |
| `--codex`               | Opt-in: cập nhật `.codex/modules/`         |

---

### `--module <tên>`

**Bước 1 — Đọc ROUTE_LIST.md, không scan lại source**

```
Tìm section tương ứng trong ROUTE_LIST.md
Lấy: danh sách routes (method + path)
Lấy: file paths đã ghi từ lần scan

CHỈ đọc files có trong ROUTE_LIST.md section đó.
Không đọc files module khác.
Không scan lại toàn project.
```

**Bước 2 — Đọc file hiện có nếu đã tồn tại**

```
Nếu docs/modules/{tên}.md đã có:
  - Đọc Flow Inventory để biết flows nào đã có diagram
  - FLOW_PROGRESS comment để biết tiến độ
  - Append/update phần còn thiếu, KHÔNG xóa content cũ

Nếu chưa có: tạo mới
```

**Bước 3 — Completion Gate**

```
Công bố trước khi vẽ:
  "Module {tên}: {N} flows
   Có diagram (async/complex): {list IDs}
   Skip diagram (GET read-only): {list IDs}
   Bắt đầu: 0/{N_async}"

Cập nhật FLOW_PROGRESS sau MỖI flow — không batch.
KHÔNG dừng cho đến FLOW_PROGRESS = N/N.

Nếu context limit sắp hết:
  Ghi <!-- INCOMPLETE: còn FIP-08, FIP-09 -->
  Để --flows-remaining tiếp tục chính xác.
```

**Anti-shortcuts:**

```
❌ "Tương tự FIP-01, xem FIP-01"  → phải vẽ thật
❌ "Còn lại theo pattern tương tự" → phải vẽ từng cái
❌ Gộp 2 flows vào 1 diagram       → mỗi flow 1 diagram riêng
```

---

### Format `docs/modules/{tên}.md`

Format chuẩn — tuân thủ chính xác như floating-ip.md và alert.md:

````markdown
# Module: {Tên hiển thị}

## Overview

{Mô tả module làm gì, business context, loại operations}
{Liệt kê sub-features nếu có: DNAT, SNAT, NO-SNAT...}

**{External system name}:** {Tên cụ thể} ({internal/external}, via `{ENV_VAR}`)
**{Async info}:** Celery task `{task_name}` cho {operation}, `{task2}` cho {op2}

## Files

| File                                                           | Mục đích             |
| -------------------------------------------------------------- | -------------------- |
| `portal-api-svc-iaas-vmw/service/api/v1/{module}/blueprint.py` | Route definitions    |
| `portal-api-svc-iaas-vmw/service/managers/{Manager}.py`        | Business logic       |
| `portal-celery/tasks/{task}.py`                                | Celery: {mô tả task} |

## Flow Inventory

| Flow ID  | Endpoint                                 | Method | Description  |
| -------- | ---------------------------------------- | ------ | ------------ |
| {PRE}-01 | `/api/v1/vmware/vpc/{vpcId}/{path}`      | POST   | {Mô tả ngắn} |
| {PRE}-02 | `/api/v1/vmware/vpc/{vpcId}/{path}`      | GET    | {Mô tả ngắn} |
| {PRE}-03 | `/api/v1/vmware/vpc/{vpcId}/{path}/{id}` | PUT    | {Mô tả ngắn} |
| {PRE}-04 | `/api/v1/vmware/vpc/{vpcId}/{path}/{id}` | DELETE | {Mô tả ngắn} |

<!-- FLOW_PROGRESS: 0/{N} -->

## Sequence Diagrams

### Flow {PRE}-01: {Tên flow}

```mermaid
sequenceDiagram
    title {PRE}-01 — {Tên flow đầy đủ}

    actor User
    participant API as VMware IaaS API :5020
    participant DB as MySQL
    [participant Redis as Redis]          ← chỉ thêm nếu có cache
    [participant Celery as Celery Worker] ← chỉ thêm nếu có async
    [participant IAM as Keycloak IAM]     ← chỉ thêm nếu có IAM call
    [participant {Ext} as {External}]     ← tên system cụ thể

    User->>API: {METHOD} {full path}\n{{request body nếu POST/PUT}}
    Note over API: @{iam_decorator}({Actions.Resource.action})\n@{other_decorators}

    [API->>IAM: iam_validate → check {permission}]
    [IAM-->>API: 200 OK]

    [API->>DB: {lookup/validate query}]
    [DB-->>API: {kết quả}]

    alt {Error condition 1}
        API-->>User: {status} {ERROR_CODE hoặc message}
    else {Error condition 2}
        API-->>User: {status} {ERROR_CODE}
    end

    [sync GET: trả về luôn, không cần Celery section]
    API-->>User: 200 OK {{response}}

    [async: dispatch Celery rồi return 200/202, Celery xử lý tiếp]
    API->>DB: INSERT/UPDATE {table} (status=PENDING/CREATING)
    API->>Celery: send_task({task_name}, kwargs={{...}})
    Note over Celery: Async — {task_file}::{task_function}\n{mô tả ngắn task làm gì}
    API-->>User: 200 OK {{status, message}} hoặc 202 Accepted

    Celery->>{Ext}: {External API call}
    {Ext}-->>Celery: {response}

    alt SUCCESS
        Celery->>DB: UPDATE {table} SET status=ACTIVE
        [Celery->>DB: UPDATE quota_usage]
    else ERROR / Timeout
        Celery->>DB: UPDATE {table} SET status=ERROR
        [Celery->>DB: Rollback quota nếu applicable]
    end
```
````

**File:** `{full/path/blueprint.py}::{handler_function}()`
**Task:** `{full/path/tasks.py}::{task_function}` | Queue: `{queue_name}`
**Gotchas:**

- {Điều gì cần chú ý — edge case, limitation, gotcha thực tế}

<!-- FLOW_PROGRESS: 1/{N} -->

---

[Repeat cho mỗi flow]

<!-- FLOW_PROGRESS: {N}/{N} — COMPLETE -->

## Known Issues & Gotchas

| Severity | Issue                                       | Impact    |
| -------- | ------------------------------------------- | --------- |
| WARNING  | {Mô tả bug/risk cụ thể — file + behavior}   | {Hậu quả} |
| INFO     | {Observation không phải bug nhưng cần biết} | {Lưu ý}   |

```

---

### Rules bắt buộc khi viết sequence diagrams

**1 — Participants: chỉ thêm những gì thực sự tham gia**

```

actor User → luôn có
participant API → luôn có, ghi rõ port: "VMware IaaS API :5020"
participant DB → thêm nếu có DB query
participant Redis → thêm nếu có cache read/write
participant Celery → thêm nếu có async task
participant IAM → thêm nếu có IAM call riêng (không phải chỉ decorator)
participant {ExtSys} → tên cụ thể: "VMware VCD", "OpenStack", "Monasca / FMon",
"Billing Service", "Veeam", "Jira", "Firebase"

````

**2 — Note over API: ghi decorators thực tế**

```mermaid
Note over API: @iam_validate(Actions.Ip.connect)\n@check_billing_budget()
````

Đọc blueprint.py để lấy decorator names thực tế, không đoán.

**3 — alt/else blocks: đọc code để lấy error conditions thực tế**

```mermaid
alt No edge gateway found
    API-->>User: 400 EDGE_GATEWAY_NOT_EXIST
else Multiple edge gateways
    API-->>User: 400 EDGE_GATEWAY_SIZE_INVALID
end
```

Không dùng generic "Error occurred" — phải là error code/message thực từ code.

**4 — Phân biệt sync vs async**

_Sync (GET, validate):_

```mermaid
API->>DB: SELECT ...
DB-->>API: data
API-->>User: 200 OK {data}
```

_Async (POST/PUT/DELETE có Celery):_

```mermaid
API->>DB: INSERT resource (status=PENDING)
API->>Celery: send_task(task_name, kwargs={...})
Note over Celery: Async — tasks/file.py::task_function
API-->>User: 200 OK {status: true}

Celery->>ExternalSys: API call
ExternalSys-->>Celery: result
Celery->>DB: UPDATE resource (status=ACTIVE)
```

**5 — Ghi rõ task name và file thực tế**

```
Note over Celery: wf_allocate_pool_v2 execution:
```

hoặc

```
Note over Celery: Async — portal-celery/tasks/vm.py::create_vm_task
```

**6 — Flow ID prefix theo module**

```
FIP → Floating IP
AL  → Alert
VM  → VM / Compute
SG  → Security Group
NW  → Network
STO → Storage
BK  → Backup
LB  → Load Balancer
VPN → VPNaaS
IAM → IAM
ORG → Organization
ANN → Annex
CTR → Contract
SCL → Scaling
SCH → Schedule
...
```

**7 — Flows nào cần diagram vs không cần**

Cần diagram:

- POST/PUT/DELETE có Celery async
- POST/PUT/DELETE có external API call (VCD, OpenStack, Monasca...)
- GET có complex logic (multiple branches, quota check, IAM validation)
- GET có external call

Có thể skip diagram (chỉ ghi vào Flow Inventory):

- GET đơn giản đọc DB và trả về
- Validation endpoints (GET check-name, GET validate-\*)
- Reference data endpoints (GET list alarm-metrics, GET list-severity...)

---

### `--api <IDs>`

Gen doc cho 1-2 flows cụ thể.

```
/codebase-doc --gen --api FIP-01,FIP-06
```

1. Đọc ROUTE_LIST.md → lấy file path của FIP-01, FIP-06
2. Đọc đúng 2 file đó
3. Nếu `docs/modules/floating-ip.md` đã tồn tại: **append** flow vào section "Sequence Diagrams", update Flow Inventory table
4. Cập nhật ROUTE_LIST.md: DOC_STATUS → `🟡 partial` (nếu chưa đủ) hoặc `✅`

---

### `--update-mr`

Gen release note để paste vào MR description.

```
/codebase-doc --gen --update-mr
```

1. `git diff main..HEAD --name-only` → files thay đổi
2. Map files → Flow IDs trong ROUTE_LIST.md
3. `git log --oneline main..HEAD` → commits
4. Đọc nội dung files thay đổi để hiểu change
5. Output:

```markdown
## Release Note — [branch] — [date]

### Summary

[1-2 câu mô tả MR làm gì]

### APIs Changed

| Module      | Flow ID | Method | Path                                   | Change                          |
| ----------- | ------- | ------ | -------------------------------------- | ------------------------------- |
| floating-ip | FIP-01  | POST   | /vpc/{id}/floating-ips/allocate-pool   | Fix quota drift khi Celery fail |
| vm          | VM-05   | PUT    | /vpc/{id}/compute/instance/{id}/resize | Thêm concurrent lock            |

### Breaking Changes

- [Nếu có]
- Không có breaking changes

### Celery Tasks Changed

- `wf_allocate_pool_v2` — Thêm rollback khi VCD timeout

### Migration Required

- [Nếu có Alembic migration]
- Không cần migration

### Commits

- a1b2c3d fix: quota drift on allocate pool
- b2c3d4e feat: distributed lock for resize

### How to Test

1. [Step cụ thể]
2. [Step cụ thể]

### Checklist

- [ ] Unit tests pass
- [ ] Related docs updated: docs/modules/floating-ip.md
- [ ] ROUTE_LIST.md DOC_STATUS updated
```

Sau khi gen: update ROUTE_LIST.md — files bị thay đổi → DOC_STATUS = `🔄 stale` (nếu có doc cũ).

---

### `--flows-remaining`

Tiếp tục sau context limit.

```
/codebase-doc --gen --module floating-ip --flows-remaining
```

1. Đọc `docs/modules/floating-ip.md`
2. Tìm `<!-- INCOMPLETE: còn FIP-08, FIP-09 -->`
3. Đọc ROUTE_LIST.md → lấy file paths của FIP-08, FIP-09
4. Đọc đúng các files đó
5. Append flows còn thiếu, xóa INCOMPLETE comment
6. Cập nhật FLOW_PROGRESS
7. Update ROUTE_LIST.md DOC_STATUS

---

### `--codex` (opt-in)

Chỉ chạy khi có flag này. Không bao giờ tự động.

```
/codebase-doc --gen --module floating-ip --codex
```

Output thêm `.codex/modules/floating-ip.md`:

```markdown
# MODULE: floating-ip

# Agent: load file này khi task liên quan Floating IP / Public IP

ROUTE_FILES:
portal-api-svc-iaas-vmw/service/api/v1/floating_ips/blueprint.py
MANAGER_FILES:
portal-api-svc-iaas-vmw/service/managers/floating_ip_manager/FloatingIpManager.py
portal-api-svc-iaas-vmw/service/managers/NatRuleManager.py
TASK_FILES:
portal-celery/tasks/wf_allocate_pool_v2.py

FLOWS: FIP-01 POST allocate-pool | FIP-02 GET list | FIP-03 POST no-snat | FIP-06 POST payg/create

EXTERNAL_CALLS:
VCD: allocate IP from edge gateway pool
OpenStack: get_network_by_router, allocate floating IP

DB_TABLES: floating_ip (rw), nat_rule (rw), quota_usage (rw)
REDIS_KEYS: quota:{vpc_id} TTL=300

KNOWN_BUGS:
quota_drift | Celery fail sau allocate → quota không rollback
multi_egw_500 | VPC có >1 EGW → raise Exception thay vì 400
port_race | Public port uniqueness check không có DB lock
```

---

## Workflow theo team

### Lead / DevOps — lần đầu setup

```bash
/codebase-doc --scan

git add docs/ROUTE_LIST.md
git commit -m "chore: initial route registry scan — 1519 routes / 148 modules"
```

### Team gen doc module của mình

```bash
# network-team gen floating-ip
/codebase-doc --gen --module floating-ip

git add docs/modules/floating-ip.md docs/ROUTE_LIST.md
git commit -m "docs: floating-ip module — FIP-01 to FIP-11"

# compute-team gen vm (độc lập, cùng lúc)
/codebase-doc --gen --module vm

git add docs/modules/vm.md docs/ROUTE_LIST.md
git commit -m "docs: vm module — VM-01 to VM-34"
```

### Khi push MR

```bash
/codebase-doc --gen --update-mr
# Paste release note vào MR description

# Nếu MR thay đổi floating-ip module:
/codebase-doc --gen --module floating-ip
git add docs/modules/floating-ip.md docs/ROUTE_LIST.md
git commit -m "docs: update floating-ip doc after quota fix"
```

### Tiếp tục sau context limit

```bash
/codebase-doc --gen --module organization --flows-remaining
# Claude đọc INCOMPLETE comment → vẽ tiếp đúng flows còn thiếu
```

---

## Output Checklist

### Sau `--scan`

```
□ ROUTE_LIST.md đúng format: header, legend, sections V1/V2/Internal
□ Mỗi module có: status, route count, docs reference
□ Mỗi route có: method + path (full path từ blueprint)
□ Total count khớp với số routes thực tế
□ DOC_STATUS đúng dựa trên FLOW_PROGRESS trong module files
```

### Sau `--gen --module`

```
□ docs/modules/{tên}.md có đúng 5 sections: Overview, Files, Flow Inventory, Sequence Diagrams, Known Issues
□ Overview mô tả đúng business context + external systems + async info
□ Files table có FULL PATH của blueprint + manager + task files
□ Flow Inventory có đủ tất cả routes của module (kể cả GET read-only)
□ FLOW_PROGRESS = N/N (không còn INCOMPLETE comment)
□ Mỗi diagram async có: Note over Celery, alt SUCCESS/ERROR, status codes
□ Decorators ghi đúng từ code (@iam_validate, @check_billing_budget...)
□ Error codes là codes thực từ code, không phải generic
□ Known Issues ghi issues thực, không phải checklist chung chung
□ ROUTE_LIST.md đã update DOC_STATUS cho module
```

### Sau `--update-mr`

```
□ Release note có: summary, APIs Changed table với Flow IDs, commits
□ APIs Changed map đúng file thay đổi → Flow ID
□ ROUTE_LIST.md mark stale cho routes bị ảnh hưởng
```

---

## Anti-patterns

- ❌ Đọc files ngoài ROUTE_LIST.md khi `--gen` (không tự scan thêm)
- ❌ Gen module khác khi đang `--gen --module X`
- ❌ "Tương tự flow Y" — mỗi flow phải có diagram riêng
- ❌ Note over API để trống hoặc generic — phải ghi decorator thực
- ❌ `alt Error occurred` — phải là error code/condition thực từ code
- ❌ Ghi `.codex/` khi không có `--codex` flag
- ❌ Để FLOW_PROGRESS không cập nhật sau mỗi flow
- ❌ Gen HTML (bỏ hoàn toàn)
- ❌ Module doc thiếu Known Issues section — phải có, kể cả khi chỉ có INFO
- ❌ Files table dùng relative path — phải là full path từ project root
