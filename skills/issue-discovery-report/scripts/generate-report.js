/**
 * Issue Discovery Report Generator Template
 *
 * CÁCH DÙNG:
 * 1. Copy file này ra working directory
 * 2. Thay thế tất cả {{PLACEHOLDER}} bằng nội dung thực tế
 * 3. Thêm/bỏ sections tùy loại issue (xem references/report-structure.md)
 * 4. Chạy: node generate-report.js
 * 5. Validate: python <docx-skill>/scripts/office/validate.py <output>.docx
 *
 * PLACEHOLDERS:
 * {{REPORT_ID}}        - VD: BDR-2026-001
 * {{REPORT_DATE}}      - VD: 08/03/2026
 * {{REPORTER_NAME}}    - VD: Dang — Backend Engineer, Compute Engine Team
 * {{MODULE}}           - VD: Compute Engine — VM Resize
 * {{ENVIRONMENT}}      - VD: STG / PRD
 * {{SEVERITY}}         - VD: Major
 * {{SUBTITLE}}         - VD: Quota hao hụt do Swap File
 * {{OUTPUT_FILENAME}}  - VD: BDR-2026-001-swap-quota.docx
 */

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  BorderStyle, WidthType, ShadingType, PageNumber
} = require("docx");

// ======================== CONSTANTS ========================
const C = {
  PRIMARY: "1A5276", ACCENT: "2E86C1",
  OK: "27AE60", ERROR: "C0392B", WARNING: "E67E22", INFO: "2E86C1", PURPLE: "8E44AD",
  TEXT: "333333", SUBTEXT: "555555", MUTED: "888888",
  HEADER_BG: "1A5276", LABEL_BG: "EBF5FB",
  HIGHLIGHT_WARN: "FEF9E7", HIGHLIGHT_ERR: "FDEDEC", HIGHLIGHT_INFO: "EBF5FB",
  CODE_BG: "F4F6F7",
};
const F = { MAIN: "Arial", CODE: "Courier New" };
const S = { TITLE: 36, SECTION: 26, SUB: 22, BODY: 20, SMALL: 18, TINY: 16, CODE: 18 };
const PG = { W: 12240, H: 15840, MT: 1200, MB: 1200, ML: 1440, MR: 1440, CW: 9360 };

// ======================== HELPERS ========================
const bdr = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const bdrs = { top: bdr, bottom: bdr, left: bdr, right: bdr };
const hBdr = { style: BorderStyle.SINGLE, size: 1, color: C.PRIMARY };
const hBdrs = { top: hBdr, bottom: hBdr, left: hBdr, right: hBdr };
const cM = { top: 80, bottom: 80, left: 120, right: 120 };

function hCell(text, w) {
  return new TableCell({ borders: hBdrs, width: { size: w, type: WidthType.DXA },
    shading: { fill: C.HEADER_BG, type: ShadingType.CLEAR }, margins: cM, verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: "FFFFFF", font: F.MAIN, size: S.BODY })] })] });
}

function c(text, w, o = {}) {
  return new TableCell({ borders: o.borders || bdrs, width: { size: w, type: WidthType.DXA },
    shading: o.shading ? { fill: o.shading, type: ShadingType.CLEAR } : undefined, margins: cM,
    children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT,
      children: [new TextRun({ text, font: o.font || F.MAIN, size: o.size || S.BODY,
        bold: o.bold || false, color: o.color || C.TEXT, italics: o.italics || false })] })] });
}

function cMulti(runs, w, o = {}) {
  return new TableCell({ borders: o.borders || bdrs, width: { size: w, type: WidthType.DXA },
    shading: o.shading ? { fill: o.shading, type: ShadingType.CLEAR } : undefined, margins: cM,
    children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT, children: runs })] });
}

function labelRow(label, value, lw = 2400, vw = 6960) {
  return new TableRow({ children: [
    new TableCell({ borders: bdrs, width: { size: lw, type: WidthType.DXA },
      shading: { fill: C.LABEL_BG, type: ShadingType.CLEAR }, margins: cM,
      children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, font: F.MAIN, size: S.BODY, color: C.PRIMARY })] })] }),
    new TableCell({ borders: bdrs, width: { size: vw, type: WidthType.DXA }, margins: cM,
      children: [new Paragraph({ children: [new TextRun({ text: value, font: F.MAIN, size: S.BODY, color: C.TEXT })] })] })
  ]});
}

function sTitle(text) {
  return new Paragraph({ spacing: { before: 300, after: 150 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: C.ACCENT, space: 4 } },
    children: [new TextRun({ text, bold: true, font: F.MAIN, size: S.SECTION, color: C.PRIMARY })] });
}

function p(text, o = {}) {
  return new Paragraph({ spacing: { before: o.before || 0, after: o.after || 80 },
    children: [new TextRun({ text, font: F.MAIN, size: o.size || S.BODY,
      color: o.color || C.TEXT, bold: o.bold || false, italics: o.italics || false })] });
}

function pMulti(runs, o = {}) {
  return new Paragraph({ spacing: { before: o.before || 0, after: o.after || 80 }, children: runs });
}

function code(text) {
  return new Paragraph({ spacing: { before: 40, after: 40 },
    shading: { fill: C.CODE_BG, type: ShadingType.CLEAR }, indent: { left: 360 },
    children: [new TextRun({ text, font: F.CODE, size: S.CODE, color: "2C3E50" })] });
}

function bullet(text) {
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 },
    children: [new TextRun({ text, font: F.MAIN, size: S.BODY, color: C.TEXT })] });
}

function bulletBold(b, n) {
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 },
    children: [
      new TextRun({ text: b, font: F.MAIN, size: S.BODY, color: C.PRIMARY, bold: true }),
      new TextRun({ text: n, font: F.MAIN, size: S.BODY, color: C.TEXT }),
    ] });
}

function gap(s = 60) { return new Paragraph({ spacing: { after: s }, children: [] }); }

function highlightBox(runs, type = "warning") {
  const cfg = { error: { f: C.HIGHLIGHT_ERR, b: C.ERROR }, warning: { f: C.HIGHLIGHT_WARN, b: C.WARNING },
    info: { f: C.HIGHLIGHT_INFO, b: C.ACCENT } }[type];
  const bd = { style: BorderStyle.SINGLE, size: 2, color: cfg.b };
  return new Table({ width: { size: PG.CW, type: WidthType.DXA }, columnWidths: [PG.CW], rows: [
    new TableRow({ children: [new TableCell({
      borders: { top: bd, bottom: bd, left: bd, right: bd },
      width: { size: PG.CW, type: WidthType.DXA },
      shading: { fill: cfg.f, type: ShadingType.CLEAR },
      margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: [new Paragraph({ children: runs })]
    })] })
  ] });
}

// ======================== CONTENT ========================
// Thay thế {{PLACEHOLDERS}} và thêm/bỏ sections theo loại issue.
// Xem references/report-structure.md để biết section nào bắt buộc.

const children = [
  // ===== TITLE =====
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ text: "BUG / ISSUE DISCOVERY REPORT", bold: true, font: F.MAIN, size: S.TITLE, color: C.PRIMARY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ACCENT, space: 8 } },
    children: [new TextRun({ text: "{{SUBTITLE}}", font: F.MAIN, size: S.SUB, color: C.SUBTEXT, italics: true })] }),

  // ===== 1. THÔNG TIN CƠ BẢN =====
  sTitle("1. Th\u00F4ng tin c\u01A1 b\u1EA3n"),
  new Table({ width: { size: PG.CW, type: WidthType.DXA }, columnWidths: [2400, 6960], rows: [
    labelRow("Report ID", "{{REPORT_ID}}"),
    labelRow("Ng\u00E0y ph\u00E1t hi\u1EC7n", "{{REPORT_DATE}}"),
    labelRow("Ng\u01B0\u1EDDi b\u00E1o c\u00E1o", "{{REPORTER_NAME}}"),
    labelRow("Module/Service", "{{MODULE}}"),
    labelRow("M\u00F4i tr\u01B0\u1EDDng", "{{ENVIRONMENT}}"),
    labelRow("Severity", "{{SEVERITY}}"),
  ]}),

  // ===== 2. TÓM TẮT VẤN ĐỀ =====
  sTitle("2. T\u00F3m t\u1EAFt v\u1EA5n \u0111\u1EC1"),

  highlightBox([
    new TextRun({ text: "V\u1EA5n \u0111\u1EC1 c\u1ED1t l\u00F5i: ", bold: true, font: F.MAIN, size: S.SUB, color: C.ERROR }),
    new TextRun({ text: "{{CORE_PROBLEM_SUMMARY}}", font: F.MAIN, size: S.BODY, color: C.TEXT }),
  ], "warning"),

  gap(40),

  // Expected vs Actual
  pMulti([new TextRun({ text: "K\u1EBFt qu\u1EA3 mong \u0111\u1EE3i:", bold: true, font: F.MAIN, size: S.BODY, color: C.PRIMARY })], { after: 40 }),
  // TODO: Thêm bullet points cho expected behavior

  gap(20),
  pMulti([new TextRun({ text: "K\u1EBFt qu\u1EA3 th\u1EF1c t\u1EBF:", bold: true, font: F.MAIN, size: S.BODY, color: C.PRIMARY })], { after: 40 }),
  // TODO: Thêm bullet points cho actual behavior

  // ===== 3. BACKGROUND (cho BA) =====
  // Bỏ section này nếu issue đơn giản, không cần giải thích kỹ thuật
  sTitle("3. Background (gi\u1EA3i th\u00EDch cho BA)"),
  // TODO: Giải thích khái niệm kỹ thuật bằng ngôn ngữ đơn giản + bảng ví dụ

  // ===== 4. PHÂN TÍCH CHI TIẾT =====
  sTitle("4. Ph\u00E2n t\u00EDch chi ti\u1EBFt"),
  // TODO: Bảng so sánh, liệt kê vấn đề con

  // ===== 5. EDGE CASE =====
  // Bỏ nếu không có edge case đáng kể
  sTitle("5. Edge case"),
  // TODO: Scenario + bảng số liệu

  // ===== 6. ĐỀ XUẤT GIẢI PHÁP =====
  sTitle("6. \u0110\u1EC1 xu\u1EA5t gi\u1EA3i ph\u00E1p"),
  // TODO: Tách theo hướng A (Backend), B (Frontend), C (Infra)...

  // ===== 7. BẢNG TÓM TẮT LOGIC =====
  // Bỏ nếu issue không liên quan logic/công thức
  // sTitle("7. Bảng tóm tắt logic"),

  // ===== 8. ĐÁNH GIÁ ẢNH HƯỞNG =====
  sTitle("7. \u0110\u00E1nh gi\u00E1 \u1EA3nh h\u01B0\u1EDFng"),
  new Table({ width: { size: PG.CW, type: WidthType.DXA }, columnWidths: [2400, 6960], rows: [
    labelRow("\u1EA2nh h\u01B0\u1EDFng user", "{{IMPACT_USERS}}"),
    labelRow("T\u1EA7n su\u1EA5t", "{{FREQUENCY}}"),
    labelRow("Workaround", "{{WORKAROUND}}"),
    labelRow("Li\u00EAn quan", "{{RELATED}}"),
  ]}),

  // ===== 9. DATA SOURCE =====
  // Bỏ nếu không liên quan API
  // sTitle("9. Data source (cho Dev)"),

  // ===== 10. ACTION ITEMS =====
  sTitle("8. Action Items"),
  // TODO: Bảng action items với columns: #, Action, Owner, Platform, Priority
  // Ví dụ:
  // new Table({ width: { size: PG.CW, type: WidthType.DXA },
  //   columnWidths: [600, 3200, 1800, 1600, 2160], rows: [
  //   new TableRow({ children: [
  //     hCell("#", 600), hCell("Action", 3200), hCell("Owner", 1800),
  //     hCell("Platform", 1600), hCell("Priority", 2160),
  //   ]}),
  //   new TableRow({ children: [
  //     c("1", 600, { align: AlignmentType.CENTER }),
  //     c("Mô tả action cụ thể", 3200),
  //     c("Dev", 1800, { align: AlignmentType.CENTER }),
  //     c("VMware", 1600, { align: AlignmentType.CENTER }),
  //     c("Cao", 2160, { align: AlignmentType.CENTER, color: C.ERROR, bold: true }),
  //   ]}),
  // ]}),

  // ===== 11. REVIEW & QUYẾT ĐỊNH =====
  sTitle("9. Review & Quy\u1EBFt \u0111\u1ECBnh"),
  new Table({ width: { size: PG.CW, type: WidthType.DXA }, columnWidths: [2400, 6960], rows: [
    labelRow("Tr\u1EA1ng th\u00E1i", "Pending Review"),
    labelRow("Ng\u01B0\u1EDDi review", ""),
    labelRow("Ng\u00E0y review", ""),
    labelRow("Ghi ch\u00FA review", ""),
    labelRow("Jira Ticket(s)", ""),
  ]}),
];

// ======================== BUILD ========================
const doc = new Document({
  styles: { default: { document: { run: { font: F.MAIN, size: 22 } } } },
  numbering: { config: [{
    reference: "bullets",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
  }] },
  sections: [{
    properties: {
      page: { size: { width: PG.W, height: PG.H },
        margin: { top: PG.MT, right: PG.MR, bottom: PG.MB, left: PG.ML } }
    },
    headers: { default: new Header({ children: [
      new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "FPT Smart Cloud \u2014 Issue Discovery Report | {{REPORT_ID}}",
          font: F.MAIN, size: S.TINY, color: C.MUTED, italics: true })] })
    ] }) },
    footers: { default: new Footer({ children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Page ", font: F.MAIN, size: S.TINY, color: C.MUTED }),
        new TextRun({ children: [PageNumber.CURRENT], font: F.MAIN, size: S.TINY, color: C.MUTED }),
      ] })
    ] }) },
    children
  }]
});

const OUTPUT = "/home/claude/{{OUTPUT_FILENAME}}";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT, buffer);
  console.log(`Done! Created: ${OUTPUT}`);
});
