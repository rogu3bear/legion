from typing import Dict, List


class PromptBuilder:
    """
    Utility to build LLM prompt messages from system prompt, memories,
    reflection instruction, thread history, and user query.
    """

    @staticmethod
    def build(
        system_prompt: str,
        memories: List[str],
        thread_history: List[Dict[str, str]],
        user_query: str,
        memory_prefix: str = "Previously on our project:",
        reflection_prompt: str = "Reflection: think step-by-step before answering.",
    ) -> List[Dict[str, str]]:
        """Constructs a list of message dicts for LLM consumption."""
        # Clean and assemble memory summary
        if memories:
            mem_content = f"{memory_prefix} " + "\n".join(memories)
        else:
            mem_content = f"{memory_prefix} (no relevant memories found)"
        # Build base messages
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "system", "content": mem_content},
            {"role": "system", "content": reflection_prompt},
        ]
        # Insert prior conversation
        messages.extend(thread_history)
        # Append user query
        messages.append({"role": "user", "content": user_query})
        return messages
