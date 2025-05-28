import React, { useState, useRef } from 'react'
import { FixedSizeList as List } from 'react-window'

export default function EchoNexus() {
  const [query, setQuery] = useState('')
  const [level, setLevel] = useState('INFO')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [results, setResults] = useState<string[]>([])
  const controllerRef = useRef<AbortController | null>(null)

  const handleSearch = async () => {
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    const ctrl = new AbortController()
    controllerRef.current = ctrl
    setResults([])
    const params = new URLSearchParams({
      q: query,
      level,
      start: startDate,
      end: endDate,
    })
    try {
      const res = await fetch(`/echo/search?${params.toString()}`, {
        signal: ctrl.signal,
      })
      if (!res.body) {
        const data = await res.json()
        setResults(data.results || [])
        return
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        let lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.trim()) {
            setResults(prev => [...prev, line.trim()])
          }
        }
      }
      if (buffer.trim()) {
        setResults(prev => [...prev, buffer.trim()])
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('search error', err)
      }
    }
  }

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style} className="px-2 py-1 border-b border-gray-200">
      {results[index]}
    </div>
  )

  return (
    <div className="my-4">
      <h3 className="font-bold">Echo Nexus</h3>
      <div className="flex items-center gap-2 mb-2">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search logs"
          className="border p-1 flex-1"
        />
        <select value={level} onChange={e => setLevel(e.target.value)} className="border p-1">
          <option value="INFO">Info</option>
          <option value="DEBUG">Debug</option>
          <option value="ERROR">Error</option>
        </select>
        <input
          type="date"
          value={startDate}
          onChange={e => setStartDate(e.target.value)}
          className="border p-1"
        />
        <input
          type="date"
          value={endDate}
          onChange={e => setEndDate(e.target.value)}
          className="border p-1"
        />
        <button onClick={handleSearch} className="bg-blue-500 text-white px-2 py-1">
          Search
        </button>
      </div>
      <div style={{ height: '300px' }}>
        <List height={300} itemCount={results.length} itemSize={24} width="100%">
          {Row}
        </List>
      </div>
    </div>
  )
}
