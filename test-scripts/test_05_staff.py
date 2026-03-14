"""
Test Suite 5: Staff Management
Tests staff invitation, roles, and management.
"""
import pytest
from conftest import BASE_URL_ONBOARDING


class TestStaffManagement:
    """Tests for the staff management page."""

    def test_staff_page_loads(self, logged_in_onboarding):
        """Verify staff page loads for an existing hotel."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "STAFF" in body
        assert "Invite New Member" in body
        assert "Send Invite" in body

    def test_staff_role_options(self, logged_in_onboarding):
        """Verify role dropdown has Hotel Admin and Hotel Staff options."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Hotel Admin" in body
        assert "Hotel Staff" in body

    def test_staff_current_and_pending(self, logged_in_onboarding):
        """Verify Current Staff and Pending Invites sections exist."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Current Staff" in body
        assert "Pending Invites" in body

    def test_staff_invite_email_field(self, logged_in_onboarding):
        """Verify email input field exists for invitations."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        email_input = page.locator('input[placeholder*="email" i]')
        assert email_input.is_visible()

    def test_staff_active_and_remove_buttons(self, logged_in_onboarding):
        """Verify Active/Remove buttons exist for current staff."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        if "Current Staff (0)" not in body:
            assert "Active" in body or "Remove" in body

    def test_staff_new_hotel_empty(self, logged_in_onboarding):
        """Verify new hotel has no staff initially."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/oberoi_udaivilas/staff", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "No staff yet" in body or "Current Staff (0)" in body
