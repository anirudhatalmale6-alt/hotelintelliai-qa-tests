"""
Test Suite 2: Hotel Management
Tests hotel listing, creation wizard, and hotel card actions.
"""
import pytest
from conftest import BASE_URL_ONBOARDING


class TestHotelListing:
    """Tests for the main hotel management page."""

    def test_hotels_displayed(self, logged_in_onboarding):
        """Verify existing hotels are listed on the main page."""
        page = logged_in_onboarding
        body = page.locator('body').inner_text()
        assert "le Patte" in body
        assert "The Riverie by Katathani" in body

    def test_hotel_cards_show_channels(self, logged_in_onboarding):
        """Verify hotel cards display configured channel badges."""
        page = logged_in_onboarding
        body = page.locator('body').inner_text()
        # Riverie should have whatsapp, telegram, line, email
        assert "whatsapp" in body
        assert "telegram" in body
        assert "email" in body

    def test_hotel_cards_have_action_buttons(self, logged_in_onboarding):
        """Verify each hotel card has Knowledge Base, Delete, and Staff buttons."""
        page = logged_in_onboarding
        kb_buttons = page.locator('button:has-text("Knowledge Base")')
        delete_buttons = page.locator('button:has-text("Delete")')
        staff_buttons = page.locator('button:has-text("Staff")')

        assert kb_buttons.count() >= 2
        assert delete_buttons.count() >= 2
        assert staff_buttons.count() >= 2

    def test_add_hotel_button_exists(self, logged_in_onboarding):
        """Verify + Add Hotel button is visible."""
        page = logged_in_onboarding
        assert page.locator('button:has-text("Add Hotel")').is_visible()

    def test_superadmin_label_shown(self, logged_in_onboarding):
        """Verify superadmin role is displayed."""
        page = logged_in_onboarding
        body = page.locator('body').inner_text()
        assert "superadmin" in body


class TestOnboardingWizard:
    """Tests for the 4-step hotel onboarding wizard."""

    def test_wizard_opens(self, logged_in_onboarding):
        """Verify Add Hotel navigates to onboarding wizard."""
        page = logged_in_onboarding
        page.locator('button:has-text("Add Hotel")').click()
        page.wait_for_timeout(3000)

        assert "/onboard" in page.url
        body = page.locator('body').inner_text()
        assert "HOTEL ONBOARDING" in body
        assert "Hotel Info" in body

    def test_step1_form_fields(self, logged_in_onboarding):
        """Verify Step 1 has all required form fields."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "HOTEL NAME" in body
        assert "HOTEL ID" in body
        assert "OWNER / MANAGER NAME" in body
        assert "CONTACT EMAIL" in body
        assert "TIMEZONE" in body
        assert "PRIMARY LANGUAGE" in body
        assert "PMS INTEGRATION" in body

    def test_step1_validation_next_disabled(self, logged_in_onboarding):
        """Verify Next button is disabled when required fields are empty."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        next_btn = page.locator('button:has-text("Next")')
        is_disabled = next_btn.get_attribute('disabled')
        assert is_disabled is not None  # Button should be disabled

    def test_step1_to_step2_navigation(self, logged_in_onboarding):
        """Verify filling Step 1 enables Next and navigates to Step 2."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Fill required fields
        inputs = page.locator('input')
        inputs.nth(0).fill("Test Wizard Hotel")
        inputs.nth(2).fill("Test Manager")
        inputs.nth(3).fill("test@hotel.com")

        page.wait_for_timeout(1000)

        # Next should now be enabled
        next_btn = page.locator('button:has-text("Next")')
        next_btn.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Connect your channels" in body

    def test_step2_channel_toggles(self, logged_in_onboarding):
        """Verify Step 2 shows all 5 channel options with toggle switches."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Fill step 1
        inputs = page.locator('input')
        inputs.nth(0).fill("Channel Test Hotel")
        inputs.nth(2).fill("Test Manager")
        inputs.nth(3).fill("test@hotel.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Web Chat Widget" in body
        assert "WhatsApp" in body
        assert "Telegram" in body
        assert "LINE" in body or "LINE Official" in body
        assert "Email" in body

        # Verify toggle switches exist (custom div.toggle-switch elements)
        toggles = page.locator('.toggle-switch')
        assert toggles.count() == 5

    def test_step2_web_toggle_default_on(self, logged_in_onboarding):
        """Verify Web Chat Widget is enabled by default."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        inputs = page.locator('input')
        inputs.nth(0).fill("Default Toggle Hotel")
        inputs.nth(2).fill("Test Manager")
        inputs.nth(3).fill("test@hotel.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        web_toggle = page.locator('.toggle-switch').first
        classes = web_toggle.get_attribute('class')
        assert 'on' in classes  # Web should be on by default

    def test_step2_toggle_click(self, logged_in_onboarding):
        """Verify clicking a channel toggle switches its state."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        inputs = page.locator('input')
        inputs.nth(0).fill("Toggle Click Hotel")
        inputs.nth(2).fill("Test Manager")
        inputs.nth(3).fill("test@hotel.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        # Click the Email toggle (5th one, index 4)
        email_toggle = page.locator('.toggle-switch').nth(4)
        initial_classes = email_toggle.get_attribute('class')
        email_toggle.click()
        page.wait_for_timeout(1000)
        after_classes = email_toggle.get_attribute('class')

        # State should have changed
        assert initial_classes != after_classes

    def test_step3_agent_personality(self, logged_in_onboarding):
        """Verify Step 3 shows personality options and escalation email."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Fill step 1 and advance
        inputs = page.locator('input')
        inputs.nth(0).fill("Agent Test Hotel")
        inputs.nth(2).fill("Test Manager")
        inputs.nth(3).fill("test@hotel.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Configure your AI concierge" in body
        assert "Friendly & Warm" in body
        assert "Formal & Professional" in body
        assert "Classic Concierge" in body
        assert "ESCALATION EMAIL" in body

    def test_step4_review_summary(self, logged_in_onboarding):
        """Verify Step 4 shows complete review with Launch button."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Fill all steps
        inputs = page.locator('input')
        inputs.nth(0).fill("Review Test Hotel")
        inputs.nth(2).fill("Review Manager")
        inputs.nth(3).fill("review@hotel.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Ready to launch" in body
        assert "Review Test Hotel" in body
        assert "Review Manager" in body
        assert "review@hotel.com" in body
        assert "Launch Hotel" in body

    def test_back_button_navigation(self, logged_in_onboarding):
        """Verify Back button navigates to previous step."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/onboard", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        inputs = page.locator('input')
        inputs.nth(0).fill("Back Nav Hotel")
        inputs.nth(2).fill("Test")
        inputs.nth(3).fill("test@test.com")
        page.locator('button:has-text("Next")').click()
        page.wait_for_timeout(3000)

        # Should be on Step 2
        body = page.locator('body').inner_text()
        assert "Connect your channels" in body

        # Click Back
        page.locator('text=Back').first.click()
        page.wait_for_timeout(2000)

        # Should be back on Step 1
        body = page.locator('body').inner_text()
        assert "Tell us about your hotel" in body
