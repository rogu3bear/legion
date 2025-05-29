import { useEffect, useState } from 'react'
import './App.css'
import AgentCard from './components/AgentCard.jsx'
import DirectiveEditor from './components/DirectiveEditor.jsx'
import PortMapDisplay from './components/PortMapDisplay.jsx'
import EchoLogIndex from './components/EchoLogIndex.tsx'

function App() {
  // ${PORT_ALLOCATOR_PORTMAP_API:-5001}
  const apiPort = import.meta.env.VITE_PORTMAP_API || '5001'
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [config, setConfig] = useState({})
  const [directive, setDirective] = useState('')

  useEffect(() => {
    fetch(`http://localhost:${apiPort}/agents`)
      .then(res => res.json())
      .then(data => setAgents(data.agents))
  }, [apiPort])

  const loadAgent = (agent) => {
    fetch(`http://localhost:${apiPort}/agents/${agent}`)
      .then(res => res.json())
      .then(data => {
        setSelectedAgent(agent)
        setConfig(data)
      })
  }

  const sendDirective = () => {
    fetch(`http://localhost:${apiPort}/echo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: directive })
    })
      .then(res => res.json())
      .then(() => setDirective(''))
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Legion Agent Management</h1>
      <PortMapDisplay />
      <EchoLogIndex />
      <div className="flex flex-wrap">
        {agents.map(agent => (
          <AgentCard key={agent} agent={agent} onSelect={loadAgent} />
        ))}
      </div>

      {selectedAgent && (
        <div>
          <h2>{selectedAgent} Configuration:</h2>
          <pre>{JSON.stringify(config, null, 2)}</pre>
          <DirectiveEditor value={directive} onChange={setDirective} />
          <button onClick={sendDirective} className="mt-2 px-2 py-1 bg-blue-500 text-white rounded">Send</button>
        </div>
      )}

      <section className="cua-placeholder">
        Coming Soon – Custom User Actions
      </section>
    </div>
  )
}

export default App
