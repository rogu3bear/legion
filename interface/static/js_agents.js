// js_agents.js - Legion Agent Management UI

(function() {
    // DOM Elements
    const agentListEl = document.getElementById('agent-list');
    const agentDetailsEl = document.getElementById('agent-details');
    const selectedAgentNameEl = document.getElementById('selected-agent-name');
    const agentStatusDetailsEl = document.getElementById('agent-status-details');
    const agentStatsEl = document.getElementById('agent-stats');
    const agentHistoryEl = document.getElementById('agent-history');

    // Configuration Elements
    const configDisplayEl = document.getElementById('config-display');
    const configDisplayContainerEl = document.getElementById('config-display-container');
    const configEditorEl = document.getElementById('config-editor');
    const configEditorContainerEl = document.getElementById('config-editor-container');

    // Buttons
    const btnEditConfig = document.getElementById('btn-edit-config');
    const btnSaveConfig = document.getElementById('btn-save-config');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const btnStartAgent = document.getElementById('btn-start-agent');
    const btnStopAgent = document.getElementById('btn-stop-agent');
    const btnRestartAgent = document.getElementById('btn-restart-agent');
    const btnReloadAgent = document.getElementById('btn-reload-agent');

    // Current state
    let currentAgentName = null;
    let currentConfig = null;
    let agents = [];

    // Function to show a notification
    function showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
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

        container.appendChild(notification);

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

    // Function to render agent list
    function renderAgentList(agents) {
        if (!agentListEl) return;

        agentListEl.innerHTML = '';

        if (!agents || agents.length === 0) {
            agentListEl.innerHTML = '<p class="text-center">No agents available.</p>';
            return;
        }

        const list = document.createElement('div');
        list.className = 'list-group';

        agents.forEach(agent => {
            const statusBadgeClass = agent.status === 'running' ? 'bg-success' :
                                     agent.status === 'stopped' ? 'bg-danger' :
                                     agent.status === 'error' ? 'bg-warning' : 'bg-secondary';

            const item = document.createElement('a');
            item.href = '#';
            item.className = `list-group-item list-group-item-action d-flex justify-content-between align-items-center${currentAgentName === agent.name ? ' active' : ''}`;
            item.innerHTML = `
                <div>
                    <strong>${agent.name}</strong>
                    <span class="badge ${statusBadgeClass} agent-status-badge">${agent.status}</span>
                </div>
                <small>${agent.type || 'Unknown type'}</small>
            `;

            item.addEventListener('click', (e) => {
                e.preventDefault();
                loadAgentDetails(agent.name);
            });

            list.appendChild(item);
        });

        agentListEl.appendChild(list);
    }

    // Function to fetch agent list
    async function fetchAgents() {
        try {
            const response = await fetch('/api/v1/agents');
            if (!response.ok) {
                throw new Error(`Error fetching agents: ${response.status} ${response.statusText}`);
            }
            agents = await response.json();
            renderAgentList(agents);
            return agents;
        } catch (error) {
            console.error('Failed to fetch agents:', error);
            showNotification(`Failed to fetch agents: ${error.message}`, 'error');
            return [];
        }
    }

    // Function to load agent details
    async function loadAgentDetails(agentName) {
        if (!agentName) return;

        currentAgentName = agentName;

        // Update UI to show the selected agent is being loaded
        agentDetailsEl.classList.remove('d-none');
        selectedAgentNameEl.textContent = agentName;
        agentStatusDetailsEl.innerHTML = '<p>Loading status...</p>';
        agentStatsEl.innerHTML = '<p>Loading stats...</p>';
        configDisplayEl.textContent = 'Loading configuration...';
        agentHistoryEl.innerHTML = '<p>Loading history...</p>';

        // Re-render agent list to highlight the selected agent
        renderAgentList(agents);

        // Fetch agent details
        try {
            const response = await fetch(`/api/v1/agents/${agentName}`);
            if (!response.ok) {
                throw new Error(`Error fetching agent details: ${response.status} ${response.statusText}`);
            }
            const agentDetails = await response.json();

            // Update status and stats
            renderAgentStatusDetails(agentDetails);
            renderAgentStats(agentDetails);

            // Fetch configuration
            await fetchAgentConfig(agentName);

            // Fetch history (if available)
            await fetchAgentHistory(agentName);
        } catch (error) {
            console.error(`Failed to load details for agent ${agentName}:`, error);
            showNotification(`Failed to load agent details: ${error.message}`, 'error');
        }
    }

    // Function to render agent status details
    function renderAgentStatusDetails(agentDetails) {
        const statusBadgeClass = agentDetails.status === 'running' ? 'bg-success' :
                                agentDetails.status === 'stopped' ? 'bg-danger' :
                                agentDetails.status === 'error' ? 'bg-warning' : 'bg-secondary';

        agentStatusDetailsEl.innerHTML = `
            <div class="mb-3">
                <span class="badge ${statusBadgeClass} fs-6">${agentDetails.status}</span>
            </div>
            <p><strong>Type:</strong> ${agentDetails.type || 'Unknown'}</p>
            <p><strong>Last updated:</strong> ${new Date(agentDetails.last_updated || Date.now()).toLocaleString()}</p>
            ${agentDetails.error ? `<div class="alert alert-danger mt-2"><strong>Error:</strong> ${agentDetails.error}</div>` : ''}
        `;
    }

    // Function to render agent stats
    function renderAgentStats(agentDetails) {
        const stats = agentDetails.stats || {};

        agentStatsEl.innerHTML = `
            <p><strong>Messages handled:</strong> ${stats.messages_handled || 0}</p>
            <p><strong>Tasks completed:</strong> ${stats.tasks_completed || 0}</p>
            <p><strong>Average response time:</strong> ${stats.avg_response_time ? `${stats.avg_response_time}ms` : 'N/A'}</p>
            <p><strong>Memory usage:</strong> ${stats.memory_usage || 'N/A'}</p>
        `;
    }

    // Function to fetch agent configuration
    async function fetchAgentConfig(agentName) {
        try {
            const response = await fetch(`/api/v1/agents/${agentName}/config`);
            if (!response.ok) {
                throw new Error(`Error fetching agent configuration: ${response.status} ${response.statusText}`);
            }
            currentConfig = await response.json();

            // Display the configuration as formatted YAML or JSON
            configDisplayEl.textContent = JSON.stringify(currentConfig, null, 2);
        } catch (error) {
            console.error(`Failed to fetch configuration for agent ${agentName}:`, error);
            configDisplayEl.textContent = `Error loading configuration: ${error.message}`;
            currentConfig = null;
        }
    }

    // Function to fetch agent history
    async function fetchAgentHistory(agentName) {
        try {
            const response = await fetch(`/api/v1/agents/${agentName}/history`);
            if (!response.ok) {
                // If endpoint doesn't exist yet, show placeholder
                if (response.status === 404) {
                    agentHistoryEl.innerHTML = '<p class="text-muted">History functionality not available yet.</p>';
                    return;
                }
                throw new Error(`Error fetching agent history: ${response.status} ${response.statusText}`);
            }
            const history = await response.json();

            if (!history || history.length === 0) {
                agentHistoryEl.innerHTML = '<p class="text-muted">No history available for this agent.</p>';
                return;
            }

            // Render history as a table or list
            const historyList = document.createElement('ul');
            historyList.className = 'list-group';

            history.slice(0, 10).forEach(entry => {
                const item = document.createElement('li');
                item.className = 'list-group-item';
                item.innerHTML = `
                    <div class="d-flex justify-content-between">
                        <small>${new Date(entry.timestamp).toLocaleString()}</small>
                        <span class="badge bg-${entry.type === 'error' ? 'danger' : entry.type === 'success' ? 'success' : 'info'}">${entry.type}</span>
                    </div>
                    <p class="mb-0">${entry.message}</p>
                `;
                historyList.appendChild(item);
            });

            agentHistoryEl.innerHTML = '';
            agentHistoryEl.appendChild(historyList);
        } catch (error) {
            console.error(`Failed to fetch history for agent ${agentName}:`, error);
            agentHistoryEl.innerHTML = '<p class="text-muted">History not available.</p>';
        }
    }

    // Function to start editing configuration
    function startEditingConfig() {
        if (!currentConfig) return;

        // Set the editor value to the current configuration
        configEditorEl.value = JSON.stringify(currentConfig, null, 2);

        // Show editor, hide display
        configDisplayContainerEl.classList.add('d-none');
        configEditorContainerEl.classList.remove('d-none');

        // Show save/cancel buttons, hide edit button
        btnEditConfig.classList.add('d-none');
        btnSaveConfig.classList.remove('d-none');
        btnCancelEdit.classList.remove('d-none');

        // Focus the editor
        configEditorEl.focus();
    }

    // Function to cancel editing
    function cancelEditing() {
        // Hide editor, show display
        configDisplayContainerEl.classList.remove('d-none');
        configEditorContainerEl.classList.add('d-none');

        // Hide save/cancel buttons, show edit button
        btnEditConfig.classList.remove('d-none');
        btnSaveConfig.classList.add('d-none');
        btnCancelEdit.classList.add('d-none');
    }

    // Function to save configuration
    async function saveConfiguration() {
        if (!currentAgentName) return;

        try {
            // Parse the edited configuration
            const newConfig = JSON.parse(configEditorEl.value);

            // Send the update to the server
            const response = await fetch(`/api/v1/agents/${currentAgentName}/config`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newConfig)
            });

            if (!response.ok) {
                throw new Error(`Error updating configuration: ${response.status} ${response.statusText}`);
            }

            // Update currentConfig and display
            currentConfig = newConfig;
            configDisplayEl.textContent = JSON.stringify(currentConfig, null, 2);

            // Exit edit mode
            cancelEditing();

            // Show success notification
            showNotification(`Configuration for ${currentAgentName} updated successfully.`, 'success');

            // Refresh agent details to show any changes
            await loadAgentDetails(currentAgentName);
        } catch (error) {
            console.error(`Failed to update configuration for agent ${currentAgentName}:`, error);
            showNotification(`Failed to update configuration: ${error.message}`, 'error');
        }
    }

    // Function to control agent (start, stop, restart, reload)
    async function controlAgent(action) {
        if (!currentAgentName) return;

        try {
            // Send the control action to the server
            const response = await fetch(`/api/v1/agents/${currentAgentName}/${action}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Error ${action} agent: ${response.status} ${response.statusText}`);
            }

            // Show success notification
            const actionDisplay = action.charAt(0).toUpperCase() + action.slice(1);
            showNotification(`${actionDisplay} operation for ${currentAgentName} successful.`, 'success');

            // Wait a moment for the agent to change status, then refresh
            setTimeout(async () => {
                await fetchAgents();
                await loadAgentDetails(currentAgentName);
            }, 1000);
        } catch (error) {
            console.error(`Failed to ${action} agent ${currentAgentName}:`, error);
            showNotification(`Failed to ${action} agent: ${error.message}`, 'error');
        }
    }

    // Initial setup: fetch agents and set up event listeners
    fetchAgents();

    // Set up interval to refresh agent list
    setInterval(fetchAgents, 10000);

    // Set up event listeners for buttons
    if (btnEditConfig) {
        btnEditConfig.addEventListener('click', startEditingConfig);
    }

    if (btnCancelEdit) {
        btnCancelEdit.addEventListener('click', cancelEditing);
    }

    if (btnSaveConfig) {
        btnSaveConfig.addEventListener('click', saveConfiguration);
    }

    if (btnStartAgent) {
        btnStartAgent.addEventListener('click', () => controlAgent('start'));
    }

    if (btnStopAgent) {
        btnStopAgent.addEventListener('click', () => controlAgent('stop'));
    }

    if (btnRestartAgent) {
        btnRestartAgent.addEventListener('click', () => controlAgent('restart'));
    }

    if (btnReloadAgent) {
        btnReloadAgent.addEventListener('click', () => controlAgent('reload'));
    }

    // Listen for WebSocket updates if available
    if (window.WebSocket) {
        const wsProtocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${wsProtocol}${location.host}/ws/events`;

        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Handle agent status updates
                if (data.type === 'agent_status_update') {
                    agents = data.data || [];
                    renderAgentList(agents);

                    // If we're currently viewing an agent whose status changed, refresh the details
                    if (currentAgentName && agents.some(a => a.name === currentAgentName)) {
                        loadAgentDetails(currentAgentName);
                    }
                }
            } catch (error) {
                console.error('Error processing WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed. Attempting to reconnect...');
            setTimeout(() => {
                if (window.location.pathname.includes('/agents')) {
                    window.location.reload();
                }
            }, 5000);
        };
    }
})();
