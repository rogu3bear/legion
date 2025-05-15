// js_feed.js - Legion static feed stub

(function() {
    function renderEvent(event) {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.textContent = JSON.stringify(event);
        return card;
    }
    function appendEvent(event) {
        document.getElementById('feed').appendChild(renderEvent(event));
    }
    function startWebSocket() {
        let ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/events');
        ws.onmessage = (msg) => {
            try { appendEvent(JSON.parse(msg.data)); } catch {}
        };
        ws.onerror = ws.onclose = () => { setTimeout(() => location.reload(), 2000); };
    }
    if (window.WebSocket) {
        startWebSocket();
    }
})();
