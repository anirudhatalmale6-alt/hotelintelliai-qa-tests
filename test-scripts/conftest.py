"""
Shared fixtures for HotelIntelliai Playwright test suite.
"""
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# Test configuration
BASE_URL_ONBOARDING = "https://onboarding.hotelintelliai.com"
BASE_URL_DASHBOARD = "https://dashboard.hotelintelliai.com"
TEST_EMAIL = "anirudhatomeiz@gmail.com"
TEST_PASSWORD = "CHANGEME"


@pytest.fixture(scope="session")
def browser():
    """Launch browser once per test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    """Create a fresh browser context for each test."""
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext):
    """Create a fresh page for each test."""
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page
    page.close()


@pytest.fixture
def logged_in_onboarding(page: Page):
    """Log in to the onboarding portal and return the page."""
    page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
    page.locator('input[type="email"]').fill(TEST_EMAIL)
    page.locator('input[type="password"]').fill(TEST_PASSWORD)
    page.locator('button').nth(1).click()
    page.wait_for_timeout(5000)
    return page


@pytest.fixture
def logged_in_dashboard(page: Page):
    """Log in to the dashboard portal and return the page."""
    page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
    page.locator('input[type="email"]').fill(TEST_EMAIL)
    page.locator('input[type="password"]').fill(TEST_PASSWORD)
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(5000)
    return page
