import React from 'react'

export default function AgentCard({ agent, onSelect }) {
  return (
    <div className="border p-2 m-1 rounded">
      <h3 className="font-bold">{agent}</h3>
      <button onClick={() => onSelect(agent)} className="text-blue-600 underline">
        View
      </button>
    </div>
  )
}
