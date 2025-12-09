import os
import subprocess
import time
import uuid

import pytest
import requests
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def start_app_server():
    """Start a uvicorn server for calculations E2E tests and tear it down."""
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./test_e2e.db"

    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

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
        raise RuntimeError("Failed to start uvicorn for calculations E2E tests")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

@pytest.fixture
def authenticated_user(page: Page):
    """Fixture to create and login a user, returning auth context."""
    # Generate unique user
    unique_id = str(uuid.uuid4())[:8]
    username = f"calc_user_{unique_id}"
    email = f"calc_{unique_id}@example.com"
    password = "securepassword123"
    
    # Register user via API
    response = requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert response.status_code == 201
    
    # Login via UI
    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#loginForm button[type='submit']")
    
    # Wait for redirect to calculations page
    expect(page).to_have_url(f"{BASE_URL}/static/calculations.html", timeout=8000)
    
    return {"username": username, "password": password}


def get_first_calculation_id(page: Page):
    return page.evaluate(
        """async () => {
            const res = await fetch('/calculations?limit=1', {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            const data = await res.json();
            return data[0]?.id;
        }"""
    )


# ========== POSITIVE TEST SCENARIOS ==========

def test_add_calculation_success(page: Page, authenticated_user):
    """Test successful creation of a new calculation."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Fill in calculation form
    page.fill("#operand-a", "10")
    page.fill("#operand-b", "5")
    page.select_option("#operation", "Add")
    
    # Submit form
    page.click("#add-calculation-form button[type='submit']")
    
    # Expect success message
    expect(page.locator(".message.success")).to_be_visible(timeout=5000)
    expect(page.locator(".message.success")).to_contain_text("Calculation created successfully")
    expect(page.locator(".message.success")).to_contain_text("15")
    
    # Verify calculation appears in table
    expect(page.locator(".calculations-table")).to_be_visible()
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)


def test_browse_calculations(page: Page, authenticated_user):
    """Test browsing/listing all user calculations."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create multiple calculations
    calculations = [
        {"a": "10", "b": "5", "op": "Add"},
        {"a": "20", "b": "4", "op": "Multiply"},
        {"a": "15", "b": "3", "op": "Divide"}
    ]
    
    for calc in calculations:
        page.fill("#operand-a", calc["a"])
        page.fill("#operand-b", calc["b"])
        page.select_option("#operation", calc["op"])
        page.click("#add-calculation-form button[type='submit']")
        page.wait_for_timeout(500)  # Brief wait between submissions
    
    # Verify all calculations are displayed
    expect(page.locator(".calculations-table tbody tr")).to_have_count(3)
    
    # Verify table headers
    expect(page.locator(".calculations-table th")).to_contain_text(["Date", "Operand A", "Operation", "Operand B", "Result", "Actions"])


def test_read_calculation_details(page: Page, authenticated_user):
    """Test viewing details of a specific calculation."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create a calculation
    page.fill("#operand-a", "25")
    page.fill("#operand-b", "5")
    page.select_option("#operation", "Subtract")
    page.click("#add-calculation-form button[type='submit']")
    
    # Wait for table to update
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    # Verify details from the table
    expect(page.locator(".calculations-table tbody")).to_contain_text("25")
    expect(page.locator(".calculations-table tbody")).to_contain_text("5")
    expect(page.locator(".calculations-table tbody")).to_contain_text("Subtract")
    expect(page.locator(".calculations-table tbody")).to_contain_text("20")


def test_edit_calculation_success(page: Page, authenticated_user):
    """Test successfully editing an existing calculation via API."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create a calculation
    page.fill("#operand-a", "100")
    page.fill("#operand-b", "10")
    page.select_option("#operation", "Divide")
    page.click("#add-calculation-form button[type='submit']")
    
    # Wait for creation
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    calc_id = get_first_calculation_id(page)
    assert calc_id
    
    # Update via PUT /calculations/{id}
    import requests
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token
    
    response = requests.put(
        f"{BASE_URL}/calculations/{calc_id}",
        json={"a": 50, "b": 5, "type": "Multiply"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Status: {response.status_code}, Error: {response.text}"
    result = response.json()
    assert result["a"] == 50
    assert result["b"] == 5
    assert result["result"] == 250
    
    # Verify updated values in table after reload
    page.reload()
    expect(page.locator(".calculations-table tbody")).to_contain_text("50", timeout=8000)
    expect(page.locator(".calculations-table tbody")).to_contain_text("250", timeout=8000)


def test_delete_calculation_success(page: Page, authenticated_user):
    """Test successfully deleting a calculation via API."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create two calculations
    page.fill("#operand-a", "10")
    page.fill("#operand-b", "2")
    page.select_option("#operation", "Add")
    page.click("#add-calculation-form button[type='submit']")
    page.wait_for_timeout(500)
    
    page.fill("#operand-a", "20")
    page.fill("#operand-b", "3")
    page.select_option("#operation", "Multiply")
    page.click("#add-calculation-form button[type='submit']")
    
    # Verify both exist
    expect(page.locator(".calculations-table tbody tr")).to_have_count(2)
    
    # Get first calculation ID and delete via API
    calc_id = get_first_calculation_id(page)
    assert calc_id
    
    import requests
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token
    
    response = requests.delete(
        f"{BASE_URL}/calculations/{calc_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 204), f"Status: {response.status_code}, Error: {response.text}"
    
    page.reload()
    
    # Verify only one calculation remains
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1, timeout=8000)


def test_multiple_operations(page: Page, authenticated_user):
    """Test all four arithmetic operations."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    operations = [
        {"a": "10", "b": "5", "op": "Add", "result": "15"},
        {"a": "10", "b": "5", "op": "Subtract", "result": "5"},
        {"a": "10", "b": "5", "op": "Multiply", "result": "50"},
        {"a": "10", "b": "5", "op": "Divide", "result": "2"}
    ]
    
    for calc in operations:
        page.fill("#operand-a", calc["a"])
        page.fill("#operand-b", calc["b"])
        page.select_option("#operation", calc["op"])
        page.click("#add-calculation-form button[type='submit']")
        
        # Verify success message contains expected result
        expect(page.locator(".message.success")).to_be_visible()
        expect(page.locator(".message.success")).to_contain_text(calc["result"])
        
        page.wait_for_timeout(300)
    
    # Verify all 4 calculations are in the table
    expect(page.locator(".calculations-table tbody tr")).to_have_count(4)


def test_power_operation_and_stats(page: Page, authenticated_user):
    """Test power operation and summary widgets update."""
    page.goto(f"{BASE_URL}/static/calculations.html")

    page.fill("#operand-a", "2")
    page.fill("#operand-b", "4")
    page.select_option("#operation", "Power")
    page.click("#add-calculation-form button[type='submit']")

    expect(page.locator(".message.success")).to_contain_text("16")

    # Summary cards should be populated
    expect(page.locator("#stat-total")).not_to_have_text("0")
    expect(page.locator("#stat-most-used")).not_to_have_text("-")


# ========== NEGATIVE TEST SCENARIOS ==========

def test_add_calculation_division_by_zero(page: Page, authenticated_user):
    """Test that division by zero is prevented."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Try to create division by zero
    page.fill("#operand-a", "10")
    page.fill("#operand-b", "0")
    page.select_option("#operation", "Divide")
    page.click("#add-calculation-form button[type='submit']")
    
    # Expect error message
    expect(page.locator(".message.error")).to_be_visible(timeout=5000)
    expect(page.locator(".message.error")).to_contain_text("Division by zero")


def test_edit_calculation_division_by_zero(page: Page, authenticated_user):
    """Test that editing to division by zero is prevented."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create a valid calculation
    page.fill("#operand-a", "10")
    page.fill("#operand-b", "5")
    page.select_option("#operation", "Add")
    page.click("#add-calculation-form button[type='submit']")
    
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    # Edit to division by zero
    calc_id = get_first_calculation_id(page)
    assert calc_id
    status = page.evaluate(
        """async (id) => {
            const res = await fetch(`/calculations/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ a: 10, b: 0, type: 'Divide' })
            });
            return res.status;
        }""",
        calc_id,
    )
    assert status in (400, 422)


def test_calculations_require_authentication(page: Page):
    """Test that accessing calculations page without auth redirects to login."""
    # Try to access calculations page without logging in
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Should redirect to login page
    expect(page).to_have_url(f"{BASE_URL}/static/login.html", timeout=5000)


def test_invalid_numeric_inputs(page: Page, authenticated_user):
    """Test handling of invalid numeric inputs."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Manually set a non-numeric value (fill fails on type=number)
    is_valid = page.eval_on_selector(
        "#operand-a",
        "el => { el.value = 'abc'; return el.validity.valid; }",
    )
    assert not is_valid


def test_user_isolation(page: Page):
    """Test that users can only see their own calculations."""
    # Create first user
    unique_id1 = str(uuid.uuid4())[:8]
    user1 = {
        "username": f"user1_{unique_id1}",
        "email": f"user1_{unique_id1}@example.com",
        "password": "password123"
    }
    
    requests.post(f"{BASE_URL}/users/register", json=user1)
    
    # Login as user1
    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#username", user1["username"])
    page.fill("#password", user1["password"])
    page.click("#loginForm button[type='submit']")
    
    expect(page).to_have_url(f"{BASE_URL}/static/calculations.html", timeout=5000)
    
    # Create a calculation for user1
    page.fill("#operand-a", "100")
    page.fill("#operand-b", "50")
    page.select_option("#operation", "Add")
    page.click("#add-calculation-form button[type='submit']")
    
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    # Logout
    page.evaluate("window.logout()")
    expect(page).to_have_url(f"{BASE_URL}/static/login.html", timeout=5000)
    
    # Create second user
    unique_id2 = str(uuid.uuid4())[:8]
    user2 = {
        "username": f"user2_{unique_id2}",
        "email": f"user2_{unique_id2}@example.com",
        "password": "password123"
    }
    
    requests.post(f"{BASE_URL}/users/register", json=user2)
    
    # Login as user2
    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#username", user2["username"])
    page.fill("#password", user2["password"])
    page.click("#loginForm button[type='submit']")
    
    expect(page).to_have_url(f"{BASE_URL}/static/calculations.html", timeout=5000)
    
    # User2 should see no calculations (or the "no data" message)
    no_data = page.locator(".no-data")
    if no_data.is_visible():
        expect(no_data).to_contain_text("No calculations found")
    else:
        # If table exists, it should be empty
        expect(page.locator(".calculations-table tbody tr")).to_have_count(0)


def test_refresh_calculations(page: Page, authenticated_user):
    """Test the refresh button reloads calculations."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create a calculation
    page.fill("#operand-a", "7")
    page.fill("#operand-b", "3")
    page.select_option("#operation", "Add")
    page.click("#add-calculation-form button[type='submit']")
    
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    # Click refresh button
    page.click("#refresh-btn")
    
    # Table should still show the calculation
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    expect(page.locator(".calculations-table tbody")).to_contain_text("7")
    expect(page.locator(".calculations-table tbody")).to_contain_text("10")


def test_cancel_edit(page: Page, authenticated_user):
    """Test canceling an edit operation."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create a calculation
    page.fill("#operand-a", "15")
    page.fill("#operand-b", "5")
    page.select_option("#operation", "Add")
    page.click("#add-calculation-form button[type='submit']")
    
    expect(page.locator(".calculations-table tbody tr")).to_have_count(1)
    
    # Open edit modal
    calc_id = get_first_calculation_id(page)
    assert calc_id
    page.evaluate(
        "id => { document.getElementById('edit-calc-id').value = id; document.getElementById('edit-modal').style.display = 'block'; }",
        calc_id,
    )
    expect(page.locator("#edit-modal")).to_be_visible()
    
    # Click cancel
    page.click("#cancel-edit-btn")
    
    # Modal should close
    expect(page.locator("#edit-modal")).not_to_be_visible()
    
    # Original calculation should remain unchanged
    expect(page.locator(".calculations-table tbody")).to_contain_text("15")
    expect(page.locator(".calculations-table tbody")).to_contain_text("20")


def test_profile_update_and_password_change(page: Page, authenticated_user):
    """Update profile and then change password via UI."""
    page.goto(f"{BASE_URL}/static/calculations.html")

    page.fill("#profile-full-name", "E2E Tester")
    page.fill("#profile-bio", "Writes e2e scenarios")
    page.click("#profile-form button[type='submit']")
    expect(page.locator(".message.success")).to_be_visible()

    page.fill("#current-password", authenticated_user["password"])
    new_password = "newpassword1234"
    page.fill("#new-password", new_password)
    page.fill("#confirm-new-password", new_password)
    page.click("#password-form button[type='submit']")

    expect(page.locator(".message.success")).to_contain_text("Password updated")
    expect(page).to_have_url(f"{BASE_URL}/static/login.html", timeout=6000)


def test_decimal_calculations(page: Page, authenticated_user):
    """Test calculations with decimal numbers."""
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Create calculation with decimals
    page.fill("#operand-a", "10.5")
    page.fill("#operand-b", "2.5")
    page.select_option("#operation", "Multiply")
    page.click("#add-calculation-form button[type='submit']")
    
    # Verify success
    expect(page.locator(".message.success")).to_be_visible()
    expect(page.locator(".message.success")).to_contain_text("26.25")
    
    # Verify in table
    expect(page.locator(".calculations-table tbody")).to_contain_text("10.5")
    expect(page.locator(".calculations-table tbody")).to_contain_text("2.5")
