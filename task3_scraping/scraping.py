import asyncio
import base64
import json
import httpx
from playwright.async_api import async_playwright
from pathlib import Path

script_dir = Path(__file__).resolve().parent
output_dir = script_dir / "results/"


TARGET_URL = "https://egypt.blsspainglobal.com/Global/CaptchaPublic/GenerateCaptcha?data=4CDiA9odF2%2b%2bsWCkAU8htqZkgDyUa5SR6waINtJfg1ThGb6rPIIpxNjefP9UkAaSp%2fGsNNuJJi5Zt1nbVACkDRusgqfb418%2bScFkcoa1F0I%3d"


async def get_base64_from_url(url):
    """Downloads an image and converts it to a base64 string."""
    try:
        if url.startswith("data:image"):
            return url.split(",", 1)[1]
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        return f"Error: {str(e)}"


async def scrape_images(target_url, page):
    """
    Scrapes images from the target URL in two steps:
    1. Scrape all images as base64 encoded
    2. Scrape only the 9 images visible to humans as base64 encoded

    target_url: The URL of the page to scrape
    """
    # Step 1: Scrape all images as base64 encoded
    all_images = await page.evaluate("""
        () => {
            const images = Array.from(document.querySelectorAll('img'));
            return images.map(img => ({
                src: img.src,
                alt: img.alt || '',
                width: img.width,
                height: img.height
            }));
        }
    """)

    all_images_base64 = []
    for img in all_images:
        base64_str = await get_base64_from_url(img["src"])
        all_images_base64.append(
            {
                "src": img["src"],
                "alt": img["alt"],
                "width": img["width"],
                "height": img["height"],
                "base64": base64_str,
            }
        )

    with open(output_dir / "allimages.json", "w") as f:
        json.dump(all_images_base64, f, indent=2)

    # Step 2: Scrape only the 9 images visible to humans
    visible_images = await page.evaluate("""
        () => {
            const images = Array.from(document.querySelectorAll('img'));
            const visibleImages = [];
            
            images.forEach(img => {
                // 1. Check computed style for basic visibility
                const style = window.getComputedStyle(img);
                if (style.display === 'none' || 
                    style.visibility === 'hidden' || 
                    style.opacity === '0') {
                    return;
                }
                
                // 2. Verify with getBoundingClientRect() - must occupy space
                const rect = img.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) {
                    return;
                }
                
                // 3. The "Human Center" Check - is the image actually visible at its center?
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const topElement = document.elementFromPoint(centerX, centerY);
                
                // Check if the topmost element is the image itself or contains it
                if (topElement === img || topElement?.contains(img) || img.contains(topElement)) {
                    const parent = img.parentElement;
                    let zIndex = 0;
                    let left = '';
                    
                    // Get parent div info if exists
                    if (parent && parent.tagName.toLowerCase() === 'div') {
                        const parentStyle = window.getComputedStyle(parent);
                        const zIndexValue = parentStyle.zIndex;
                        zIndex = zIndexValue === 'auto' ? 0 : parseInt(zIndexValue) || 0;
                        left = parentStyle.left;
                    }
                    
                    visibleImages.push({
                        src: img.src,
                        alt: img.alt || '',
                        width: img.width,
                        height: img.height,
                        zIndex: zIndex,
                        left: left
                    });
                }
            });
            
            return visibleImages;
        }
    """)

    visible_images_base64 = []
    for img in visible_images:
        base64_str = await get_base64_from_url(img["src"])
        visible_images_base64.append(
            {
                "src": img["src"],
                "alt": img["alt"],
                "width": img["width"],
                "height": img["height"],
                "zIndex": img["zIndex"],
                "base64": base64_str,
            }
        )

    with open(output_dir / "visible_images_only.json", "w") as f:
        json.dump(visible_images_base64, f, indent=2)

    print(f"Scraped {len(all_images_base64)} total images")
    print(f"Scraped {len(visible_images_base64)} visible images")


async def scrape_text(target_url, page):
    """
    Scrapes all human visible text content.

    target_url: The URL of the page to scrape
    """
    # Scrape all human visible text content
    visible_text = await page.evaluate("""
        () => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
            const visibleTexts = [];
            
            while (walker.nextNode()) {
                const node = walker.currentNode;
                const text = node.textContent.trim();
                
                // Skip empty text
                if (text === '') {
                    continue;
                }
                
                const parent = node.parentElement;
                if (!parent) {
                    continue;
                }
                
                // 1. Basic visibility check
                const style = window.getComputedStyle(parent);
                if (style.display === 'none' || 
                    style.visibility === 'hidden' || 
                    style.opacity === '0') {
                    continue;
                }
                
                // 2. Check that element occupies space
                const rect = parent.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) {
                    continue;
                }
                
                // 3. Check that the element is at the top (not hidden behind another element)
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const topElement = document.elementFromPoint(centerX, centerY);
                
                // Verify the top element is the parent or contains it
                if (topElement === parent || topElement?.contains(parent) || parent.contains(topElement)) {
                    visibleTexts.push(text);
                }
            }
            
            return visibleTexts;
        }
    """)

    with open(output_dir / "visible_text.json", "w") as f:
        json.dump(visible_text, f, indent=2)

    print(f"Scraped {len(visible_text)} visible text items")


async def run_scraping(target_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(target_url)
        await page.wait_for_load_state("networkidle")

        # Take a screenshot of the page for reference
        await page.screenshot(path=output_dir / "page_screenshot.png", full_page=True)

        await scrape_images(target_url, page)
        await scrape_text(target_url, page)

        await browser.close()


if __name__ == "__main__":
    output_dir.mkdir(exist_ok=True)
    asyncio.run(run_scraping(TARGET_URL))
