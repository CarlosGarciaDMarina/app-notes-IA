import pytest

def test_ui_edit_note_basic():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        pytest.skip("Playwright not installed or not available in this environment.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5000/")
        page.wait_for_selector("#noteForm")
        # Create a note
        page.fill("#title", "UI Edit Test")
        page.fill("#content", "Initial content")
        page.fill("#notebook", "UI")
        page.fill("#tags", "edit")
        page.click("#noteForm button[type='submit']")
        page.wait_for_selector(".note-card", timeout=10000)
        page.click(".note-card")
        page.wait_for_selector("#modalTitle", timeout=5000)
        # Edit title
        page.fill("#edit_title", "UI Edit Test - Updated")
        page.click("#modalSave")
        page.wait_for_timeout(1000)
        browser.close()
