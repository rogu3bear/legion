import { useEffect, useState } from 'react'

interface LogEntry {
  timestamp: string
  level: string
  message: string
}

export default function EchoLogViewer({ agentId }: { agentId: string }) {
  const [logs, setLogs] = useState<LogEntry[]>([])

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/v1/echo/search?agent_id=${agentId}&limit=20`)
        if (res.ok) {
          const data = await res.json()
          setLogs(data.events || [])
        }
      } catch (err) {
        console.error('Failed to load logs', err)
      }
    }
    fetchLogs()
  }, [agentId])

  return (
    <div className="text-sm space-y-1">
      {logs.map((log, idx) => (
        <div key={idx} className="border-b pb-1">
          <span className="text-gray-500 mr-2">{log.timestamp}</span>
          <span className="font-mono">{log.level}</span> {log.message}
        </div>
      ))}
      {logs.length === 0 && <p className="text-gray-500">No recent logs</p>}
    </div>
  )
}
