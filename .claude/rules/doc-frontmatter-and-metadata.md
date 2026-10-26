# Rule: frontmatter and content metadata

Every Markdown file under `en/docs/` needs frontmatter. AI systems and search rely on it.

## Required frontmatter fields

- `title` — page title, short enough not to truncate on narrow devices.
- `description` — SEO description of the page, under 158 characters.
- `canonical_url` — the document's canonical URL.
- `md_url` — link to the Markdown version of the document.
- `tags` — a list, so LLMs and agents can relate pages and concepts.
- `author` — "WSO2 API Platform Documentation Team". For more than one, use `authors` with a list.
- `last_updated` — `YYYY-MM-DD`.
- `content_type` — one of `how-to`, `tutorial`, `reference`, `concept`, `explanation`, `troubleshooting`, `faq`, `release-notes`, `changelog`, `quickstart`.

## Multimedia metadata

- Descriptive image file names: `llm-proxy-creation-in-ai-workspace.png`, not `image1.png`.
- Alt text on every image — see `doc-images.md`.
- Transcripts and captions for video and audio.
- Never put information in an image that the surrounding text doesn't also cover.

## Discoverability and reuse

- Keep `en/docs/llms.txt` updated.
- Link to related topics. Don't leave a page isolated, and don't duplicate across pages.
- Reuse section patterns: standard task steps, consistent troubleshooting layouts.
- Audit and update pages regularly.
