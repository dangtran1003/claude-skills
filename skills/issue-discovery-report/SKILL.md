---
name: issue-discovery-report
description: >
  Tạo tài liệu Issue Discovery Report (.docx) khi phát hiện bug, missing case,
  hoặc vấn đề nằm ngoài scope trong quá trình phát triển phần mềm. Sử dụng skill này
  khi user muốn tạo report cho bug/issue/lỗi mới phát hiện, viết báo cáo phát hiện lỗi,
  tạo BDR (Bug Discovery Report), document missing case hoặc edge case, tạo report để
  BA/Dev review, hoặc bất kỳ khi nào user đề cập "tạo report lỗi", "phát hiện bug",
  "missing case", "issue report", "BDR", "discovery report". Cũng trigger khi user nói
  "tạo report như template", "report theo format cũ", hoặc muốn document vấn đề kỹ thuật
  để team review.
---

# Issue Discovery Report Generator

## Overview

Skill này tạo file `.docx` chuyên nghiệp theo format Issue Discovery Report, phục vụ
quy trình phát hiện và báo cáo bug/missing case ngoài scope. Report được thiết kế để
cả BA và Dev đều đọc hiểu, có thể đưa lên Confluence để review, approve/reject, và
tạo Jira ticket.

## Khi nào dùng skill này

- Phát hiện bug/lỗi nằm ngoài scope hiện tại
- Phát hiện missing case, edge case chưa được BA cover
- Muốn document vấn đề kỹ thuật để team review
- Tạo evidence cho performance review

## Workflow

### Step 1: Thu thập thông tin từ user

Hỏi user các thông tin sau (bỏ qua những gì đã có trong context):

**Bắt buộc:**
1. **Tóm tắt vấn đề**: Mô tả ngắn gọn bug/issue là gì?
2. **Module/Service**: Thuộc module nào? (VD: Compute Engine, Network, IAM...)
3. **Expected vs Actual**: Hệ thống nên làm gì vs đang làm gì?
4. **Severity**: Critical / Major / Minor / Suggestion

**Tùy chọn (hỏi thêm nếu cần):**
5. Môi trường (DEV/STG/PRD)
6. Steps to reproduce
7. Evidence (screenshot, log, API response)
8. Đánh giá ảnh hưởng (ai bị ảnh hưởng, tần suất, workaround)
9. Đề xuất giải pháp
10. Liên quan đến module/ticket nào khác

### Step 2: Xác định Report ID

Format: `BDR-YYYY-NNN`
- YYYY = năm hiện tại
- NNN = số thứ tự (hỏi user hoặc dùng 001 nếu chưa biết)

### Step 3: Generate Report

Đọc file template tại `scripts/generate-report.js` trong thư mục skill này,
sau đó **tùy chỉnh nội dung** theo thông tin user cung cấp.

```bash
# Install dependency
npm install -g docx

# Copy template ra working directory và sửa nội dung
cp <skill-path>/scripts/generate-report.js /home/claude/generate-report.js
```

Chỉnh sửa file JS với nội dung thực tế, sau đó chạy:

```bash
cd /home/claude && node generate-report.js
python <skill-path>/../../public/docx/scripts/office/validate.py /home/claude/<output-file>.docx
```

### Step 4: Deliver

Copy file sang `/mnt/user-data/outputs/` và dùng `present_files` để gửi cho user.

## Report Structure (11 sections)

Mỗi report PHẢI có đủ các section sau. Đọc `references/report-structure.md` để xem
chi tiết format và hướng dẫn viết từng section.

| # | Section | Ai đọc | Ghi chú |
|---|---------|--------|---------|
| 1 | Thông tin cơ bản | Tất cả | ID, ngày, reporter, module, severity |
| 2 | Tóm tắt vấn đề | Tất cả | Highlight box, expected vs actual |
| 3 | Background/Giải thích | BA | Giải thích kỹ thuật bằng ngôn ngữ đơn giản, bảng ví dụ |
| 4 | Phân tích chi tiết | Dev + BA | So sánh cũ vs mới, bảng color-coded |
| 5 | Edge case | Dev + BA | Scenario cụ thể với số liệu |
| 6 | Đề xuất giải pháp | Tất cả | Tách theo hướng: Backend, Frontend/UX, Infra |
| 7 | Bảng tóm tắt logic | Dev | Quick reference table |
| 8 | Đánh giá ảnh hưởng | BA + Lead | Ảnh hưởng user, tần suất, workaround |
| 9 | Data source | Dev | API endpoint, field reference |
| 10 | Action Items | Tất cả | Bảng action, owner, platform, priority |
| 11 | Review & Quyết định | BA + Lead | Status, reviewer, Jira ticket |

**Nguyên tắc quan trọng:**
- Section 3 (Background) phải viết sao cho BA không có kiến thức kỹ thuật sâu cũng hiểu
- Code example chỉ dùng pseudocode ngắn gọn, KHÔNG paste full implementation
- Dùng bảng và color code (đỏ = sai/nguy hiểm, xanh = đúng/ok, cam = cảnh báo)
- Highlight box cho thông tin quan trọng nhất
- Nếu issue liên quan nhiều platform (VMware, OpenStack...), tách giải pháp theo platform

## Styling Guide

Đọc `references/report-structure.md` phần "Styling Constants" để lấy chính xác
color codes, font sizes, và component helpers dùng trong docx-js.

## Severity Definitions

| Level | Khi nào dùng |
|-------|-------------|
| **Critical** | Mất dữ liệu, sập hệ thống, ảnh hưởng bảo mật, không có workaround |
| **Major** | Chức năng chính bị ảnh hưởng, có workaround nhưng phiền phức |
| **Minor** | Lỗi nhỏ, UI/UX không đúng, edge case ít gặp |
| **Suggestion** | Không phải bug, nhưng có thể cải thiện (missing case, UX improvement) |

## Tips

- Nếu user chỉ mô tả ngắn gọn, vẫn tạo report đầy đủ — điền những gì biết,
  đánh dấu placeholder cho phần chưa có
- Report nên self-contained: người đọc không cần context bên ngoài để hiểu vấn đề
- Luôn có section Action Items với owner rõ ràng — đây là phần quan trọng nhất
  để chuyển từ report sang Jira ticket
- File output đặt tên theo format: `BDR-YYYY-NNN-<short-slug>.docx`
