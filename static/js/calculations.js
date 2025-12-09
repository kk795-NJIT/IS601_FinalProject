// Calculations Management JavaScript
const API_BASE_URL = window.location.origin;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
    loadProfile();
    loadSummary();
    loadCalculations();
});

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    if (!token || !username) {
        window.location.href = '/static/login.html';
        return;
    }
    
    document.getElementById('username-display').textContent = `Welcome, ${username}!`;
}

// Fetch and display user profile
async function loadProfile() {
    const usernameDisplay = document.getElementById('username-display');
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const profile = await response.json();
        localStorage.setItem('username', profile.username);
        usernameDisplay.textContent = `Welcome, ${profile.username}!`;
        document.getElementById('last-login').textContent = profile.last_login ? `Last login: ${new Date(profile.last_login).toLocaleString()}` : '';

        // Populate form fields
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.username.value = profile.username;
            profileForm.email.value = profile.email;
            profileForm.full_name.value = profile.full_name || '';
            profileForm.bio.value = profile.bio || '';
        }
    } catch (error) {
        console.error('Error loading profile', error);
    }
}

// Submit profile update
async function handleProfileUpdate(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        username: form.username.value,
        email: form.email.value,
        full_name: form.full_name.value || null,
        bio: form.bio.value || null,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update profile');
        }

        showMessage('Profile updated successfully', 'success');
        await loadProfile();
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

// Submit password change
async function handlePasswordChange(event) {
    event.preventDefault();
    const form = event.target;

    if (form.new_password.value !== form.confirm_new_password.value) {
        showMessage('New passwords do not match', 'error');
        return;
    }

    const payload = {
        current_password: form.current_password.value,
        new_password: form.new_password.value,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/change-password`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to change password');
        }

        showMessage('Password updated successfully. Please login again.', 'success');
        setTimeout(logout, 1200);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

// Fetch calculation summary
async function loadSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/calculations/summary`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;

        const summary = await response.json();
        document.getElementById('stat-total').textContent = summary.total;
        document.getElementById('stat-average').textContent = summary.average_result !== null ? summary.average_result.toFixed(2) : '-';
        document.getElementById('stat-most-used').textContent = summary.most_used_operation || '-';
        document.getElementById('stat-last').textContent = summary.last_result !== null ? summary.last_result.toFixed(2) : '-';

        const breakdown = document.getElementById('stat-breakdown');
        breakdown.innerHTML = '';
        Object.entries(summary.operations_breakdown || {}).forEach(([op, count]) => {
            const span = document.createElement('span');
            span.textContent = `${op}: ${count}`;
            breakdown.appendChild(span);
        });
    } catch (error) {
        console.error('Failed to load summary', error);
    }
}

// Get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Add calculation form
    document.getElementById('add-calculation-form').addEventListener('submit', handleAddCalculation);
    
    // Edit calculation form
    document.getElementById('edit-calculation-form').addEventListener('submit', handleEditCalculation);

    // Profile + password forms
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }

    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }
    
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', loadCalculations);
    
    // Modal close buttons
    const modals = document.querySelectorAll('.modal');
    const closeBtns = document.querySelectorAll('.close');
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // Cancel edit button
    document.getElementById('cancel-edit-btn').addEventListener('click', function() {
        document.getElementById('edit-modal').style.display = 'none';
    });
    
    // Close view button
    document.getElementById('close-view-btn').addEventListener('click', function() {
        document.getElementById('view-modal').style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Tab switching function
function switchTab(tabName) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab and mark button as active
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    const activeButton = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    window.location.href = '/static/login.html';
}

// Display message
function showMessage(message, type = 'success') {
    const container = document.getElementById('message-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    container.innerHTML = '';
    container.appendChild(messageDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Browse - Load all calculations
async function loadCalculations() {
    const container = document.getElementById('calculations-container');
    container.innerHTML = '<p class="loading">Loading calculations...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculations?limit=100`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            throw new Error(`Failed to load calculations: ${response.statusText}`);
        }
        
        const calculations = await response.json();
        displayCalculations(calculations);
        
    } catch (error) {
        console.error('Error loading calculations:', error);
        container.innerHTML = '<p class="error">Failed to load calculations. Please try again.</p>';
        showMessage('Failed to load calculations.', 'error');
    }
}

// Display calculations in a table
function displayCalculations(calculations) {
    const container = document.getElementById('calculations-container');
    
    if (calculations.length === 0) {
        container.innerHTML = '<p class="no-data">No calculations found. Create your first calculation above!</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'calculations-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Date</th>
                <th>Operand A</th>
                <th>Operation</th>
                <th>Operand B</th>
                <th>Result</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            ${calculations.map(calc => `
                <tr>
                    <td>${new Date(calc.created_at).toLocaleString()}</td>
                    <td>${calc.a}</td>
                    <td>${getOperationSymbol(calc.type)}</td>
                    <td>${calc.b}</td>
                    <td class="result">${calc.result.toFixed(4)}</td>
                    <td class="actions">
                        <button class="btn btn-small btn-info" onclick="viewCalculation('${calc.id}')">View</button>
                        <button class="btn btn-small btn-warning" onclick="editCalculation('${calc.id}')">Edit</button>
                        <button class="btn btn-small btn-danger" onclick="deleteCalculation('${calc.id}')">Delete</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    container.innerHTML = '';
    container.appendChild(table);
}

// Get operation symbol
function getOperationSymbol(type) {
    const symbols = {
        'Add': '+',
        'Subtract': '−',
        'Multiply': '×',
        'Divide': '÷',
        'Power': '^',
        'Modulo': '%'
    };
    return `${type} (${symbols[type] || type})`;
}

// Add - Create new calculation
async function handleAddCalculation(event) {
    event.preventDefault();
    
    const formData = {
        a: parseFloat(document.getElementById('operand-a').value),
        b: parseFloat(document.getElementById('operand-b').value),
        type: document.getElementById('operation').value
    };
    
    // Client-side validation
    if ((formData.type === 'Divide' || formData.type === 'Modulo') && formData.b === 0) {
        showMessage('Division by zero is not allowed!', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculations`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create calculation');
        }
        
        const calculation = await response.json();
        showMessage(`Calculation created successfully! Result: ${calculation.result}`, 'success');
        
        // Reset form and reload calculations
        document.getElementById('add-calculation-form').reset();
        loadCalculations();
        loadSummary();
        
    } catch (error) {
        console.error('Error creating calculation:', error);
        showMessage(error.message, 'error');
    }
}

// Read - View calculation details
async function viewCalculation(calcId) {
    try {
        const response = await fetch(`${API_BASE_URL}/calculations/${calcId}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load calculation details');
        }
        
        const calc = await response.json();
        displayCalculationDetails(calc);
        
        // Show modal
        document.getElementById('view-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error viewing calculation:', error);
        showMessage('Failed to load calculation details.', 'error');
    }
}

// Display calculation details in modal
function displayCalculationDetails(calc) {
    const detailsDiv = document.getElementById('calculation-details');
    detailsDiv.innerHTML = `
        <div class="detail-row">
            <label>Calculation ID:</label>
            <span>${calc.id}</span>
        </div>
        <div class="detail-row">
            <label>First Operand (a):</label>
            <span>${calc.a}</span>
        </div>
        <div class="detail-row">
            <label>Operation:</label>
            <span>${getOperationSymbol(calc.type)}</span>
        </div>
        <div class="detail-row">
            <label>Second Operand (b):</label>
            <span>${calc.b}</span>
        </div>
        <div class="detail-row">
            <label>Result:</label>
            <span class="result-highlight">${calc.result}</span>
        </div>
        <div class="detail-row">
            <label>Created At:</label>
            <span>${new Date(calc.created_at).toLocaleString()}</span>
        </div>
    `;
}

// Edit - Open edit modal
async function editCalculation(calcId) {
    try {
        const response = await fetch(`${API_BASE_URL}/calculations/${calcId}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load calculation');
        }
        
        const calc = await response.json();
        
        // Populate edit form
        document.getElementById('edit-calc-id').value = calc.id;
        document.getElementById('edit-operand-a').value = calc.a;
        document.getElementById('edit-operand-b').value = calc.b;
        document.getElementById('edit-operation').value = calc.type;
        
        // Show modal
        document.getElementById('edit-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error loading calculation for edit:', error);
        showMessage('Failed to load calculation for editing.', 'error');
    }
}

// Edit - Submit updated calculation
async function handleEditCalculation(event) {
    event.preventDefault();
    
    const calcId = document.getElementById('edit-calc-id').value;
    const formData = {
        a: parseFloat(document.getElementById('edit-operand-a').value),
        b: parseFloat(document.getElementById('edit-operand-b').value),
        type: document.getElementById('edit-operation').value
    };
    
    // Client-side validation
    if ((formData.type === 'Divide' || formData.type === 'Modulo') && formData.b === 0) {
        showMessage('Division by zero is not allowed!', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculations/${calcId}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update calculation');
        }
        
        const calculation = await response.json();
        showMessage(`Calculation updated successfully! New result: ${calculation.result}`, 'success');
        
        // Close modal and reload calculations
        document.getElementById('edit-modal').style.display = 'none';
        loadCalculations();
        loadSummary();
        
    } catch (error) {
        console.error('Error updating calculation:', error);
        showMessage(error.message, 'error');
    }
}

// Delete - Remove calculation
async function deleteCalculation(calcId) {
    if (!confirm('Are you sure you want to delete this calculation? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculations/${calcId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000);
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to delete calculation');
        }
        
        showMessage('Calculation deleted successfully!', 'success');
        loadCalculations();
        loadSummary();
        
    } catch (error) {
        console.error('Error deleting calculation:', error);
        showMessage('Failed to delete calculation.', 'error');
    }
}

// Make functions globally available for onclick handlers
window.viewCalculation = viewCalculation;
window.editCalculation = editCalculation;
window.deleteCalculation = deleteCalculation;
