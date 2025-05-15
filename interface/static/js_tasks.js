// js_tasks.js - Legion Task Management UI

(function() {
    const taskListContainer = document.getElementById('task-list');
    const taskForm = document.getElementById('task-form');
    const taskAgentSelect = document.getElementById('task-agent');
    const notificationContainer = document.getElementById('notification-container');

    // Function to show a notification
    function showNotification(message, type = 'info') {
        if (!notificationContainer) {
            console.warn("Notification container not found.");
            return;
        }
        const notification = document.createElement('div');
        notification.className = `toast show bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} text-white`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');

        notification.innerHTML = `
            <div class="toast-header bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} text-white">
                <strong class="me-auto">${type === 'error' ? 'Error' : type === 'success' ? 'Success' : 'Info'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;

        notificationContainer.appendChild(notification);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 500);
        }, 5000);

        // Add click handler to close button
        const closeBtn = notification.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 500);
            });
        }
    }

    // Function to render the task list
    function renderTasks(tasks) {
        if (!taskListContainer) {
            console.warn("Task list container #task-list not found.");
            return;
        }
        taskListContainer.innerHTML = '<h2>Tasks</h2>'; // Reset content
        if (!tasks || tasks.length === 0) {
            taskListContainer.innerHTML += '<p>No tasks available.</p>';
            return;
        }

        const list = document.createElement('ul');
        list.className = 'list-group';
        tasks.forEach(task => {
            const item = document.createElement('li');
            item.className = 'list-group-item task-item d-flex justify-content-between align-items-center';
            item.innerHTML = `
                <div>
                    <strong>${task.title || 'Untitled Task'}</strong> - <span class="badge bg-${task.status === 'completed' ? 'success' : task.status === 'pending' ? 'warning' : 'secondary'} rounded-pill">${task.status || 'unknown'}</span>
                    <p>${task.description || 'No description'}</p>
                    <small>Assigned to: ${task.agent || 'None'} | ID: ${task.id}</small>
                </div>
                <button class="btn btn-danger btn-sm delete-task-btn" data-id="${task.id}">Delete</button>
            `;
            list.appendChild(item);
        });
        taskListContainer.appendChild(list);

        // Attach event listeners to delete buttons
        document.querySelectorAll('.delete-task-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const taskId = e.target.getAttribute('data-id');
                await deleteTask(taskId);
            });
        });
    }

    // Function to fetch tasks from API
    async function fetchTasks() {
        try {
            const response = await fetch('/api/v1/tasks');
            if (!response.ok) {
                // Display error message if fetch fails
                const errorText = await response.text();
                taskListContainer.innerHTML = `<h2>Tasks</h2><p class="text-danger">Error fetching tasks: ${response.status} ${response.statusText}. ${errorText || ''}</p>`;
                return;
            }
            const tasks = await response.json();
            renderTasks(tasks);
        } catch (error) {
            console.error('Failed to fetch or render tasks:', error);
            // Display error message if fetch fails
            taskListContainer.innerHTML = `<h2>Tasks</h2><p class="text-danger">Failed to fetch tasks: ${error.message}</p>`;
        }
    }

    // Function to populate agent dropdown
    async function populateAgentDropdown() {
        try {
            const response = await fetch('/api/v1/agents');
            if (!response.ok) {
                console.error(`Error fetching agents for dropdown: ${response.status} ${response.statusText}`);
                showNotification(`Error fetching agents: ${response.statusText}`, 'error');
                return;
            }
            const agents = await response.json();
            taskAgentSelect.innerHTML = '<option value="">Select an agent</option>';
            agents.forEach(agent => {
                const option = document.createElement('option');
                option.value = agent.name;
                option.textContent = agent.name;
                taskAgentSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to fetch agents for dropdown:', error);
            showNotification(`Failed to fetch agents: ${error.message}`, 'error');
        }
    }

    // Function to create a new task
    async function createTask(title, description, agent) {
        try {
            const taskData = {
                title: title,
                description: description,
                agent: agent || null
            };
            const response = await fetch('/api/v1/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                console.error(`Error creating task: ${response.status}`, errorData);
                showNotification(`Failed to create task: ${errorData.detail || response.statusText}`, 'error');
                return false;
            }
            const newTask = await response.json();
            showNotification(`Task "${newTask.title}" created successfully.`, 'success');
            // Refresh task list immediately
            await fetchTasks();
            return true;
        } catch (error) {
            console.error('Failed to create task:', error);
            showNotification(`Failed to create task: ${error.message}`, 'error');
            return false;
        }
    }

    // Function to delete a task
    async function deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }
        try {
            const response = await fetch(`/api/v1/tasks/${taskId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                console.error(`Error deleting task: ${response.status}`, errorData);
                showNotification(`Failed to delete task ${taskId}: ${errorData.detail || response.statusText}`, 'error');
                return;
            }
            showNotification(`Task ${taskId} deleted successfully.`, 'success');
            // Refresh task list immediately
            await fetchTasks();
        } catch (error) {
            console.error('Failed to delete task:', error);
            showNotification(`Failed to delete task ${taskId}: ${error.message}`, 'error');
        }
    }

    // Event listener for task form submission
    if (taskForm) {
        taskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('task-title').value;
            const description = document.getElementById('task-description').value;
            const agent = document.getElementById('task-agent').value;
            const success = await createTask(title, description, agent);
            if (success) {
                // Clear form on success
                taskForm.reset();
            }
        });
    } else {
        console.warn("Task form #task-form not found.");
    }

    // Initial setup
    if (taskListContainer) {
        fetchTasks();
        setInterval(fetchTasks, 10000); // Refresh tasks every 10 seconds
    } else {
        console.warn("Task list container #task-list not found, skipping task updates.");
    }

    // WebSocket connection for real-time updates
    function setupWebSocket() {
        const wsProtocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${wsProtocol}${location.host}/ws/events`;
        console.log(`Connecting WebSocket to: ${wsUrl}`);
        let ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Task WebSocket connection established.');
            showNotification('Real-time updates connected.', 'info');
        };

        ws.onmessage = (msg) => {
            try {
                const eventData = JSON.parse(msg.data);
                // Check if it's a task update event
                if (eventData.type === 'task_update') {
                    console.log('Task update received via WebSocket:', eventData.data);
                    showNotification(`Task ${eventData.data.id} updated: ${eventData.data.status}`, 'info');
                    // Refresh the entire task list on any task update for simplicity
                    // A more sophisticated approach would update only the changed task
                    fetchTasks();
                }
            } catch (e) {
                console.error('Failed to parse WebSocket message:', e);
            }
        };

        ws.onerror = (error) => {
            console.error('Task WebSocket error:', error);
            showNotification('WebSocket connection error.', 'error');
        };

        ws.onclose = (event) => {
            console.log(`Task WebSocket connection closed. Code: ${event.code}. Reconnecting...`);
            showNotification('Real-time updates disconnected. Attempting to reconnect...', 'warning');
            // Simple reconnect attempt
            setTimeout(setupWebSocket, 5000);
        };
    }

    if (window.WebSocket) {
        setupWebSocket();
    } else {
        console.error('WebSockets are not supported by your browser.');
        showNotification('WebSockets not supported by your browser.', 'error');
    }

    if (taskAgentSelect) {
        populateAgentDropdown();
    } else {
        console.warn("Task agent select #task-agent not found.");
    }

})();
