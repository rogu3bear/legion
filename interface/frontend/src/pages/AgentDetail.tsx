import { useEffect, useState } from "react";
import useSWR from "swr";

interface AgentDetailProps {
  agentId: string;
}

const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) throw res;
    return res.json();
  });

export default function AgentDetail({ agentId }: AgentDetailProps) {
  const [meta, setMeta] = useState<any | null>(null);
  const [input, setInput] = useState("");

  const { data: messages } = useSWR(`/conversations/${agentId}`, fetcher, {
    refreshInterval: 2000,
    fallbackData: [],
  });

  useEffect(() => {
    fetch(`/agents/${agentId}`)
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then(setMeta)
      .catch(() =>
        setMeta({
          name: agentId,
          description: "Placeholder metadata",
        }),
      );
  }, [agentId]);

  const sendMessage = () => {
    if (!input) return;
    // Placeholder send implementation
    setInput("");
  };

  const diagnose = () => {
    fetch(`/therapist/diagnose?agent_id=${agentId}`).catch(() => {});
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center border-b pb-2">
        <h2 className="text-xl font-bold">{meta?.name || agentId}</h2>
        <span className="text-gray-500">⚙️</span>
      </div>

      <button
        onClick={diagnose}
        className="px-3 py-1 bg-purple-600 text-white rounded"
      >
        Therapist ➤ Diagnose Agent
      </button>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="flex flex-col rounded-2xl shadow p-4 space-y-2">
          <h3 className="font-semibold">Calls &amp; Qs</h3>
          <textarea
            className="flex-grow border rounded p-2"
            rows={6}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            onClick={sendMessage}
            className="self-end px-3 py-1 bg-blue-600 text-white rounded"
          >
            Send
          </button>
        </div>
        <div className="flex flex-col rounded-2xl shadow p-4 space-y-2">
          <h3 className="font-semibold">Conversation Panel</h3>
          <div className="flex flex-col space-y-2 overflow-y-auto h-64">
            {messages && messages.length > 0 ? (
              messages.map((m: any, idx: number) => (
                <div key={idx} className="p-2 rounded-2xl bg-gray-100">
                  {m.content}
                </div>
              ))
            ) : (
              <p className="text-gray-500">No messages</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
