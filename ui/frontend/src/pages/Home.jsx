import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AgentCard from '../components/AgentCard.jsx'
import PortMapDisplay from '../components/PortMapDisplay.jsx'

export default function Home() {
  const apiPort = import.meta.env.VITE_PORTMAP_API || '5001'
  const [agents, setAgents] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`http://localhost:${apiPort}/agents`)
      .then(res => res.json())
      .then(data => setAgents(data.agents || []))
  }, [])

  const loadAgent = (agent) => navigate(`/agents/${agent}`)

  return (
    <div style={{ padding: '20px' }}>
      <h1>Legion Agent Management</h1>
      <PortMapDisplay />
      <div className="flex flex-wrap">
        {agents.map(agent => (
          <AgentCard key={agent} agent={agent} onSelect={loadAgent} />
        ))}
      </div>
    </div>
  )
}
