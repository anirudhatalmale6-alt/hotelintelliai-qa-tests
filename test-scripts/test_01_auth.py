"""
Test Suite 1: Authentication & Login
Tests login flows for both onboarding and dashboard portals.
"""
import pytest
from conftest import BASE_URL_ONBOARDING, BASE_URL_DASHBOARD, TEST_EMAIL, TEST_PASSWORD


class TestOnboardingAuth:
    """Authentication tests for onboarding.hotelintelliai.com"""

    def test_login_page_loads(self, page):
        """Verify login page renders with all expected elements."""
        page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
        assert page.locator('input[type="email"]').is_visible()
        assert page.locator('input[type="password"]').is_visible()
        assert page.locator('button:has-text("Sign in with Google")').is_visible()
        assert page.locator('button[type="submit"]').is_visible()
        assert "HotelIntelliai" in page.content()

    def test_login_page_title(self, page):
        """Verify page title is correct."""
        page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
        assert "hotelintelliai" in page.title().lower()

    def test_successful_email_login(self, page):
        """Verify email/password login works and shows hotel list."""
        page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(TEST_EMAIL)
        page.locator('input[type="password"]').fill(TEST_PASSWORD)
        page.locator('button').nth(1).click()
        page.wait_for_timeout(5000)

        body = page.locator('body').inner_text()
        assert "HOTEL MANAGEMENT" in body
        assert "Add Hotel" in body
        assert TEST_EMAIL in body

    def test_invalid_credentials(self, page):
        """Verify invalid login is handled gracefully."""
        page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill("invalid@test.com")
        page.locator('input[type="password"]').fill("wrongpassword")
        page.locator('button').nth(1).click()
        page.wait_for_timeout(5000)

        # Should still be on login page or show error
        body = page.locator('body').inner_text()
        # Should NOT show hotel management (not logged in)
        assert "HOTEL MANAGEMENT" not in body or "error" in body.lower() or "invalid" in body.lower()

    def test_empty_credentials_prevented(self, page):
        """Verify empty form doesn't submit (Next/Sign In should be disabled or show error)."""
        page.goto(BASE_URL_ONBOARDING, wait_until="networkidle", timeout=60000)
        # Don't fill anything, just click Sign In
        page.locator('button').nth(1).click()
        page.wait_for_timeout(3000)

        # Should still be on login page
        assert page.locator('input[type="email"]').is_visible()


class TestDashboardAuth:
    """Authentication tests for dashboard.hotelintelliai.com"""

    def test_dashboard_login_page_loads(self, page):
        """Verify dashboard login page renders correctly."""
        page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
        assert page.locator('input[type="email"]').is_visible()
        assert page.locator('input[type="password"]').is_visible()

    def test_dashboard_successful_login(self, page):
        """Verify dashboard login shows hotel selection."""
        page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(TEST_EMAIL)
        page.locator('input[type="password"]').fill(TEST_PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)

        body = page.locator('body').inner_text()
        assert "SELECT HOTEL" in body
        assert "Sign Out" in body

    def test_dashboard_sign_out(self, page):
        """Verify sign out returns to login page."""
        page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(TEST_EMAIL)
        page.locator('input[type="password"]').fill(TEST_PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)

        page.locator('button:has-text("Sign Out")').click()
        page.wait_for_timeout(3000)

        # Should be back on login page
        assert page.locator('input[type="email"]').is_visible()
