// js_tasks.js - Legion Task Management UI

document.addEventListener('DOMContentLoaded', () => {
    const taskListContainer = document.getElementById('task-list-container');
    const taskForm = document.getElementById('task-form');
    const taskAgentSelect = document.getElementById('task-agent');
    const notificationContainer = document.getElementById('notification-container');
    const refreshTasksButton = document.getElementById('refresh-tasks-btn');
    const filterStatusSelect = document.getElementById('filter-task-status');
    const filterOwnerInput = document.getElementById('filter-task-owner');

    const API_BASE_URL = '/api/v1/tasks';

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
            console.warn('Task list container #task-list-container not found in DOM.');
            return;
        }
        if (!tasks || tasks.length === 0) {
            taskListContainer.innerHTML = '<p class="text-gray-600">No tasks found matching your criteria.</p>';
            return;
        }

        taskListContainer.innerHTML = tasks.map(task => createTaskElement(task)).join('');
        addEventListenersToTaskButtons();
    }

    function getStatusColor(status) {
        if (!status) return 'bg-gray-300';
        switch (status.toLowerCase()) {
            case 'pending': return 'bg-yellow-500';
            case 'running': return 'bg-blue-500';
            case 'completed': return 'bg-green-500';
            case 'failed': return 'bg-red-500';
            case 'cancelled': return 'bg-gray-500';
            default: return 'bg-gray-300';
        }
    }

    function createTaskElement(task) {
        const tags = task.metadata && task.metadata.tags && Array.isArray(task.metadata.tags) && task.metadata.tags.length > 0 ?
            task.metadata.tags.map(tag => `<span class="tag-chip">${tag}</span>`).join(' ') :
            '<span class="tag-chip tag-unset">No Tags</span>';

        const owner = task.agent_id ? task.agent_id : '<span class="text-gray-500">Unassigned</span>';
        const taskIdShort = task.id ? task.id.substring(0, 8) : 'N/A';

        return `
            <div class="task-item bg-white p-4 border border-gray-200 rounded-lg mb-3 shadow-sm hover:shadow-md transition-shadow duration-200" id="task-${task.id}">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-lg font-semibold text-gray-800">${task.title || 'Untitled Task'} (ID: ${taskIdShort})</h3>
                    <span class="status-badge ${getStatusColor(task.status)} text-white text-xs font-semibold px-3 py-1 rounded-full">${task.status || 'UNKNOWN'}</span>
                </div>
                <p class="text-sm text-gray-600 mb-1"><strong>Owner:</strong> ${owner}</p>
                <p class="text-sm text-gray-700 mb-2">${task.description || 'No description provided.'}</p>
                <div class="mb-2 text-sm"><strong>Tags:</strong> ${tags}</div>
                <div class="text-xs text-gray-500">
                    Created: ${task.created_at ? new Date(task.created_at).toLocaleString() : 'N/A'}
                    ${task.priority ? `<span class="mx-1">|</span> Priority: ${task.priority}` : ''}
                </div>
                <div class="mt-3 flex justify-end">
                    <button class="delete-task-btn text-red-500 hover:text-red-700 text-xs font-medium py-1 px-2 rounded border border-red-500 hover:bg-red-50 transition-colors duration-150" data-task-id="${task.id}">Delete Task</button>
                </div>
            </div>
        `;
    }

    // Function to fetch tasks from API
    async function fetchTasks(filters = {}) {
        const queryParams = new URLSearchParams();
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.agent) queryParams.append('agent', filters.agent); // agent_id is used as owner

        try {
            const response = await fetch(`${API_BASE_URL}?${queryParams.toString()}`);
            if (!response.ok) {
                console.error('Failed to fetch tasks:', response.status, await response.text());
                if(taskListContainer) taskListContainer.innerHTML = '<p class="text-red-500">Error loading tasks.</p>';
                return [];
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching tasks:', error);
            if(taskListContainer) taskListContainer.innerHTML = '<p class="text-red-500">Error loading tasks.</p>';
            return [];
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
        if (!taskId) {
            console.error('Task ID is undefined, cannot delete.');
            alert('Cannot delete task: Task ID is missing.');
            return;
        }
        if (!confirm(`Are you sure you want to delete task ${taskId.substring(0,8)}...? This will attempt to cancel it.`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/${taskId}`, { method: 'DELETE' });
            if (response.ok) { // 204 No Content is ok
                console.log(`Task ${taskId} deleted/cancelled successfully.`);
                // Optional: show a success message to the user
                document.getElementById(`task-${taskId}`)?.remove(); // Optimistically remove from UI
                // loadAndRenderTasks(); // Or, reload all tasks to confirm from server
            } else {
                const errorText = await response.text();
                console.error(`Failed to delete task ${taskId}:`, response.status, errorText);
                alert(`Failed to delete task: ${errorText || response.statusText}`);
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            alert('An error occurred while trying to delete the task.');
        }
    }

    function addEventListenersToTaskButtons() {
        document.querySelectorAll('.delete-task-btn').forEach(button => {
            // Remove old event listeners to prevent multiple fires if re-rendering
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);

            newButton.addEventListener('click', (event) => {
                const taskId = event.target.dataset.taskId;
                deleteTask(taskId);
            });
        });
    }

    async function loadAndRenderTasks() {
        const statusFilter = filterStatusSelect ? filterStatusSelect.value : '';
        const ownerFilter = filterOwnerInput ? filterOwnerInput.value.trim() : '';

        const filters = {};
        if (statusFilter) filters.status = statusFilter;
        if (ownerFilter) filters.agent = ownerFilter; // 'agent' is the query param for owner

        if(taskListContainer) taskListContainer.innerHTML = '<p class="text-gray-600">Loading tasks...</p>';
        const tasks = await fetchTasks(filters);
        renderTasks(tasks);
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
        loadAndRenderTasks();
        setInterval(loadAndRenderTasks, 10000); // Refresh tasks every 10 seconds
    } else {
        console.info('Task list container #task-list-container not found. Task script will not load initial tasks.');
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
                    loadAndRenderTasks();
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

    if (refreshTasksButton) {
        refreshTasksButton.addEventListener('click', loadAndRenderTasks);
    }
    if (filterStatusSelect) {
        filterStatusSelect.addEventListener('change', loadAndRenderTasks);
    }
    if (filterOwnerInput) {
        filterOwnerInput.addEventListener('input', () => {
            // Basic debounce could be added here if performance becomes an issue
            loadAndRenderTasks();
        });
    }
});
