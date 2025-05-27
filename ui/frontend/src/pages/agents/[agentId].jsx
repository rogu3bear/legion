import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import EchoLogViewer from '../../components/EchoLogViewer.jsx'

export default function AgentDetailPage() {
  const { agentId } = useParams()
  const apiPort = import.meta.env.VITE_PORTMAP_API || '5001'
  const [config, setConfig] = useState(null)
  const [tab, setTab] = useState('config')

  useEffect(() => {
    fetch(`http://localhost:${apiPort}/agents/${agentId}`)
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(() => setConfig(null))
  }, [agentId])

  return (
    <div className="p-4">
      <Link to="/" className="text-blue-600 underline">Back</Link>
      <h2 className="text-xl font-bold mt-2">Agent {agentId}</h2>
      <div className="mt-4">
        <button onClick={() => setTab('config')} className={`mr-2 ${tab === 'config' ? 'font-bold' : ''}`}>Details</button>
        <button onClick={() => setTab('logs')} className={`mr-2 ${tab === 'logs' ? 'font-bold' : ''}`}>Echo Logs</button>
      </div>
      {tab === 'config' && (
        <pre className="bg-gray-100 dark:bg-gray-800 p-2 mt-2 text-sm overflow-auto">
          {config ? JSON.stringify(config, null, 2) : 'Loading...'}
        </pre>
      )}
      {tab === 'logs' && (
        <div className="mt-2">
          <EchoLogViewer agentId={agentId} />
        </div>
      )}
    </div>
  )
}
