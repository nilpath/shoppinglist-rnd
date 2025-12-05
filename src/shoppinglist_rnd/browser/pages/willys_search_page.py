import re
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout

from shoppinglist_rnd.browser.pages.base_page import BasePage
from shoppinglist_rnd.models import Product, SearchResult, AddToCartResult


class WillysSearchPage(BasePage):
    """Page Object Model for Willys.se search page."""

    URL = "https://www.willys.se/sok"

    # Selectors - using multiple fallbacks for stability
    SEARCH_INPUT = 'input[type="search"], input[placeholder*="Sök"], [data-testid="search-input"]'
    SEARCH_BUTTON = 'button[type="submit"], button:has-text("Sök")'

    # Product listing selectors
    PRODUCT_GRID = 'section > div:nth-child(1) [data-testid="grid"]'
    PRODUCT_CARD = '[data-testid="product"]'
    PRODUCT_NAME = '[itemprop="name"]'
    PRODUCT_PRICE = '[data-testid="product-price-DEFAULT"]'
    PRODUCT_UNIT_PRICE = 'div:nth-of-type(2) > div:nth-of-type(3)'
    PRODUCT_IMAGE = 'img'

    # Quantity controls
    QUANTITY_INPUT = 'input[name="quantity"]'
    QUANTITY_INCREASE = 'button[name="increase"]'
    QUANTITY_DECREASE = 'button[name="decrease"]'

    # Cart
    MINI_CART_BUTTON = 'button[data-testid="mini-cart-button"] > span:not([data-testid="cart-icon"])'
    CART_POPUP_BACKDROP = 'div[data-backdrop="true"]'
    

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate(self) -> "WillysSearchPage":
        """
        Navigate to Willys search page.
        Handles cookie consent automatically.

        Returns:
            Self for method chaining.
        """
        self._page.goto(self.URL)
        self.wait_for_page_load()
        self.handle_cookie_consent()
        return self

    def search(self, query: str) -> SearchResult:
        """
        Search for products on Willys.

        Args:
            query: Search term (e.g., "mjölk", "ägg")

        Returns:
            SearchResult with list of found products.
        """
        self.handle_cookie_consent()

        search_input = self._page.locator(self.SEARCH_INPUT).first
        search_input.wait_for(state="visible")
        search_input.fill(query)
        search_input.press("Enter")

        self._wait_for_search_results(query)

        products = self._extract_products()

        return SearchResult(
            query=query,
            products=products,
            total_count=len(products),
        )

    def _wait_for_cart_update(self, previous_text: str, timeout: int = 5000) -> None:
        """Wait for the mini cart button to change from its previous state."""
        try:
            self._page.locator(self.MINI_CART_BUTTON).wait_for(
                state="visible",
                timeout=timeout,
            )
            self._page.wait_for_function(
                f"document.querySelector('{self.MINI_CART_BUTTON}')?.innerText !== '{previous_text}'",
                timeout=timeout,
            )
        except PlaywrightTimeout:
            pass

    def _get_cart_button_text(self) -> str:
        """Get the current text of the mini cart button."""
        try:
            return self._page.locator(self.MINI_CART_BUTTON).inner_text()
        except Exception:
            return ""

    def _dismiss_cart_popup(self) -> None:
        """Dismiss the cart popup if visible by clicking the backdrop."""
        try:
            backdrop = self._page.locator(self.CART_POPUP_BACKDROP)
            if backdrop.is_visible():
                backdrop.click()
        except Exception:
            pass

    def _wait_for_search_results(self, query: str, timeout: int = 10000) -> None:
        """Wait for search results to appear."""
        try:
            self._page.locator(f'h1:has-text("\\"{query}\\"")').wait_for(
                state="visible",
                timeout=timeout,
            )
        except PlaywrightTimeout:
            pass

    def _extract_products(self) -> list[Product]:
        """Extract product information from search results."""
        products = []
        grid = self._page.locator(self.PRODUCT_GRID).first
        product_cards = grid.locator(self.PRODUCT_CARD).all()

        for card in product_cards:
            try:
                product = self._extract_product_from_card(card)
                if product:
                    products.append(product)
            except Exception:
                continue

        return products

    def _extract_product_from_card(self, card: Locator) -> Product | None:
        """Extract product data from a single product card."""
        try:
            name_elem = card.locator(self.PRODUCT_NAME).first
            name = self.get_text(name_elem).strip()

            if not name:
                return None

            price_elem = card.locator(self.PRODUCT_PRICE).first
            price_text = self.get_text(price_elem)
            price = self._parse_price(price_text)

            unit_price = None
            try:
                unit_price_elem = card.locator(self.PRODUCT_UNIT_PRICE).first
                if unit_price_elem.is_visible():
                    unit_price = self.get_text(unit_price_elem).strip()
            except Exception:
                pass

            image_url = None
            try:
                img_elem = card.locator(self.PRODUCT_IMAGE).first
                if img_elem.is_visible():
                    image_url = img_elem.get_attribute("src")
            except Exception:
                pass

            product_id = card.get_attribute("data-product-id") or card.get_attribute("data-sku")

            return Product(
                name=name,
                price=price,
                unit_price=unit_price,
                image_url=image_url,
                product_id=product_id,
            )

        except Exception:
            return None

    def _parse_price(self, price_text: str) -> float:
        """Parse price from text like '25,90 kr' or '25.90'."""
        cleaned = re.sub(r"[^\d,.]", "", price_text)
        cleaned = cleaned.replace(",", ".")

        try:
            return float(cleaned)
        except Exception:
            return 0.0

    def get_product_card(self, product_name: str) -> Locator | None:
        """
        Find a product card by name (partial match).

        Args:
            product_name: Product name to search for.

        Returns:
            Locator for the product card or None.
        """
        grid = self._page.locator(self.PRODUCT_GRID).first
        cards = grid.locator(self.PRODUCT_CARD).all()

        for card in cards:
            try:
                name_elem = card.locator(self.PRODUCT_NAME).first
                name = self.get_text(name_elem).lower()
                if product_name.lower() in name:
                    return card
            except Exception:
                continue

        return None

    def change_quantity(self, product_name: str, quantity: int) -> bool:
        """
        Change quantity for a product.

        Args:
            product_name: Name of product to modify.
            quantity: Target quantity (0 to remove from cart).

        Returns:
            True if quantity was changed successfully.
        """
        if quantity < 0:
            return False

        card = self.get_product_card(product_name)
        if not card:
            return False

        try:
            cart_text = self._get_cart_button_text()
            qty_input = card.locator(self.QUANTITY_INPUT).first
            qty_input.fill(str(quantity))
            qty_input.blur()
            self._wait_for_cart_update(cart_text)
            self._dismiss_cart_popup()
            return True

        except Exception:
            return False

    def add_to_cart(self, product_name: str, quantity: int = 1) -> AddToCartResult:
        """
        Add a product to cart.

        Args:
            product_name: Name of product to add.
            quantity: Quantity to add (default 1).

        Returns:
            AddToCartResult with success status and details.
        """
        card = self.get_product_card(product_name)

        if not card:
            return AddToCartResult(
                success=False,
                product_name=product_name,
                quantity=0,
                message=f"Product '{product_name}' not found in search results",
            )

        try:
            cart_text = self._get_cart_button_text()
            qty_input = card.locator(self.QUANTITY_INPUT).first
            current_qty = 0
            try:
                qty_text = qty_input.input_value()
                current_qty = int(qty_text) if qty_text.isdigit() else 0
            except Exception:
                pass

            new_qty = current_qty + quantity
            qty_input.fill(str(new_qty))
            qty_input.blur()
            self._wait_for_cart_update(cart_text)
            self._dismiss_cart_popup()

            return AddToCartResult(
                success=True,
                product_name=product_name,
                quantity=new_qty,
                message=f"Set '{product_name}' quantity to {new_qty} (added {quantity})",
            )

        except Exception as e:
            return AddToCartResult(
                success=False,
                product_name=product_name,
                quantity=0,
                message=f"Failed to add to cart: {str(e)}",
            )
