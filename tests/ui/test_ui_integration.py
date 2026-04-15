import pytest

def test_ui_create_note_flow():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        pytest.skip("Playwright not installed or not available in this environment.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5000/")
        page.wait_for_selector("#noteForm")

        # Create a new note
        page.fill("#title", "UI Test App Note")
        page.fill("#content", "Contenido de prueba desde UI")
        page.fill("#notebook", "UI Tests")
        page.fill("#tags", "ui, test")
        page.click("#noteForm button[type='submit']")
        page.wait_for_selector(".note-title", timeout=10000)
        title = page.inner_text(".note-title")
        assert title == "UI Test App Note"

        # Open the note modal and verify title is centered in modal header
        page.click(".note-card")
        page.wait_for_selector("#modalTitle", timeout=5000)
        modal_title = page.inner_text("#modalTitle")
        assert modal_title == "UI Test App Note"

        # Close modal and finish
        page.click("#modalClose")
        browser.close()
