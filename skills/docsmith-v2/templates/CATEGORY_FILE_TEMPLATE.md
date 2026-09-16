# Category File Template (Docusaurus `_category_.json`)

Used by the `categorize` command to render Docusaurus sidebar category labels and order.

## Schema

```json
{
  "label": "<Title from sitemap, normalized>",
  "position": <integer, from sitemap order>,
  "link": {
    "type": "generated-index",
    "description": "<optional one-line summary from sitemap>"
  },
  "collapsible": true,
  "collapsed": false
}
```

## Field reference

| Field         | Required | Source                                   | Notes                                                                |
| ------------- | -------- | ---------------------------------------- | -------------------------------------------------------------------- |
| `label`       | Yes      | Sitemap title for this folder            | Title-case normalized; siblings consistent                           |
| `position`    | Yes      | Sitemap order                            | Integer 1-N within parent. Lower = higher in sidebar                 |
| `link.type`   | Yes      | Constant `generated-index`               | Tells Docusaurus to auto-generate a category landing page            |
| `link.description` | No  | Sitemap one-liner                        | Shown on the auto-generated landing page                             |
| `collapsible` | No       | Constant `true`                          | Allow user to collapse this section                                  |
| `collapsed`   | No       | `false` for top level, `true` for deep   | Initial collapse state                                               |

## Examples

### Top-level category

```json
{
  "label": "Getting Started",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Quick start guides and tutorials for new users"
  },
  "collapsible": true,
  "collapsed": false
}
```

### Nested category

```json
{
  "label": "API Reference",
  "position": 4,
  "link": {
    "type": "generated-index",
    "description": "REST and CLI reference"
  },
  "collapsible": true,
  "collapsed": true
}
```

### Acronym preservation in label

Sitemap title `API Reference` should produce label `API Reference` (NOT `Api Reference`). The categorize command's title normalizer keeps configured acronyms uppercase (default list: `API`, `CLI`, `SQL`, `JSON`, `URL`, `HTTP`, `SSH`, `SSL`, `TLS`, `DNS`, `IP`, `TCP`, `UDP`, `XML`, `HTML`, `CSS`, `JS`, `TS`, `OS`, `IO`, `UI`, `UX`, `ID`).

## What categorize does NOT touch

- Folders not in sitemap (listed in deploy report; user must add to sitemap, exclude in docusaurus.config, or delete)
- Existing `_category_.json` files in folders not in sitemap (left alone)
- `sidebars.js` (use `generate_sidebars: true` opt-in for that)
