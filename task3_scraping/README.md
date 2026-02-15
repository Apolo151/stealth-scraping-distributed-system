### DOM Scraping
A web scraper that extracts images and text from a CAPTCHA page using advanced visibility detection.

**Main Tasks:**
1. Scrape all images, convert to base64, save to `allimages.json`
2. Scrape only human-visible images (9), convert to base64, save to `visible_images_only.json`
3. Scrape all human-visible text content, save to `visible_text.json`

### Design
**Three-Layer Visibility Detection** (applied to both images and text):
1. **Computed style checks**: Filter out `display: none`, `visibility: hidden`, `opacity: 0`
2. **getBoundingClientRect() verification**: Ensure elements occupy actual screen space
3. **"Human Center" check**: Use `document.elementFromPoint()` to verify content is truly visible and not occluded

### Implementation Details

**Image Scraping:**
- Step 1: Query all `<img>` elements, convert to base64
- Step 2: Apply three-layer visibility detection, capture parent div metadata (z-index, left position)

**Text Scraping:**
- Use `TreeWalker` to traverse all text nodes in the DOM
- Apply same three-layer visibility detection to parent elements
- Filter out empty/whitespace-only text

**Tools:** Playwright (Chromium), httpx for image downloads

### Output Files
- `allimages.json` - All images with base64 data
- `visible_images_only.json` - Human-visible images (typically 9) with base64 + parent metadata
- `visible_text.json` - All human-visible text content
- `page_screenshot.png` - Full-page reference screenshot