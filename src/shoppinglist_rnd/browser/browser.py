from playwright.sync_api import sync_playwright, Browser as PlaywrightBrowser, BrowserContext, Page

from shoppinglist_rnd.browser.pages.willys_search_page import WillysSearchPage
from shoppinglist_rnd.browser.pages.willys_cart_page import WillysCartPage
from shoppinglist_rnd.models import SearchResult, AddToCartResult


class Browser:
    """Browser manager that provides page objects and DSPy-compatible tool methods."""

    def __init__(self, headless: bool = False):
        self._playwright = sync_playwright().start()
        self._browser: PlaywrightBrowser = self._playwright.chromium.launch(headless=headless)
        self._context: BrowserContext = self._browser.new_context()
        self._page: Page = self._context.new_page()

        self._willys_search_page: WillysSearchPage | None = None
        self._willys_cart_page: WillysCartPage | None = None

    @property
    def page(self) -> Page:
        """Access to the underlying Playwright page."""
        return self._page

    @property
    def willys_search(self) -> WillysSearchPage:
        """Get Willys search page object."""
        if self._willys_search_page is None:
            self._willys_search_page = WillysSearchPage(self._page)
        return self._willys_search_page

    @property
    def willys_cart(self) -> WillysCartPage:
        """Get Willys cart page object."""
        if self._willys_cart_page is None:
            self._willys_cart_page = WillysCartPage(self._page)
        return self._willys_cart_page

    def goto(self, url: str) -> None:
        """Navigate to a URL."""
        self._page.goto(url)

    def close(self) -> None:
        """Close browser and cleanup resources."""
        self._browser.close()
        self._playwright.stop()

    def wait_for_close(self) -> None:
        """Block until the browser is closed by the user."""
        try:
            self._page.wait_for_event("close", timeout=0)
        except Exception:
            pass  # Browser/page already closed

    # =========================================================================
    # DSPy Tool Methods
    # These methods are designed to be used as tools in dspy.ReAct
    # =========================================================================

    def search_willys(self, query: str) -> str:
        """
        Search for products on Willys.se.

        Args:
            query: Search term (e.g., "mjölk", "ägg", "bröd")

        Returns:
            String with search results including product names and prices.
        """
        self.willys_search.navigate()
        result: SearchResult = self.willys_search.search(query)

        if not result.products:
            return f"No products found for '{query}'"

        output_lines = [f"Found {result.total_count} products for '{query}':"]
        for i, product in enumerate(result.products[:10], 1):
            line = f"{i}. {product.name} - {product.price} kr"
            if product.unit_price:
                line += f" ({product.unit_price})"
            output_lines.append(line)

        return "\n".join(output_lines)

    def add_product_to_cart(self, product_name: str, quantity: int = 1) -> str:
        """
        Add a product to the Willys shopping cart.

        Args:
            product_name: Name of the product to add (must match a product from search results)
            quantity: Number of items to add (default 1)

        Returns:
            String describing whether the operation succeeded or failed.
        """
        result: AddToCartResult = self.willys_search.add_to_cart(product_name, quantity)
        return result.message

    def change_product_quantity(self, product_name: str, quantity: int) -> str:
        """
        Change the quantity of a product before adding to cart.

        Args:
            product_name: Name of the product to modify
            quantity: New quantity (must be >= 1)

        Returns:
            String describing whether the operation succeeded or failed.
        """
        success = self.willys_search.change_quantity(product_name, quantity)
        if success:
            return f"Changed quantity of '{product_name}' to {quantity}"
        return f"Failed to change quantity for '{product_name}'"

    def go_to_cart(self) -> str:
        """
        Navigate to the Willys shopping cart page.

        Returns:
            String confirming navigation to cart.
        """
        self.willys_cart.navigate()
        return "Navigated to shopping cart at https://www.willys.se/varukorg"

    def get_tools(self) -> list:
        """
        Get list of browser methods as DSPy tools.

        Returns:
            List of callable methods suitable for dspy.ReAct tools parameter.
        """
        return [
            self.search_willys,
            self.add_product_to_cart,
            self.change_product_quantity,
            self.go_to_cart,
        ]
