package developer

import (
	"context"
	"encoding/json"
	"testing"
	"time"
)

func TestNewAgent(t *testing.T) {
	agent := NewAgent("test_dev")

	if agent.name != "test_dev" {
		t.Errorf("Expected agent name to be 'test_dev', got '%s'", agent.name)
	}

	if len(agent.skills) != 0 {
		t.Errorf("Expected 0 skills, got %d", len(agent.skills))
	}

	if agent.active {
		t.Error("Expected new agent to be inactive")
	}
}

func TestAgentLifecycle(t *testing.T) {
	agent := NewAgent("lifecycle_test")

	// Test Start
	err := agent.Start()
	if err != nil {
		t.Errorf("Unexpected error starting agent: %v", err)
	}

	if !agent.active {
		t.Error("Expected agent to be active after start")
	}

	// Test double start
	err = agent.Start()
	if err == nil {
		t.Error("Expected error when starting already running agent")
	}

	// Test message handling
	payload, _ := json.Marshal(map[string]interface{}{"content": "test content"})
	msg := Message{
		ID:      "test_msg",
		Type:    "code_review",
		Payload: payload,
	}

	agent.msgChan <- msg
	time.Sleep(100 * time.Millisecond) // Allow time for message processing

	// Test Stop
	err = agent.Stop()
	if err != nil {
		t.Errorf("Unexpected error stopping agent: %v", err)
	}
	if agent.active {
		t.Error("Expected agent to be inactive after stop")
	}
}

func TestStatus(t *testing.T) {
	agent := NewAgent("status_test")
	status := agent.Status()

	if status["name"] != "status_test" {
		t.Errorf("Expected status name to be 'status_test', got '%v'", status["name"])
	}

	if status["active"].(bool) != false {
		t.Error("Expected status active to be false")
	}

	skills := status["skills"].(int)
	if skills != 0 {
		t.Errorf("Expected 0 skills in status, got %d", skills)
	}
}

func TestMessageHandling(t *testing.T) {
	agent := NewAgent("message_test")
	err := agent.Start()
	if err != nil {
		t.Fatalf("Failed to start agent: %v", err)
	}

	testCases := []struct {
		name    string
		msgType string
		wantErr bool
	}{
		{"code review", "code_review", false},
		{"refactor", "refactor", false},
		{"debug", "debug", false},
		{"unknown", "unknown_type", true},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			payload, _ := json.Marshal(map[string]interface{}{"content": "test content"})
			msg := Message{
				ID:      "test_" + tc.name,
				Type:    tc.msgType,
				Payload: payload,
			}

			agent.msgChan <- msg
			time.Sleep(50 * time.Millisecond) // Allow time for message processing
		})
	}

	err = agent.Stop()
	if err != nil {
		t.Errorf("Unexpected error stopping agent: %v", err)
	}
}

func TestNewDeveloper(t *testing.T) {
	name := "test_developer"
	dev := NewDeveloper(name)

	if dev == nil {
		t.Fatal("Expected non-nil Developer instance")
	}

	if dev.Name != name {
		t.Errorf("Expected name %s, got %s", name, dev.Name)
	}

	if dev.logger == nil {
		t.Error("Expected non-nil logger")
	}
}

func TestDeveloperLifecycle(t *testing.T) {
	dev := NewDeveloper("test_developer")
	ctx := context.Background()

	// Test Initialize
	if err := dev.Initialize(ctx); err != nil {
		t.Errorf("Initialize failed: %v", err)
	}

	// Test Execute
	if err := dev.Execute(ctx); err != nil {
		t.Errorf("Execute failed: %v", err)
	}

	// Test Shutdown
	if err := dev.Shutdown(ctx); err != nil {
		t.Errorf("Shutdown failed: %v", err)
	}
}
