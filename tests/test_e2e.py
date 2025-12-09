import os
import subprocess
import time

import pytest
import requests
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def start_app_server():
    """Start a uvicorn server for E2E tests and stop it after the session."""
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./test_e2e.db"

    # Launch uvicorn in the background
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for the server to become healthy
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        proc.terminate()
        proc.wait(timeout=5)
        raise RuntimeError("Failed to start uvicorn for E2E tests")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

def test_register_success(page: Page):
    # Generate unique user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f"user_{unique_id}"
    email = f"user_{unique_id}@example.com"
    password = "securepassword123"

    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirmPassword", password)
    
    page.click("button[type='submit']")
    
    # Expect success message
    expect(page.locator(".message.success")).to_be_visible(timeout=5000)
    expect(page.locator(".message.success")).to_contain_text("Registration successful")

def test_register_password_mismatch(page: Page):
    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", "mismatch_user")
    page.fill("#email", "mismatch@example.com")
    page.fill("#password", "password123")
    page.fill("#confirmPassword", "password456")
    
    page.click("button[type='submit']")
    
    # Expect error message
    expect(page.locator(".message.error")).to_be_visible()
    expect(page.locator(".message.error")).to_contain_text("Passwords do not match")

def test_login_success(page: Page):
    # First register a user (or use a known one, but better to register fresh)
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f"login_{unique_id}"
    email = f"login_{unique_id}@example.com"
    password = "securepassword123"

    # Register via API to speed up
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", username)
    page.fill("#password", password)
    
    page.click("button[type='submit']")
    
    # Expect success message
    expect(page.locator(".message.success")).to_be_visible(timeout=5000)
    expect(page.locator(".message.success")).to_contain_text("Login successful")

def test_login_invalid_credentials(page: Page):
    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", "nonexistent_user")
    page.fill("#password", "wrongpassword")
    
    page.click("button[type='submit']")
    
    # Expect error message
    expect(page.locator(".message.error")).to_be_visible(timeout=5000)
    expect(page.locator(".message.error")).to_contain_text("Invalid username or password")
