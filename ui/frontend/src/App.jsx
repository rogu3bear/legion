import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState("")

  useEffect(() => {
    fetch("http://localhost:5001/")
      .then(res => res.json())
      .then(data => setStatus(data.status))
  }, [])

  return (
    <div>
      <h1>Legion UI</h1>
      <p>Server Status: {status}</p>
    </div>
  )
}

export default App
