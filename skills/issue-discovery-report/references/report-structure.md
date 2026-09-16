# Report Structure Reference

Hướng dẫn chi tiết format, styling, và cách viết từng section của Issue Discovery Report.

## Table of Contents

1. [Styling Constants](#styling-constants)
2. [Component Helpers](#component-helpers)
3. [Section Details](#section-details)
4. [Writing Guidelines](#writing-guidelines)

---

## Styling Constants

### Colors

```javascript
const COLORS = {
  // Primary
  PRIMARY: "1A5276",       // Dark blue - headings, labels
  ACCENT: "2E86C1",        // Medium blue - borders, dividers
  
  // Status
  OK: "27AE60",            // Green - correct, approved
  ERROR: "C0392B",         // Dark red - wrong, critical
  WARNING: "E67E22",       // Orange - caution, major
  INFO: "2E86C1",          // Blue - minor, info
  PURPLE: "8E44AD",        // Purple - suggestion, backlog
  
  // Text
  TEXT: "333333",           // Main text
  SUBTEXT: "555555",       // Secondary text
  MUTED: "888888",         // Muted/placeholder text
  PLACEHOLDER: "999999",   // Very muted
  
  // Backgrounds
  HEADER_BG: "1A5276",     // Table header background
  LABEL_BG: "EBF5FB",      // Label cell background
  HIGHLIGHT_WARN: "FEF9E7", // Warning highlight box
  HIGHLIGHT_ERR: "FDEDEC",  // Error highlight box
  HIGHLIGHT_INFO: "EBF5FB", // Info highlight box
  CODE_BG: "F4F6F7",       // Code block background
};
```

### Fonts & Sizes

```javascript
const FONTS = {
  MAIN: "Arial",
  CODE: "Courier New",
};

const SIZES = {
  TITLE: 36,        // Report title
  SECTION: 26,      // Section headings
  SUBSECTION: 22,   // Sub-headings
  BODY: 20,         // Normal text (10pt)
  SMALL: 18,        // Small text, table cells
  TINY: 16,         // Header/footer
  CODE: 18,         // Code blocks
};
```

### Page Setup

```javascript
const PAGE = {
  WIDTH: 12240,      // US Letter
  HEIGHT: 15840,
  MARGIN_TOP: 1200,
  MARGIN_BOTTOM: 1200,
  MARGIN_LEFT: 1440,
  MARGIN_RIGHT: 1440,
  CONTENT_WIDTH: 9360, // WIDTH - LEFT - RIGHT
};
```

### Borders

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const hdrBorder = { style: BorderStyle.SINGLE, size: 1, color: COLORS.PRIMARY };
const hdrBorders = { top: hdrBorder, bottom: hdrBorder, left: hdrBorder, right: hdrBorder };

const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };
```

---

## Component Helpers

Các function helper cần có trong mỗi report generator script:

### Header Cell (cho table header)

```javascript
function hCell(text, width) {
  return new TableCell({
    borders: hdrBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLORS.HEADER_BG, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text, bold: true, color: "FFFFFF", font: FONTS.MAIN, size: SIZES.BODY
      })]
    })]
  });
}
```

### Normal Cell

```javascript
function c(text, width, opts = {}) {
  return new TableCell({
    borders: opts.borders || borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({
        text, font: opts.font || FONTS.MAIN, size: opts.size || SIZES.BODY,
        bold: opts.bold || false, color: opts.color || COLORS.TEXT,
        italics: opts.italics || false
      })]
    })]
  });
}
```

### Multi-run Cell (nhiều TextRun trong 1 cell)

```javascript
function cMulti(runs, width, opts = {}) {
  return new TableCell({
    borders: opts.borders || borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: runs
    })]
  });
}
```

### Label-Value Row (cho info tables)

```javascript
function labelRow(label, value, lw = 2400, vw = 6960) {
  return new TableRow({ children: [
    new TableCell({
      borders, width: { size: lw, type: WidthType.DXA },
      shading: { fill: COLORS.LABEL_BG, type: ShadingType.CLEAR },
      margins: cellMargins,
      children: [new Paragraph({
        children: [new TextRun({
          text: label, bold: true, font: FONTS.MAIN, size: SIZES.BODY, color: COLORS.PRIMARY
        })]
      })]
    }),
    new TableCell({
      borders, width: { size: vw, type: WidthType.DXA },
      margins: cellMargins,
      children: [new Paragraph({
        children: [new TextRun({
          text: value, font: FONTS.MAIN, size: SIZES.BODY, color: COLORS.TEXT
        })]
      })]
    })
  ]});
}
```

### Section Title

```javascript
function sTitle(text) {
  return new Paragraph({
    spacing: { before: 300, after: 150 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: COLORS.ACCENT, space: 4 } },
    children: [new TextRun({
      text, bold: true, font: FONTS.MAIN, size: SIZES.SECTION, color: COLORS.PRIMARY
    })]
  });
}
```

### Paragraph helpers

```javascript
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.before || 0, after: opts.after || 80 },
    children: [new TextRun({
      text, font: FONTS.MAIN, size: opts.size || SIZES.BODY,
      color: opts.color || COLORS.TEXT, bold: opts.bold || false,
      italics: opts.italics || false
    })]
  });
}

function pMulti(runs, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.before || 0, after: opts.after || 80 },
    children: runs
  });
}
```

### Code Block (pseudocode)

```javascript
function code(text) {
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    shading: { fill: COLORS.CODE_BG, type: ShadingType.CLEAR },
    indent: { left: 360 },
    children: [new TextRun({
      text, font: FONTS.CODE, size: SIZES.CODE, color: "2C3E50"
    })]
  });
}
```

### Highlight Box (cho thông tin quan trọng)

```javascript
// type: "error" | "warning" | "info"
function highlightBox(runs, type = "warning") {
  const config = {
    error:   { fill: COLORS.HIGHLIGHT_ERR,  border: COLORS.ERROR },
    warning: { fill: COLORS.HIGHLIGHT_WARN, border: COLORS.WARNING },
    info:    { fill: COLORS.HIGHLIGHT_INFO,  border: COLORS.ACCENT },
  }[type];
  const bdr = { style: BorderStyle.SINGLE, size: 2, color: config.border };
  return new Table({
    width: { size: PAGE.CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [PAGE.CONTENT_WIDTH],
    rows: [new TableRow({ children: [
      new TableCell({
        borders: { top: bdr, bottom: bdr, left: bdr, right: bdr },
        width: { size: PAGE.CONTENT_WIDTH, type: WidthType.DXA },
        shading: { fill: config.fill, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 200, right: 200 },
        children: [new Paragraph({ children: runs })]
      })
    ]})]
  });
}
```

### Bullet Items

```javascript
// Cần khai báo numbering config trong Document:
// numbering: { config: [{
//   reference: "bullets",
//   levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
//     alignment: AlignmentType.LEFT,
//     style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
// }] }

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, font: FONTS.MAIN, size: SIZES.BODY, color: COLORS.TEXT })]
  });
}

function bulletBold(boldText, normalText) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [
      new TextRun({ text: boldText, font: FONTS.MAIN, size: SIZES.BODY, color: COLORS.PRIMARY, bold: true }),
      new TextRun({ text: normalText, font: FONTS.MAIN, size: SIZES.BODY, color: COLORS.TEXT }),
    ]
  });
}
```

---

## Section Details

### Section 1: Thông tin cơ bản

Dùng `labelRow` table với các field:
- Report ID: `BDR-YYYY-NNN`
- Ngày phát hiện: `DD/MM/YYYY`
- Người báo cáo: Tên + role + team
- Module/Service: Tên module cụ thể
- Môi trường: DEV / STG / PRD
- Severity: Critical / Major / Minor / Suggestion

### Section 2: Tóm tắt vấn đề

**Bắt đầu bằng highlight box** tóm tắt vấn đề cốt lõi trong 2-3 câu. Đây là phần
quan trọng nhất — người đọc phải hiểu vấn đề chỉ từ đoạn này.

Tiếp theo: bảng minh họa bằng số liệu cụ thể (nếu có), rồi liệt kê expected vs actual
dùng bullet points với bold label.

### Section 3: Background/Giải thích

**Viết cho BA đọc.** Giải thích khái niệm kỹ thuật bằng ngôn ngữ đơn giản.
Dùng bảng ví dụ cụ thể thay vì chỉ nói lý thuyết.

Ví dụ: Thay vì nói "swap file = virtual memory backing store", nói
"Khi tạo VM với 2GB RAM, VMware tự động tạo thêm 1 file 2GB trên ổ đĩa để dự phòng."

### Section 4: Phân tích chi tiết

Dùng bảng so sánh cũ vs mới với color code:
- Đỏ (`COLORS.ERROR`) = hiện tại / sai
- Xanh (`COLORS.OK`) = đề xuất / đúng
- Cam (`COLORS.WARNING`) = cần lưu ý

Liệt kê từng vấn đề con với heading riêng (dùng bold paragraph, không dùng HeadingLevel).

### Section 5: Edge case

Trình bày scenario cụ thể:
1. Bảng số liệu minh họa tình huống
2. Mô tả kết quả: chuyện gì xảy ra
3. Tại sao đây là vấn đề

### Section 6: Đề xuất giải pháp

Tách theo hướng giải quyết, mỗi hướng là 1 sub-section:
- **A. Backend**: Sửa logic, công thức, API
- **B. Frontend/UX**: Warning, error message, UI improvement
- **C. Infra/Platform**: Thay đổi cấu hình, infrastructure
- **D. Các platform khác**: Nếu issue ảnh hưởng nhiều platform

Mỗi hướng có bảng chi tiết hoặc bullet points cụ thể.

### Section 7: Bảng tóm tắt logic

Quick reference table cho Dev. Columns: Action | Check gì | Công thức | Lưu ý.
Dùng Courier New cho công thức, color code cho lưu ý quan trọng.

**Bỏ section này nếu issue không liên quan đến logic/công thức.**

### Section 8: Đánh giá ảnh hưởng

Dùng `labelRow` table:
- Ảnh hưởng user: Ai bị ảnh hưởng, bao nhiêu user
- Tần suất: Luôn / Thỉnh thoảng / Hiếm khi
- Workaround: Có cách tạm không
- Liên quan đến: Các module/ticket/flow khác
- Platform: VMware / OpenStack / cả hai

### Section 9: Data source

Cho Dev tham khảo:
- API endpoint
- Bảng field reference (field name + ý nghĩa)
- Lưu ý về giả định (VD: default storage profile)

**Bỏ section này nếu issue không liên quan đến API/data.**

### Section 10: Action Items

**Section quan trọng nhất để chuyển sang Jira.** Bảng columns:
- #: Số thứ tự
- Action: Mô tả cụ thể việc cần làm
- Owner: Dev / Frontend / BA / Infra / Lead
- Platform: VMware / OSP / cả hai
- Priority: Cao (đỏ) / Trung bình (cam) / Cần thảo luận (tím)

### Section 11: Review & Quyết định

Dùng `labelRow` table, để trống cho reviewer điền:
- Trạng thái: Pending Review (default)
- Người review
- Ngày review
- Ghi chú review
- Jira Ticket(s)

---

## Writing Guidelines

### Ngôn ngữ

- Viết bằng tiếng Việt (trừ technical terms giữ nguyên tiếng Anh)
- Câu ngắn, rõ ràng, tránh câu dài quá 2 dòng
- Dùng "chúng ta", "hệ thống" thay vì "tôi", "em"

### Code trong report

- CHỈ dùng pseudocode 1-2 dòng mỗi case
- KHÔNG paste full function/implementation
- Dùng ký hiệu toán học: `≤`, `→`, `≥` thay vì `<=`, `->`, `>=`
- Ví dụ tốt: `if cpu_delta > (cpuLimit - cpuUsed) → REJECT`
- Ví dụ xấu: paste cả function validate_resize() 50 dòng

### Bảng

- Luôn dùng `WidthType.DXA`, KHÔNG dùng percentage
- Tổng columnWidths phải bằng `PAGE.CONTENT_WIDTH` (9360)
- Cell width phải match columnWidths
- Header row dùng `hCell()`, data row dùng `c()`

### Document structure

```javascript
const doc = new Document({
  styles: { default: { document: { run: { font: FONTS.MAIN, size: 22 } } } },
  numbering: { config: [/* bullets config */] },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE.WIDTH, height: PAGE.HEIGHT },
        margin: {
          top: PAGE.MARGIN_TOP, right: PAGE.MARGIN_RIGHT,
          bottom: PAGE.MARGIN_BOTTOM, left: PAGE.MARGIN_LEFT
        }
      }
    },
    headers: { default: new Header({ children: [/* FPT Smart Cloud — Issue Discovery Report | BDR-ID */] }) },
    footers: { default: new Footer({ children: [/* Page X */] }) },
    children: [/* all sections */]
  }]
});
```

### Adaptive sections

Không phải report nào cũng cần đủ 11 sections. Tùy theo loại issue:

| Loại issue | Sections bắt buộc | Sections tùy chọn |
|-----------|-------------------|-------------------|
| Bug logic/công thức | 1-6, 7, 8, 10, 11 | 9 (nếu có API) |
| Missing case / edge case | 1-5, 6, 8, 10, 11 | 7 (nếu có logic), 9 |
| UI/UX issue | 1-2, 4, 6, 8, 10, 11 | 3, 5, 7, 9 |
| Security/permission issue | 1-6, 8, 9, 10, 11 | 7 |
| Suggestion/improvement | 1-2, 6, 8, 10, 11 | 3-5, 7, 9 |

Khi bỏ section, đánh lại số thứ tự cho liên tục.
