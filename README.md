# claude-skills

Bộ skill Claude Code dùng cho việc phát triển BSS portal — từ lúc thấy triệu chứng lỗi đến lúc MR có
đủ tài liệu. Dùng trọn gói theo luồng, hoặc nhặt từng skill lẻ.

## Cài

```bash
git clone https://github.com/dangtran1003/claude-skills.git
cd claude-skills
./install.sh                    # cài tất cả (symlink vào ~/.claude/skills/)
./install.sh bss-flow watcher   # hoặc chỉ vài cái
```

Symlink nên `git pull` là có bản mới, không phải cài lại. Muốn copy hẳn thì `COPY=1 ./install.sh`.

Skill nào cần credential sẽ có `.env.example` — copy sang `.env` rồi điền token **của bạn**:

```bash
cp skills/watcher/.env.example skills/watcher/.env
$EDITOR skills/watcher/.env
```

`.env` đã bị `.gitignore` chặn. Đừng commit.

## Luồng chính

**`/bss-flow`** — cái khung nối mọi thứ lại: observability → định vị code → trace → verify → fix →
MR → tài liệu → xác minh sau deploy.

Phần đáng giá không phải các bước, mà là **các gate giữa các bước**. Mỗi gate sinh ra từ một lần
hỏng thật:

- Xác nhận đúng branch trước khi đọc code — `staging-compute` là **DEV**, `staging` mới là staging
- Trace trọn call-chain kể cả method gọi ngầm bên trong, đừng sửa theo cái nhìn thấy ở task-level
- Check cả OSP lẫn VMW trước khi chốt mọi thay đổi đụng infra/boundary/sync
- Grep hết consumer BE + FE khi đổi giá trị dữ liệu, hoặc đổi timing/nullability của nó
- Copy đúng format canonical khi ghi vào cột đã có writer khác (lệch format hỏng **im lặng**)
- Sau deploy verify mọi pod/worker chạy code đó đã lên bản mới, không chỉ API pod

`CLAUDE.md.example` là bản rút gọn các quy tắc luôn-áp-dụng, copy vào `CLAUDE.md` của repo bạn.

## Danh sách skill

### Điều tra
| Skill | Làm gì | Cần credential |
|---|---|---|
| `bss-flow` | Khung luồng đầy đủ + các gate | — |
| `signoz-trace` | Phân tích 1 trace SigNoz theo ID (full hoặc partial) → bug report | `SIGNOZ_API_KEY` |
| `watcher` | Sentry self-hosted: issue, stacktrace, payload, so sánh tuần | `WATCHER_TOKEN` |
| `grafana` | Dashboard, PromQL, LogQL (Loki), alert đang firing | `GRAFANA_TOKEN` |
| `signoz-weekly` | Quét tuần SigNoz + code pattern, flag regression so tuần trước | `SIGNOZ_API_KEY` |
| `signoz-monthly` | Audit tháng, refresh BDR, tìm bottleneck mới | `SIGNOZ_API_KEY` |

### MR & review
| Skill | Làm gì | Cần credential |
|---|---|---|
| `mr-description` | Description MR chuẩn: vì sao → sơ đồ → thay đổi → API ảnh hưởng → dual-platform → bảng test | GitLab token (`$GITLAB_TOKEN` hoặc `~/.gl_token`) |
| `mr-review-doc` | Trang review cho người ngoài đọc hiểu, publish lên Confluence | `WIKI_USER`/`WIKI_PASS` |
| `review-pr` | Trang HTML review + sơ đồ C4 cho diff hiện tại, chạy offline | — |
| `verify-feature-code` | Đối chiếu tài liệu feature BA với code thật → gap report có mức độ | — |

### Tài liệu
| Skill | Làm gì | Cần credential |
|---|---|---|
| `issue-discovery-report` | Sinh BDR `.docx` 11 mục cho bug/missing case ngoài scope | — |
| `isd-kb` | Ticket ISD → viết KB lên wiki → gắn link → đẩy ticket sang W/A FOR CLOSE | `ISD_TOKEN`, `WIKI_PASS` |
| `codebase-doc` | Scan routes → `docs/ROUTE_LIST.md`, sinh doc module + sequence diagram | — |
| `docsmith-v2` | Pipeline docs đầy đủ: intake → fetch → draft → screenshot → dịch → deploy Docusaurus | tuỳ nguồn |
| `generate-short-video` | Video walkthrough UI ~40s có thuyết minh tiếng Việt (Playwright + gTTS + ffmpeg) | — |

## Dùng lẻ

Mọi skill chạy độc lập được, không bắt buộc đi kèm `bss-flow`. Hai cái hay được dùng riêng nhất là
`/mr-description` và `/review-pr` — chỉ cần repo git, không cần credential gì.

## Repo này đã được lược bỏ gì

Nội dung public không kèm bất kỳ giá trị hạ tầng nào. Đã thay bằng biến môi trường hoặc để trống:

- Hostname, IP và port của SigNoz / Sentry / Grafana / Confluence / Jira / GitLab
- Token, API key, mật khẩu — không file `.env` nào trong repo, `.gitignore` chặn sẵn
- ID trang Confluence, ID project GitLab, UID datasource Grafana
- Đường dẫn máy cá nhân, email, tên tài khoản

Phương pháp, các gate và toàn bộ checklist thì giữ nguyên. Muốn chạy thật thì điền `.env` theo
`.env.example` của từng skill — giá trị nội bộ hỏi người trong team, đừng commit lại lên đây.

## Ghi chú

- Các skill `gitnexus-*` không nằm trong repo này vì đến từ nguồn khác; cài riêng từ marketplace.
- Skill viết bằng tiếng Việt vì team dùng tiếng Việt. Nội dung kỹ thuật (tên hàm, cột, lệnh) giữ nguyên.
