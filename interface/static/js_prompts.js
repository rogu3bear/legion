/**
 * Legion Prompt Management & LM Studio Chat Interface
 * Frontend JavaScript for managing agent prompts and testing with LM Studio
 * Now with JWT authentication support
 */

class PromptManager {
    constructor() {
        this.currentAgent = null;
        this.originalPrompt = null;
        this.chatHistory = [];
        this.currentUser = null;
        this.init();
    }

    init() {
        // Check if user is already logged in
        const token = localStorage.getItem('legion_token');
        if (token) {
            this.validateTokenAndInit();
        } else {
            this.showLoginForm();
        }
    }

    async validateTokenAndInit() {
        try {
            const response = await fetch('/api/v1/auth/me', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.currentUser = await response.json();
                this.showMainContent();
                this.bindEvents();
                this.loadAgents();
                this.checkLMStudioStatus();

                // Check LM Studio status periodically
                setInterval(() => this.checkLMStudioStatus(), 30000);
            } else {
                // Token is invalid
                localStorage.removeItem('legion_token');
                this.showLoginForm();
            }
        } catch (error) {
            console.error('Token validation failed:', error);
            localStorage.removeItem('legion_token');
            this.showLoginForm();
        }
    }

    showLoginForm() {
        document.getElementById('auth-overlay').classList.remove('hidden');
        document.getElementById('main-content').classList.add('hidden');
        this.bindLoginEvents();
    }

    showMainContent() {
        document.getElementById('auth-overlay').classList.add('hidden');
        document.getElementById('main-content').classList.remove('hidden');

        // Update user info
        if (this.currentUser) {
            document.getElementById('user-info').textContent = `Welcome, ${this.currentUser.username}`;
        }
    }

    bindLoginEvents() {
        const loginForm = document.getElementById('login-form');
        const loginBtn = document.getElementById('login-btn');
        const loginError = document.getElementById('login-error');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            loginError.classList.add('hidden');

            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);

                const response = await fetch('/api/v1/auth/login', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('legion_token', data.access_token);
                    await this.validateTokenAndInit();
                } else {
                    const errorData = await response.json();
                    loginError.textContent = errorData.detail || 'Login failed';
                    loginError.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Login error:', error);
                loginError.textContent = 'Network error. Please try again.';
                loginError.classList.remove('hidden');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Login';
            }
        });
    }

    bindEvents() {
        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // Prompt editor events
        document.getElementById('agent-select').addEventListener('change', (e) => {
            this.selectAgent(e.target.value);
        });

        document.getElementById('prompt-editor').addEventListener('input', () => {
            this.enableSaveButton();
        });

        document.getElementById('btn-save-prompt').addEventListener('click', () => {
            this.savePrompt();
        });

        document.getElementById('btn-new-prompt').addEventListener('click', () => {
            this.showNewPromptModal();
        });

        document.getElementById('btn-create-prompt').addEventListener('click', () => {
            this.createNewPrompt();
        });

        // Chat interface events
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        document.getElementById('btn-send-chat').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('btn-clear-chat').addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('btn-test-prompt').addEventListener('click', () => {
            this.testCurrentPrompt();
        });
    }

    logout() {
        localStorage.removeItem('legion_token');
        this.currentUser = null;
        this.showLoginForm();
        this.showNotification('Logged out successfully', 'info');
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/v1/prompts/', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.populateAgentSelect(data.agents);
            } else if (response.status === 401) {
                this.handleUnauthorized();
            } else {
                this.showNotification('Failed to load agents', 'error');
            }
        } catch (error) {
            console.error('Error loading agents:', error);
            this.showNotification('Error loading agents', 'error');
        }
    }

    populateAgentSelect(agents) {
        const select = document.getElementById('agent-select');
        select.innerHTML = '<option value="">Select an agent...</option>';

        agents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent;
            option.textContent = agent;
            select.appendChild(option);
        });
    }

    async selectAgent(agentName) {
        if (!agentName) {
            this.clearEditor();
            return;
        }

        try {
            const response = await fetch(`/api/v1/prompts/${agentName}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.loadPromptIntoEditor(agentName, data.content);
            } else if (response.status === 401) {
                this.handleUnauthorized();
            } else if (response.status === 404) {
                this.loadPromptIntoEditor(agentName, this.getDefaultPromptTemplate(agentName));
            } else {
                this.showNotification('Failed to load prompt', 'error');
            }
        } catch (error) {
            console.error('Error loading prompt:', error);
            this.showNotification('Error loading prompt', 'error');
        }
    }

    loadPromptIntoEditor(agentName, content) {
        this.currentAgent = agentName;
        this.originalPrompt = content;

        const editor = document.getElementById('prompt-editor');
        editor.value = content;
        editor.disabled = false;

        this.updateStatus(`Loaded prompt for ${agentName}`);
        this.disableSaveButton();
        this.enableTestButton();
    }

    clearEditor() {
        this.currentAgent = null;
        this.originalPrompt = null;

        const editor = document.getElementById('prompt-editor');
        editor.value = '';
        editor.disabled = true;

        this.updateStatus('Select an agent to edit its prompt');
        this.disableSaveButton();
        this.disableTestButton();
    }

    enableSaveButton() {
        const saveBtn = document.getElementById('btn-save-prompt');
        const editor = document.getElementById('prompt-editor');

        saveBtn.disabled = !this.currentAgent || editor.value === this.originalPrompt;
    }

    disableSaveButton() {
        document.getElementById('btn-save-prompt').disabled = true;
    }

    enableTestButton() {
        const testBtn = document.getElementById('btn-test-prompt');
        testBtn.disabled = !this.currentAgent;
    }

    disableTestButton() {
        document.getElementById('btn-test-prompt').disabled = true;
    }

    async savePrompt() {
        if (!this.currentAgent) return;

        const content = document.getElementById('prompt-editor').value;
        const saveBtn = document.getElementById('btn-save-prompt');

        // Disable save button and show loading state
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        try {
            const response = await fetch(`/api/v1/prompts/${this.currentAgent}`, {
                method: 'PUT',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });

            if (response.ok) {
                this.originalPrompt = content;
                this.showNotification('Prompt saved successfully', 'success');
                this.updateStatus(`Saved prompt for ${this.currentAgent}`);
            } else if (response.status === 401) {
                this.handleUnauthorized();
            } else {
                this.showNotification('Failed to save prompt', 'error');
            }
        } catch (error) {
            console.error('Error saving prompt:', error);
            this.showNotification('Error saving prompt', 'error');
        } finally {
            saveBtn.textContent = 'Save';
            this.enableSaveButton(); // Re-evaluate if save should be enabled
        }
    }

    showNewPromptModal() {
        const modal = new bootstrap.Modal(document.getElementById('newPromptModal'));
        document.getElementById('new-agent-name').value = '';
        modal.show();
    }

    async createNewPrompt() {
        const agentName = document.getElementById('new-agent-name').value.trim();

        if (!agentName) {
            this.showNotification('Please enter an agent name', 'warning');
            return;
        }

        const content = this.getDefaultPromptTemplate(agentName);

        try {
            const response = await fetch('/api/v1/prompts/', {
                method: 'POST',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ agent_name: agentName, content })
            });

            if (response.ok) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('newPromptModal'));
                modal.hide();

                // Reload agents and select the new one
                await this.loadAgents();
                document.getElementById('agent-select').value = agentName;
                await this.selectAgent(agentName);

                this.showNotification('New prompt created successfully', 'success');
            } else if (response.status === 401) {
                this.handleUnauthorized();
            } else if (response.status === 409) {
                this.showNotification('Prompt already exists for this agent', 'warning');
            } else {
                this.showNotification('Failed to create prompt', 'error');
            }
        } catch (error) {
            console.error('Error creating prompt:', error);
            this.showNotification('Error creating prompt', 'error');
        }
    }

    getDefaultPromptTemplate(agentName) {
        return `# ${agentName.charAt(0).toUpperCase() + agentName.slice(1)} Prompt Template

**Description:**
(Brief overview of this agent's role.)

**System Instructions:**
- (High-level directives for model behavior.)

**Examples:**
- **User:** …
- **Assistant:** …
`;
    }

    // LM Studio Chat Interface

    async checkLMStudioStatus() {
        try {
            const response = await fetch('/api/v1/lmstudio/echo', {
                method: 'POST',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: [{ role: 'user', content: 'ping' }],
                    max_tokens: 1
                })
            });

            if (response.ok) {
                this.setLMStudioStatus(true);
            } else {
                this.setLMStudioStatus(false);
            }
        } catch (error) {
            this.setLMStudioStatus(false);
        }
    }

    setLMStudioStatus(online) {
        const statusText = document.getElementById('lm-status-text');
        const statusIndicator = document.getElementById('lm-status-indicator');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('btn-send-chat');

        if (online) {
            statusText.textContent = 'Online';
            statusIndicator.className = 'status-indicator status-online';
            chatInput.disabled = false;
            sendBtn.disabled = false;
        } else {
            statusText.textContent = 'Offline';
            statusIndicator.className = 'status-indicator status-offline';
            chatInput.disabled = true;
            sendBtn.disabled = true;
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addChatMessage('user', message);
        input.value = '';

        // Prepare messages for LM Studio
        const messages = this.chatHistory.map(msg => ({
            role: msg.role,
            content: msg.content
        }));

        try {
            this.setLoading(true);

            const response = await fetch('/api/v1/lmstudio/chat', {
                method: 'POST',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 2048
                })
            });

            if (response.ok) {
                const data = await response.json();
                const assistantMessage = data.choices[0].message.content;
                this.addChatMessage('assistant', assistantMessage);
            } else if (response.status === 401) {
                this.handleUnauthorized();
            } else {
                this.addChatMessage('system', 'Error: Failed to get response from LM Studio');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addChatMessage('system', 'Error: Failed to connect to LM Studio');
        } finally {
            this.setLoading(false);
        }
    }

    async testCurrentPrompt() {
        if (!this.currentAgent) return;

        const promptContent = document.getElementById('prompt-editor').value;

        if (!promptContent.trim()) {
            this.showNotification('No prompt content to test', 'warning');
            return;
        }

        // Clear chat and add system message with current prompt
        this.clearChat();
        this.addChatMessage('system', `Testing prompt for ${this.currentAgent}:\n\n${promptContent}`);

        this.showNotification('Prompt loaded into chat - send a message to test', 'info');
    }

    addChatMessage(role, content) {
        const container = document.getElementById('chat-container');

        // Add to history
        this.chatHistory.push({ role, content });

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.textContent = content;

        const roleLabel = document.createElement('small');
        roleLabel.className = 'text-muted';
        roleLabel.textContent = role.toUpperCase();

        messageDiv.appendChild(roleLabel);
        messageDiv.appendChild(contentDiv);

        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }

    clearChat() {
        this.chatHistory = [];
        const container = document.getElementById('chat-container');
        container.innerHTML = '<div class="text-center text-muted">Chat cleared - ready for new conversation</div>';
    }

    setLoading(loading) {
        const sendBtn = document.getElementById('btn-send-chat');
        const chatInput = document.getElementById('chat-input');

        if (loading) {
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            chatInput.disabled = true;
        } else {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            chatInput.disabled = false;
        }
    }

    // Utility methods

    getAuthHeaders() {
        const token = localStorage.getItem('legion_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    handleUnauthorized() {
        localStorage.removeItem('legion_token');
        this.currentUser = null;
        this.showLoginForm();
        this.showNotification('Session expired. Please log in again.', 'warning');
    }

    updateStatus(message) {
        document.getElementById('prompt-status').textContent = message;
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');

        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PromptManager();
});
