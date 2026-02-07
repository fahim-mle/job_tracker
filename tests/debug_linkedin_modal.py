import argparse
import asyncio

from playwright.async_api import async_playwright


MODAL_SELECTORS = [
    "div#public-sign-in-modal",
    ".contextual-sign-in-modal",
    "div[aria-label='Sign in']",
]

DISMISS_SELECTORS = [
    "button.contextual-sign-in-modal__modal-dismiss",
    "button[aria-label='Dismiss']",
    "button[aria-label='Close']",
    "button:has-text('Dismiss')",
    "button:has-text('Close')",
]


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--wait", type=int, default=3000)
    args = parser.parse_args()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=args.headless)
        page = await browser.new_page()

        try:
            await page.goto(args.url, wait_until="domcontentloaded")
            await page.wait_for_timeout(args.wait)

            modal_found = False
            for selector in MODAL_SELECTORS:
                if await page.locator(selector).count() > 0:
                    modal_found = True
                    break

            modal_closed = False
            if modal_found:
                for selector in DISMISS_SELECTORS:
                    dismiss = page.locator(selector)
                    if await dismiss.count() > 0:
                        await dismiss.first.click(timeout=2000)
                        await page.wait_for_timeout(500)
                        modal_closed = True
                        break
                if not modal_closed:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
                    modal_closed = True

            description_found = await page.locator(
                ".show-more-less-html__markup"
            ).count()
            await page.screenshot(path="debug_modal.png", full_page=True)

            print(f"Modal found: {modal_found}")
            print(f"Modal closed: {modal_closed}")
            print(f"Description found: {description_found > 0}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
