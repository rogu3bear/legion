#!/usr/bin/env python3
import re

def fix_orchestrator_syntax():
    with open('legion/orchestrator/__init__.py', 'r') as f:
        content = f.read()

    # Apply comprehensive fixes for all known patterns
    fixes = [
        # Fix logger.error calls with missing commas
        (r'logger\.error\(\s*\n\s*f\"([^\"]*)\"\s*\n\s*exc_info=True', r'logger.error(\n                    f"\1",\n                    exc_info=True'),
        
        # Fix dictionary entries missing commas - more specific patterns
        (r'"detail": "Orchestrator is running"\s*\n\s*"pid":', r'"detail": "Orchestrator is running",\n            "pid":'),
        (r'"pid": os\.getpid\(\)\s*\n\s*"active_agents":', r'"pid": os.getpid(),\n            "active_agents":'),
        (r'"status": "success"\s*\n\s*"detail":', r'"status": "success",\n            "detail":'),
        (r'"detail": "Memory system statistics \(placeholder\)"\s*\n\s*"total_documents":', r'"detail": "Memory system statistics (placeholder)",\n            "total_documents":'),
        (r'"total_documents": 0\s*\n\s*"total_size_mb":', r'"total_documents": 0,\n            "total_size_mb":'),
        (r'"total_size_mb": 0\s*\n\s*"vector_db_status":', r'"total_size_mb": 0,\n            "vector_db_status":'),
        (r'"id": str\(task_id\)\s*\n\s*"status": "pending"', r'"id": str(task_id),\n            "status": "pending"'),
        (r'"status": "pending"\s*\n\s*"title": "Dummy Task"', r'"status": "pending",\n            "title": "Dummy Task"'),
        (r'"cpu_usage_percent": 0\.0\s*\n\s*"memory_usage_mb":', r'"cpu_usage_percent": 0.0,\n                "memory_usage_mb":'),
        (r'"memory_usage_mb": 0\.0\s*\n\s*"pid":', r'"memory_usage_mb": 0.0,\n                "pid":'),
        
        # Fix function call parameters missing commas  
        (r'prompt=prompt\s*\n\s*response=response', r'prompt=prompt,\n                        response=response'),
        (r'response=response\s*\n\s*context=context', r'response=response,\n                        context=context'),
        (r'mentioned\s*\n\s*f"Mentioned by', r'mentioned,\n                        f"Mentioned by'),
        (r'payload\.get\("from", "\?"\)\s*\n\s*payload\.get\("title"', r'payload.get("from", "?"),\n                    payload.get("title"'),
        (r'to_agent\s*\n\s*f"New message from', r'to_agent,\n                    f"New message from'),
        
        # Fix specific dictionary patterns
        (r'"id": message_id\s*\n\s*"agent": agent_name', r'"id": message_id,\n            "agent": agent_name'),
        (r'"agent": agent_name\s*\n\s*"content": content,', r'"agent": agent_name,\n            "content": content,'),
        (r'"directive": content,\s*\n\s*"author"', r'"directive": content,\n            "author"'),
        (r'"author": author or "N/A"\s*\n\s*"timestamp"', r'"author": author or "N/A",\n            "timestamp"'),
        (r'"original_content": content,\s*\n\s*"response_content":', r'"original_content": content,\n                "response_content":'),
        (r'"response_content": response_content\s*\n\s*"author":', r'"response_content": response_content,\n                "author":'),
        (r'"author": "agent:" \+ agent_name\s*\n\s*"timestamp"', r'"author": "agent:" + agent_name,\n                "timestamp"'),
        
        # Fix Task constructor
        (r'id=str\(new_task_id\)\s*\n\s*agent=agent_name', r'id=str(new_task_id),\n            agent=agent_name'),
        (r'agent=agent_name\s*\n\s*payload=payload', r'agent=agent_name,\n            payload=payload'),
        (r'id=str\(uuid\.uuid4\(\)\)\s*\n\s*agent=agent_name', r'id=str(uuid.uuid4()),\n            agent=agent_name'),
        (r'payload=\{"content": build_intro\(agent_name\), "intro": True\}\s*\n\s*\)', r'payload={"content": build_intro(agent_name), "intro": True},\n        )'),
        (r'payload=\{"directive": directive, \*\*kwargs\}\s*\n\s*\)', r'payload={"directive": directive, **kwargs},\n        )'),
        
        # Fix init_context dictionary
        (r'"namespace": namespace\s*\n\s*"orchestrator": self', r'"namespace": namespace,\n            "orchestrator": self'),
        (r'"orchestrator": self\s*\n\s*"agents": list', r'"orchestrator": self,\n            "agents": list'),
        (r'"agents": list\(self\.agents\.keys\(\)\)\s*\n\s*"timestamp"', r'"agents": list(self.agents.keys()),\n            "timestamp"'),
        
        # Fix logger.info calls
        (r'"agent registration handshake"\s*\n\s*extra=', r'"agent registration handshake",\n            extra='),
        (r'"task assigned"\s*\n\s*extra=', r'"task assigned",\n                extra='),
        
        # Fix return dictionaries with error patterns
        (r'"status": "error"\s*\n\s*"message": f"Error loading agent', r'"status": "error",\n                "message": f"Error loading agent'),
        (r'"status": "error"\s*\n\s*"detail": "Missing agent_name', r'"status": "error",\n                        "detail": "Missing agent_name'),
        (r'"status": "error"\s*\n\s*"detail": f"Agent', r'"status": "error",\n                        "detail": f"Agent'),
        (r'"status": "success"\s*\n\s*"detail": "Agent configurations reloaded', r'"status": "success",\n                        "detail": "Agent configurations reloaded'),
        (r'"status": "error"\s*\n\s*"detail": f"Failed to reload', r'"status": "error",\n                        "detail": f"Failed to reload'),
        
        # Fix middleware request dictionary
        (r'"agent": agent_name\s*\n\s*"directive": directive_name', r'"agent": agent_name,\n            "directive": directive_name'),
        (r'"directive": directive_name\s*\n\s*"confidence": confidence_score,', r'"directive": directive_name,\n            "confidence": confidence_score,'),
        
        # Fix event_data dictionaries
        (r'"type": "task_created"\s*\n\s*"task_id": str\(task_id\)', r'"type": "task_created",\n                            "task_id": str(task_id)'),
        (r'"task_id": str\(task_id\)\s*\n\s*"payload": payload', r'"task_id": str(task_id),\n                            "payload": payload'),
        
        # Fix config update dictionary
        (r'"type": "config_update"\s*\n\s*"agent": agent_name', r'"type": "config_update",\n                "agent": agent_name'),
        (r'"agent": agent_name\s*\n\s*"model": model', r'"agent": agent_name,\n                "model": model'),
        (r'"model": model\s*\n\s*"temperature": temperature', r'"model": model,\n                "temperature": temperature'),
        (r'"temperature": temperature\s*\n\s*"max_tokens": max_tokens', r'"temperature": temperature,\n                "max_tokens": max_tokens'),
        
        # Fix log entries
        (r'"timestamp": datetime\.datetime\.now\(datetime\.timezone\.utc\)\.isoformat\(\)\s*\n\s*"level": "INFO"', r'"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),\n                "level": "INFO"'),
        (r'"level": "INFO"\s*\n\s*"message": "Log fetching', r'"level": "INFO",\n                "message": "Log fetching'),
        (r'"message": "Log fetching via ZMQ active\."\s*\n\s*"agent": "system"', r'"message": "Log fetching via ZMQ active.",\n                "agent": "system"'),
        
        # Fix agent status dictionary
        (r'"name": agent_name\s*\n\s*"status": "running",', r'"name": agent_name,\n                "status": "running",'),
        (r'"status": "running",\s*\n\s*"tasks": 0,', r'"status": "running",\n                "tasks": 0,'),
        (r'"tasks": 0,\s*\n\s*"config": agent\.config,', r'"tasks": 0,\n                "config": agent.config,'),
        
        # Fix search result dictionaries
        (r'"status": "success"\s*\n\s*"results": results', r'"status": "success",\n                    "results": results'),
        (r'"results": results\s*\n\s*"query": query', r'"results": results,\n                    "query": query'),
        (r'"query": query\s*\n\s*"agent_name": agent_name', r'"query": query,\n                    "agent_name": agent_name'),
    ]

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    with open('legion/orchestrator/__init__.py', 'w') as f:
        f.write(content)

    print('Applied comprehensive syntax fixes to orchestrator')

if __name__ == '__main__':
    fix_orchestrator_syntax() 