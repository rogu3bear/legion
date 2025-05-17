import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [config, setConfig] = useState({})

  useEffect(() => {
    fetch("http://localhost:5001/agents")
      .then(res => res.json())
      .then(data => setAgents(data.agents))
  }, [])

  const loadAgent = (agent) => {
    fetch(`http://localhost:5001/agents/${agent}`)
      .then(res => res.json())
      .then(data => {
        setSelectedAgent(agent)
        setConfig(data)
      })
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Legion Agent Management</h1>
      <ul>
        {agents.map(agent => (
          <li key={agent}>
            <button onClick={() => loadAgent(agent)}>
              {agent}
            </button>
          </li>
        ))}
      </ul>

      {selectedAgent && (
        <div>
          <h2>{selectedAgent} Configuration:</h2>
          <pre>{JSON.stringify(config, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default App
