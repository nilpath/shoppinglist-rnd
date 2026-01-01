from playwright.sync_api import Page

from shoppinglist_rnd.browser.pages.base_page import BasePage


class WillysCartPage(BasePage):
    """Page Object Model for Willys.se shopping cart page."""

    URL = "https://www.willys.se/varukorg"

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate(self) -> "WillysCartPage":
        """Navigate to cart page."""
        self._page.goto(self.URL)
        self.wait_for_page_load()
        self.handle_cookie_consent()
        return self
