# Voice Chart

> Part of [PRC-010A: UX Content Standards Subprocess](prc-010a-ux-content-standards-subprocess.md)
> Based on *Strategic Writing for UX* (Podmajersky, 2019), Chapter 2

## Product Information

| Field | Value |
|-------|-------|
| **Product Name** | [Product name] |
| **Target Audience** | [Brief audience description — reference Audience Profile from PRC-010 STEP-001] |
| **Date Created** | [YYYY-MM-DD] |
| **Approved By** | [Name/role] |

## Product Principles

Define 2-4 principles that describe what the experience should be for the people who use it. Principles are qualities, not features.

| # | Principle | Description |
|---|-----------|-------------|
| 1 | [Principle name] | [What this principle means for the user experience] |
| 2 | [Principle name] | [What this principle means for the user experience] |
| 3 | [Principle name] | [What this principle means for the user experience] |

## Voice Chart

|  | [Principle 1] | [Principle 2] | [Principle 3] |
|--|---------------|---------------|---------------|
| **Concepts** | [Ideas/topics to emphasize when opportunity arises] | [Ideas/topics to emphasize] | [Ideas/topics to emphasize] |
| **Vocabulary** | [Word choices, terminology, jargon rules] | [Word choices, terminology] | [Word choices, terminology] |
| **Verbosity** | [How much text: terse, moderate, thorough?] | [How much text?] | [How much text?] |
| **Grammar** | [Sentence structure, tense, person, voice] | [Grammar rules] | [Grammar rules] |
| **Punctuation** | [Punctuation conventions and style] | [Punctuation rules] | [Punctuation rules] |
| **Capitalization** | [Capitalization rules: sentence case, title case, etc.] | [Capitalization rules] | [Capitalization rules] |

## Voice Aspect Definitions

Use this section to elaborate on each aspect when the table cells need more detail.

### Concepts
[Expanded guidance on which themes and ideas should surface throughout the experience, beyond the immediate task at hand.]

### Vocabulary
[Expanded guidance: preferred terms, banned terms, jargon policy, terminology glossary reference.]

### Verbosity
[Expanded guidance: character limits, line count limits, when to be brief vs. thorough.]

### Grammar
[Expanded guidance: active vs. passive voice, person (first/second/third), tense for procedures vs. descriptions, sentence complexity.]

### Punctuation
[Expanded guidance: Oxford comma, exclamation marks, periods in headings/labels, em-dash vs. en-dash, etc.]

### Capitalization
[Expanded guidance: title case rules, sentence case rules, product name capitalization, feature name capitalization.]

## Voice vs. Tone Guidance

Voice is consistent across the entire experience. Tone varies by context. Use this section to define how tone shifts for different situations while staying within the voice.

| Context | Tone Shift | Example |
|---------|-----------|---------|
| **Onboarding / Getting Started** | [e.g., Warm, encouraging] | [Example text] |
| **Error Messages** | [e.g., Calm, solution-focused] | [Example text] |
| **Success / Confirmation** | [e.g., Brief, positive] | [Example text] |
| **Technical / Reference** | [e.g., Precise, neutral] | [Example text] |
| **Warnings / Cautions** | [e.g., Direct, clear] | [Example text] |

## Quick Reference Card

Summarize the voice in one sentence that anyone on the team can remember:

> **"[Product] speaks like [metaphor/role], helping people [goal]."**

For example: *"TAPP speaks like a friendly local who knows every bus route, helping riders get where they're going without hassle."*

---

## FPT Cloud Preset (v1.6.0+)

When project intake has `compliance: fpt-user-guide`, AI generates voice chart using THIS preset instead of the generic template above. This preset directly mirrors [FPT_TEMPLATES.md § Part 5](FPT_TEMPLATES.md) authoritative voice rules.

### Product Principles (FPT)

| # | Principle | Description |
|---|---|---|
| 1 | **Clear (Rõ ràng)** | Clear instructions so reader self-serves without calling support |
| 2 | **Practical (Thực dụng)** | Focus on real value: WHY before HOW, link to business benefit |
| 3 | **Consistent (Nhất quán)** | Same style, pattern throughout — terminology, structure, tone unified |

### Voice Chart Matrix (FPT)

|  | Clear | Practical | Consistent |
|---|---|---|---|
| **Concepts** | Self-service, reduce support dependency | ROI, cost savings, security, risk reduction | Same mental model across modules, familiar UX |
| **Vocabulary** | Concrete, terse words. `Chọn [Action]` not `Thực hiện thao tác [Action]` | Business value: `giảm chi phí X%` not `tối ưu hóa` | Tech terms in EN unchanged (see Vocabulary Guide) |
| **Verbosity** | Terse: 1 sentence/step, max 2 lines | Moderate: intro max 2 sentences explaining WHY, no trailing clauses | Prerequisites thorough, steps terse, callouts 1-2 sentences |
| **Grammar** | Active voice, imperative: `Nhấn [Button]` not `Nút [Button] được nhấn` | Second person: `bạn chọn`, `bạn có thể`. Present tense | Same sentence structure for all procedure steps |
| **Punctuation** | Period at end of each step. NO exclamation marks | Em-dash (—) for short inline explanations | Bullet lists no semicolons at end. Heading sentence case |
| **Capitalization** | Feature/product names follow UI capitalization | Heading sentence case | NO ALL CAPS. NEVER lowercase product names |

### Vocabulary Guide (FPT)

**Technical terms — KEEP English**:
Instance, VPC, Subnet, Floating IP, Snapshot, Load Balancer, Security Group, Container, Pod, Cluster, Namespace, Volume, Bucket, Region, Zone, API, SDK, CLI, Dashboard, Webhook, Token, OAuth, JWT, REST, GraphQL, SSH, HTTPS

**Actions — USE Vietnamese**:
Tạo (Create), Xóa (Delete), Chỉnh sửa (Edit), Lưu (Save), Mở (Open), Đóng (Close), Khởi động (Start), Dừng (Stop), Triển khai (Deploy)

**FPT product names — KEEP unchanged**:
FPT Cloud Console, Cloud Advisor, Cost Explorer, FPT Object Storage, FPT Container Service

### Tone Variants (FPT)

| Context | Tone | Example |
|---|---|---|
| **Onboarding** | Warm, encouraging | `Hãy bắt đầu bằng việc [action] để [benefit].` |
| **Error Messages** | Calm, solution-oriented | `Không thể [action]. Kiểm tra [cause] hoặc liên hệ Admin.` |
| **Success** | Concise, positive | `[Object] đã được [action] thành công.` |
| **Technical Reference** | Precise, neutral | `[Concept] gồm [component A] và [component B].` |
| **Warnings** | Direct, clear consequences | `Khi [action], [consequence]. Hành động không thể hoàn tác.` |

### Quick Reference (FPT)

> **"FPT Cloud docs speak like a senior DevOps engineer who explains things to a colleague — direct, terse, value-oriented, never condescending."**

When `voice` command runs with `compliance: fpt-user-guide`, AI fills audience-specific examples (product name, modules, etc.) into the FPT preset rather than asking user to write a custom voice chart from scratch.
