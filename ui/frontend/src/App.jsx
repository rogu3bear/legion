import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import AgentDetailPage from './pages/agents/[agentId].jsx'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/agents/:agentId" element={<AgentDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}
