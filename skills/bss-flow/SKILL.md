---
name: bss-flow
description: >
  Luồng chuẩn từ dấu hiệu lỗi đến MR đã có tài liệu cho BSS portal — observability → định vị code →
  verify → fix → MR → wiki/BDR/KB → xác minh sau deploy. Dùng khi user đưa một trace SigNoz, một issue
  Sentry, một ticket ISD, một alert, hoặc chỉ mô tả triệu chứng ("VM không có SG", "API trả 500",
  "khách báo mất firewall rule") và muốn đi tới tận cùng chứ không chỉ đọc log. Cũng dùng khi user nói
  "điều tra vụ này", "trace cái này xem sao", "fix rồi tạo MR luôn", "làm nốt tài liệu".
  Trigger - /bss-flow, "điều tra", "trace rồi fix".
---

# BSS Flow — từ triệu chứng đến MR có tài liệu

Skill này là **cái khung**, không phải cái thay thế. Mỗi bước gọi tiếp skill lẻ tương ứng
(`/watcher`, `/signoz-trace`, `/grafana`, `/mr-description`, `/mr-review-doc`,
`/issue-discovery-report`, `/isd-kb`) — các skill đó dùng riêng vẫn chạy độc lập được.

Giá trị nằm ở **các cổng chặn (gate)** giữa các bước. Mỗi gate dưới đây sinh ra từ một lần hỏng thật.
Bỏ gate là lặp lại đúng lỗi cũ.

```
  ISD ticket ─┐
  Sentry     ─┼─► 1.CHỨNG CỨ ─► 2.ĐỊNH VỊ ─► 3.TRACE ─► [3 GATE] ─► 4.FIX ─► 5.LINT+TEST
  SigNoz     ─┤                    ▲                                              │
  Alert/mô tả ┘                    └────── chưa đủ bằng chứng thì quay lại ────────┤
                                                                                  ▼
              9.SAU DEPLOY ◄─ 8.TÀI LIỆU ◄─ 7.MR + DESCRIPTION ◄─ 6.ĐÚNG BRANCH ◄─┘
```

---

## 1. Thu chứng cứ — chọn đúng công cụ theo câu hỏi

Đừng mở cả ba. Mỗi nguồn trả lời một loại câu hỏi khác nhau:

| Cần biết | Công cụ | Ghi chú |
|---|---|---|
| Stacktrace, payload thật, user nào, IP thật | `/watcher` (Sentry) | XFF/Userid chỉ có ở Sentry, retention 30 ngày |
| Luồng đi qua service nào, chậm ở span nào, lỗi phát sinh ở đâu | `/signoz-trace <trace_id>` | Ground truth của "chậm" nằm ở traces, không phải dashboard đếm log |
| CPU/RAM/pod/MySQL/Kong, alert đang firing | `/grafana` | Dùng khi nghi hạ tầng chứ không phải code |
| Trạng thái nghiệp vụ, khách báo gì, ai đang giữ ticket | MCP `servicedesk-fci` | |
| Dữ liệu thật trong DB portal | Query trực tiếp | Dùng để **chứng minh**, không phải để đoán |

**Gate 1 — verify time window.** Trước khi kết luận "không có log", xác nhận cửa sổ thời gian có
phủ đúng trace. Đã từng phải rút lại kết luận vì quét sai khung giờ. Với SigNoz: `groupBy` là bắt
buộc, field thưa trong groupBy làm rớt kết quả âm thầm.

**Gate 2 — chưa có data/trace thật thì chưa được gọi là "root cause".** Nêu giả thuyết thì nói rõ
là giả thuyết. Bẫy hay gặp: 10 tenant ID trùng nhau trong `IN (...)` vẫn chỉ trả 1 dòng — đừng vội
kết luận "chỉ có 1 tenant bị".

---

## 2. Định vị code

Bốn repo hay phải mở cùng lúc: BE chính, FE người dùng, và hai repo dùng chung
(model/shared + client hạ tầng) nằm trên `PYTHONPATH` chứ không phải package cài sẵn — grep thiếu
hai repo này là tưởng hàm không tồn tại.

Project ID GitLab tra bằng API, token đọc từ file riêng ngoài repo (`~/.gl_token` hoặc biến
`$GITLAB_TOKEN`). Dùng GitNexus index để đi call-chain nếu repo đã được index.

**Gate 3 — XÁC NHẬN BRANCH TRƯỚC KHI ĐỌC CODE.** Đây là gate bị vi phạm nhiều nhất:

- `staging-compute` là **DEV**, không phải staging. `staging` mới là staging.
- Hậu tố service tương ứng: `-stg-compute` (dev) vs `-stg` (staging).
- Hai môi trường mang **state khác nhau** → phải grep xác nhận trước khi cherry-pick.
- Controller có cả `v1` lẫn `v2`. Xác nhận version nào đang thực sự phục vụ endpoint đó, đừng mặc
  định bản mới nhất.

Liệt kê đúng endpoint + đúng file + đúng branch rồi mới bắt đầu phân tích.

---

## 3. Trace trọn call-chain

Đi đủ `task → controller → manager → boundary`, **gồm cả những gì method gọi ngầm bên trong**.

Ví dụ thật: một controller apply security group tự gọi luôn bước sync ở bên trong thân hàm — đó mới
là chỗ ngốn gần hết thời gian, không phải lệnh sync nhìn thấy ở task-level. Tối ưu lệnh sync ở
task-level là sửa nhầm chỗ, đo lại vẫn chậm y nguyên.

Với mỗi bước định đụng vào, tự hỏi:
- Bước này tồn tại để làm gì?
- Bỏ hoặc đổi thứ tự nó thì vỡ invariant nào?

Cấu trúc hiện tại **có thể là cố ý theo design**. Ví dụ sync-sau-apply tồn tại để DB phản ánh kết quả
thật và set `ACTIVE`/`ERROR`. Đừng đảo thứ tự chỉ vì đọc bề mặt thấy "thừa". Xác nhận bằng đọc code.

---

## 4. Ba gate bắt buộc trước khi chốt fix

### Gate A — Dual-platform OSP vs VMW
Bắt buộc khi fix đụng: gọi infra API, dùng SDK, boundary, sync, task.

- Boundary/method khác nhau theo platform; nhiều method **no-op hoặc rẽ nhánh** theo platform
  (vd hàm sync-một-phần no-op với platform B → phải fallback full sync, nếu không thì im lặng không sync gì).
- Verify return type / param / signature SDK **đúng cho từng platform**: sai arity, truyền nhầm param,
  `.id` trên `None`, endpoint khác nhau.
- Đã gây incident thật vì chỉ test một platform. Đọc code **cả hai nhánh** rồi mới sửa.

### Gate B — Đổi GIÁ TRỊ dữ liệu (type, enum, status, classification, schema)
Trước khi đổi một giá trị, liệt kê **mọi nơi đọc/diễn giải** giá trị đó, cả BE lẫn FE:

- **FE** hay gate action / filter / sort theo giá trị đó (nút chỉ hiện khi `type == LOCAL`). Đổi giá
  trị BE ghi ra có thể ẩn nút hoặc lệch filter mà nhìn ở BE không thấy gì.
- **BE khác** cũng query riêng giá trị đó: billing, quota, terraform, reconcile, sync. Phân biệt
  consumer đọc từ **cột DB** (bị ảnh hưởng) với consumer tính lại từ **hạ tầng** (không ảnh hưởng).
- Từng relabel giá trị type của một loại tài nguyên chỉ nhìn phía ghi → FE mất nút thao tác và lệch
  bộ lọc, vì FE gate action theo đúng giá trị đó.

### Gate C — Đổi LIFECYCLE/timing/nullability (tạo row sớm hơn, pre-insert cột NULL, đổi thứ tự ghi)
Đổi **khi nào / hình dạng** producer ghi data là mở ra **trạng thái transient mới**
(row tồn tại nhưng field NULL, `CREATING`, chưa sync). Reader cũ giả định invariant cũ sẽ vỡ.

Reader thiếu guard là code cũ của họ, **nhưng regression vẫn tính là của mình** vì sửa producer làm
nó lộ ra. Grep mọi reader và verify nó sống sót ở trạng thái transient, không chỉ trạng thái cuối.

Các shape lỗi hay gặp:
- chained access `None.attr` → `AttributeError`
- `str(None)` → chuỗi rác `"None"`, không crash nhưng sai data
- pydantic field bắt buộc nhận `None` → `ValidationError`
- row NULL lọt vào outer-join (inner-join thì lọc mất nó)
- required-field `name` fallback thiếu `or ""`

Fix thường nằm ở phía **consumer** (thêm null-guard) chứ không đảo design producer, nếu
NULL-cho-tới-khi-sync là chủ đích. Guard mới phải là điều kiện **luôn đúng** ở mọi input mà code cũ
không crash → trạng thái bình thường output y hệt.

### Gate D (khi thêm writer vào cột đã có writer khác) — copy đúng format canonical
Đừng nhớ datamodel, **hãy grep**. Trước khi ghi vào cột đã có path khác ghi (sync, boundary platform
khác, cron reconcile), grep mọi writer + reader của **đúng cột đó**:

- Convention repo: mỗi bảng có **cặp id** — `id` là PK nội bộ (`UUIDType()`, lưu binary) vs
  `<entity>_id` là id hạ tầng (`String`). Xác định đúng cột, đừng đoán theo tên.
- Format id hạ tầng khác nhau theo platform và **chỉ giữ bằng convention, không có constraint**:
  OSP dùng `uuid.UUID(x).hex` (không gạch), VMW dùng urn `urn:vcloud:...`. Copy từ writer sẵn có.
- Check reader match kiểu gì: `== / in_ / notin_` (exact string → **miss âm thầm**) vs bọc
  `uuid.UUID()` (tha cả hai dạng → bug ẩn, chạy đúng nên không ai phát hiện).
- Hậu quả lệch format là **im lặng**: `notin_` coi row là "đã xoá trên infra" → soft-delete oan;
  lookup miss → sync INSERT row trùng; activity log gắn thiếu resource.

---

## 5. Viết code

- **Bám đúng scope.** Không sửa bug không liên quan, không đổi behavior kèm theo. Thấy vấn đề ngoài
  scope thì ghi lại và sinh BDR ở bước 8, đừng sửa lẫn vào MR này.
- **Comment tối đa 1 dòng**, chỉ cho chỗ thực sự khó, nội dung là **WHY** chứ không mô tả lại code.
  Cần 2 dòng nghĩa là chưa chắt — viết lại hoặc bỏ. Docstring cũng 1 dòng.
- Bối cảnh, số liệu, lịch sử bug thuộc về **commit message / MR description**, không phải trong code.

## 6. Lint + test trước khi push

```bash
# BE — portal-api
black --version          # phải là 22.3.0
flake8 --version         # phải là 3.9.2 (Python 3.9)
source .venv/bin/activate
PYTHONPATH=../portal-api-core:../fptcloud-api pytest

# FE — portal-ui
NODE_ENV=test npx jest   # THIẾU NODE_ENV=test sẽ fail giả hàng loạt
```

Sai version black là fail lint CI dù code đúng. Luôn chạy test khi vừa resolve conflict.

**Gate E — đúng branch trước mọi commit/revert/cherry-pick:**
```bash
git branch --show-current
```
Đã từng commit nhầm branch. Với `merge --squash` cẩn thận bị kéo commit lạ từ master vào staging.

## 7. Tạo MR + description

Gọi `/mr-description`. Cấu trúc chuẩn:
vì sao (N bug/gap gốc) → sơ đồ data-flow → thay đổi theo mảng → API/luồng bị ảnh hưởng →
**dual-platform OSP vs VMW** (bắt buộc nếu đụng infra/boundary) → bảng test case (mới / xoá kèm lý do /
phủ theo rủi ro) → lưu ý review.

Số liệu test thì đếm bằng script so set `def test_\w+` giữa `origin/master:<path>` và `<branch>:<path>`,
đừng đếm tay.

## 8. Tài liệu (tuỳ việc, không phải lúc nào cũng cần)

| Tình huống | Skill |
|---|---|
| Cần trang review cho người ngoài đọc hiểu | `/mr-review-doc` → $WIKI_URL |
| Phát hiện bug/missing case **ngoài scope** | `/issue-discovery-report` → BDR `.docx` |
| Việc xuất phát từ ticket ISD | `/isd-kb` → viết KB, gắn link, đẩy ticket Resolve → KB Update → W/A for KB → W/A FOR CLOSE |

Confluence `$WIKI_URL`: MCP write đang hỏng → dùng `PUT` REST, convert markdown sang storage format,
escape placeholder dạng `<...>`, validate XHTML trước khi đẩy. Diagram thì embed PNG qua REST, đừng
dùng mermaid macro hay upload attachment qua MCP (hay fail render).

## 9. Sau deploy — verify đủ mọi nơi

Một fix chỉ có hiệu lực ở process đã deploy. Cùng một hàm thường chạy ở nhiều deployable.

- Xác định code vừa sửa chạy **in-process** (API pod) hay **enqueue task** chạy ở **worker nào**.
  Endpoint khác nhau có thể đi process khác nhau cho cùng một logic.
- Celery task chạy ở service worker riêng (Consumer spans), **không** ở service API — tìm span ở
  đúng service, đừng tìm ở API rồi kết luận "không có log".
- Triệu chứng deploy thiếu: đường này đã fix, đường kia vẫn lỗi (sync in-process ra đúng, sync async ở
  worker chưa deploy vẫn ra sai) → dễ tưởng nhầm còn bug code. Cảnh giác rolling-deploy, pod cũ/mới lẫn lộn.

---

## Checklist rút gọn

```
[ ] Time window phủ đúng trace, chưa kết luận "không có log" quá sớm
[ ] Có data/trace thật rồi mới gọi là root cause
[ ] Đúng branch (staging-compute = DEV!) + đúng version controller v1/v2
[ ] Trace trọn call-chain, kể cả method gọi ngầm bên trong
[ ] Gate A: đọc cả nhánh OSP lẫn VMW
[ ] Gate B: grep hết consumer FE + BE nếu đổi giá trị dữ liệu
[ ] Gate C: grep hết reader nếu đổi timing/nullability
[ ] Gate D: copy đúng format canonical nếu ghi vào cột đã có writer khác
[ ] Bám scope, comment tối đa 1 dòng
[ ] black 22.3.0 + flake8 3.9.2 + pytest (FE: NODE_ENV=test)
[ ] git branch --show-current trước khi commit
[ ] MR description đủ mục, có bảng test
[ ] Sau deploy: mọi pod/worker chạy code đó đã lên bản mới
```

## Bẫy đã gặp thật

| Bẫy | Hậu quả |
|---|---|
| Sửa sync ở task-level, bỏ qua sync gọi ngầm trong controller | Fix không có tác dụng, đo lại vẫn chậm |
| Relabel giá trị type chỉ nhìn phía ghi | FE mất nút thao tác, lệch bộ lọc |
| Pre-insert row sớm với cột NULL | Consumer cũ crash `None.attr`, ghi chuỗi `"None"`, ValidationError |
| Ghi id hạ tầng lệch format so với writer sẵn có | Hỏng im lặng, phải mở thêm nhiều MR sửa lại |
| Chỉ test một platform | Sai arity/param → incident |
| Nhầm `staging-compute` là staging | Phân tích sai môi trường, phải redirect |
| Chỉ deploy API pod, quên celery worker | Hành vi không nhất quán giữa hai đường |
