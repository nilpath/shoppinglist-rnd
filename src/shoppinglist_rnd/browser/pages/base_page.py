from playwright.sync_api import Page, Locator


class BasePage:
    """Base class for all page objects with common functionality."""

    COOKIE_ACCEPT_SELECTORS = [
        'button:has-text("Acceptera")',
        'button:has-text("Godkänn")',
        'button:has-text("Accept")',
        "[data-testid='cookie-accept']",
        "#onetrust-accept-btn-handler",
    ]

    def __init__(self, page: Page):
        self._page = page
        self._cookie_handled = False

    @property
    def page(self) -> Page:
        """Access to underlying Playwright page."""
        return self._page

    def handle_cookie_consent(self) -> bool:
        """
        Dismiss cookie consent banner if present.

        Returns:
            True if consent was handled, False if no banner found.
        """
        if self._cookie_handled:
            return True

        for selector in self.COOKIE_ACCEPT_SELECTORS:
            try:
                button = self._page.locator(selector).first
                if button.is_visible(timeout=2000):
                    button.click()
                    self._cookie_handled = True
                    self._page.wait_for_timeout(500)
                    return True
            except Exception:
                continue

        return False

    def wait_for_page_load(self, timeout: int = 30000) -> None:
        """Wait for page to be fully loaded."""
        self._page.wait_for_load_state("networkidle", timeout=timeout)

    def get_text(self, locator: Locator, timeout: int = 1000) -> str:
        """Safely get text content from a locator."""
        try:
            return locator.text_content(timeout=timeout) or ""
        except Exception:
            return ""

    def is_element_visible(self, selector: str, state: str = "visible", timeout: int = 5000) -> bool:
        """Check if element is visible within timeout."""
        try:
            self._page.wait_for_selector(selector, state=state, timeout=timeout)
            return True
        except Exception:
            return False
