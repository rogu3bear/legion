import { useEffect, useState } from 'react'

export default function EchoLogViewer({ agentId }) {
  const apiPort = import.meta.env.VITE_PORTMAP_API || '5001'
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')
  const [expanded, setExpanded] = useState(null)

  const loadLogs = () => {
    setLoading(true)
    const eventParam = filter !== 'all' ? `&event=${filter}` : ''
    fetch(`http://localhost:${apiPort}/echo/logs?agent=${agentId}${eventParam}`)
      .then(res => res.json())
      .then(data => {
        setLogs(data)
        setLoading(false)
      })
      .catch(() => {
        setError('Failed to load logs')
        setLoading(false)
      })
  }

  useEffect(() => {
    loadLogs()
  }, [agentId, filter])

  if (loading) return <p>Loading...</p>
  if (error) return <p className="text-red-500">{error}</p>
  if (!logs.length) return <p>No logs available.</p>

  return (
    <div>
      <div className="mb-2">
        <select value={filter} onChange={e => setFilter(e.target.value)} className="border p-1 dark:bg-gray-800">
          <option value="all">All</option>
          <option value="Fallback">Fallback</option>
          <option value="Retry">Retry</option>
          <option value="PromptStart">PromptStart</option>
        </select>
      </div>
      <table className="min-w-full text-sm">
        <thead>
          <tr>
            <th className="px-2 py-1 text-left">Event</th>
            <th className="px-2 py-1 text-left">Trace ID</th>
            <th className="px-2 py-1 text-left">Timestamp</th>
            <th className="px-2 py-1 text-left">Tokens</th>
            <th className="px-2 py-1 text-left">Model</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, idx) => (
            <tr key={idx} className="border-t">
              <td className="px-2 py-1">{log.event}</td>
              <td className="px-2 py-1">{log.trace_id}</td>
              <td className="px-2 py-1">{log.timestamp}</td>
              <td className="px-2 py-1">{log.token_count ?? '-'}</td>
              <td className="px-2 py-1">{log.fallback_model ?? '-'}</td>
              <td className="px-2 py-1">
                <button onClick={() => setExpanded(expanded === idx ? null : idx)} className="text-blue-600 underline">
                  {expanded === idx ? 'Hide' : 'View'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {expanded !== null && (
        <pre className="bg-gray-100 dark:bg-gray-800 p-2 mt-2 text-xs overflow-auto">
          {JSON.stringify(logs[expanded], null, 2)}
        </pre>
      )}
    </div>
  )
}
