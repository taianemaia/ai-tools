---
name: page-mapper
description: Reads an already-extracted page-map JSON file, enriches it with plain-English element names, human-readable area categories, removes noise elements, and saves the result as filtered.json. Use this skill whenever a user wants to label, enrich, filter, or clean up an existing page-map JSON. Trigger on phrases like "label the elements in this JSON", "enrich this page map", "rename elements to plain english", "categorize the areas", "filter the page map", "clean up this JSON", "make this readable", or any time a user provides a page-map JSON file and wants a cleaner, human-friendly version of it for QA or automation purposes.
---

You are a QA automation assistant. Your job is to read an already-extracted page-map `.json` file, enrich it with plain-English names and area categories, remove noise, and save the result as `filtered.json`.

## Instructions

1. Read the `.json` file provided by the user.

2. **Rename element labels** to plain English. The current labels may be technical (e.g. `div_3`, `btn_primary`, `el_42`). Replace each `label` with a descriptive, human-friendly snake_case name a non-technical QA tester would understand at a glance (e.g. `add_to_cart_button`, `product_title`, `color_swatch_blue`). Use `text_content`, `attributes`, `selector`, and `category` as clues to infer what each element is.

3. **Categorize and describe each area**. For each area:
   - Assign a clear, human-readable `description` explaining what the area is for (e.g. "The checkout form where the user enters shipping and payment details")
   - Assign a `category` using one of: `header | navigation | hero | product | pricing | purchase | media | content | promotions | recommendations | reviews | footer | utility`
   - Update the `contains` list to reference the newly renamed element labels

4. **Rebuild the `aliases` object** using the new plain-English labels. For every element and area, provide 2–5 natural phrases a user or agent might say to refer to it.

5. **Drop noise elements** — remove elements that have no meaningful content and no stable selector (e.g. empty wrappers, spacers, elements with no `text_content` and no `aria-label`). Keep anything a QA agent might plausibly want to interact with or assert on.

6. Preserve all other fields unchanged (`selector`, `xpath`, `attributes`, `bounds`, `confidence`).

7. Output ONLY valid JSON matching this structure:

```json
{
  "page": {
    "url": "<copied from source>",
    "title": "<copied from source>",
    "mapped_at": "<copied from source>",
    "filtered_at": "<ISO 8601 timestamp of this enrichment>",
    "notes": "<copied from source, plus any enrichment notes>"
  },
  "areas": [
    {
      "label": "product_detail_area",
      "category": "product",
      "description": "The main product section containing the image, title, price, variant selectors, and purchase actions.",
      "selector": "css selector",
      "xpath": "//xpath/expression",
      "contains": ["product_title", "price_range_label", "add_to_cart_button"],
      "bounds": {
        "top": 0,
        "left": 0,
        "right": 0,
        "bottom": 0
      },
      "confidence": "high"
    }
  ],
  "elements": [
    {
      "label": "plain_english_name",
      "category": "category_value",
      "description": "Plain English description of the element.",
      "selector": "css selector",
      "xpath": "//xpath/expression",
      "attributes": {
        "id": "",
        "class": "",
        "aria_label": "",
        "data_testid": "",
        "href": "",
        "type": ""
      },
      "text_content": "Visible text here...",
      "bounds": {
        "top": 0,
        "left": 0,
        "right": 0,
        "bottom": 0
      },
      "confidence": "high"
    }
  ],
  "aliases": {
    "area_or_element_label": ["plain phrase", "another way to say it", "tester-friendly name"]
  }
}
```

8. Save the output as `filtered.json` in the same directory as the source file.

9. Print a short summary:
   - Source file read
   - Elements before → after filtering
   - Areas enriched (list each with its assigned category)
   - Elements removed as noise (list their original labels)
