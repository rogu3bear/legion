import React, { useState, useRef, useEffect, useCallback } from 'react'
import { FixedSizeList as List } from 'react-window'

interface EchoEvent {
  timestamp: number
  level: string
  agent_id: string
  message: string
  payload?: any
}

interface EchoStats {
  total_events: number
  events_by_level: Record<string, number>
  recent_activity: {
    last_hour: number
    timestamp: string
  }
  active_agents: string[]
  agent_count: number
}

export default function EchoLogIndex() {
  // Search and filter state
  const [query, setQuery] = useState('')
  const [level, setLevel] = useState('')
  const [agentId, setAgentId] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [sortOrder, setSortOrder] = useState('desc')
  const [includePayload, setIncludePayload] = useState(true)
  
  // Results and pagination
  const [results, setResults] = useState<EchoEvent[]>([])
  const [totalResults, setTotalResults] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(false)
  
  // Real-time streaming
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingEvents, setStreamingEvents] = useState<EchoEvent[]>([])
  const eventSourceRef = useRef<EventSource | null>(null)
  
  // Statistics
  const [stats, setStats] = useState<EchoStats | null>(null)
  const [showStats, setShowStats] = useState(false)
  
  // UI state
  const [activeTab, setActiveTab] = useState<'search' | 'stream' | 'stats'>('search')
  const [expandedEvent, setExpandedEvent] = useState<number | null>(null)
  
  const controllerRef = useRef<AbortController | null>(null)

  // Load statistics
  const loadStats = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/echo/stats')
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }, [])

  // Search function with advanced filtering
  const handleSearch = async (resetOffset = true) => {
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    
    const ctrl = new AbortController()
    controllerRef.current = ctrl
    setLoading(true)
    
    if (resetOffset) {
      setOffset(0)
      setResults([])
    }
    
    const params = new URLSearchParams({
      limit: '50',
      offset: resetOffset ? '0' : offset.toString(),
      sort_order: sortOrder,
      include_payload: includePayload.toString(),
    })
    
    if (query) params.set('query', query)
    if (level) params.set('level', level)
    if (agentId) params.set('agent_id', agentId)
    if (startDate) params.set('start_time', new Date(startDate).toISOString())
    if (endDate) params.set('end_time', new Date(endDate).toISOString())
    
    try {
      const res = await fetch(`/api/v1/echo/search?${params.toString()}`, {
        signal: ctrl.signal,
      })
      
      if (!res.ok) {
        throw new Error(`Search failed: ${res.status}`)
      }
      
      const data = await res.json()
      
      if (resetOffset) {
        setResults(data.events || [])
      } else {
        setResults(prev => [...prev, ...(data.events || [])])
      }
      
      setTotalResults(data.total || 0)
      setOffset(data.next_offset || 0)
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Search error:', err)
      }
    } finally {
      setLoading(false)
    }
  }

  // Export to CSV
  const handleExport = async () => {
    const params = new URLSearchParams({
      format: 'csv',
      limit: '1000',
      sort_order: sortOrder,
      include_payload: includePayload.toString(),
    })
    
    if (query) params.set('query', query)
    if (level) params.set('level', level)
    if (agentId) params.set('agent_id', agentId)
    if (startDate) params.set('start_time', new Date(startDate).toISOString())
    if (endDate) params.set('end_time', new Date(endDate).toISOString())
    
    try {
      const res = await fetch(`/api/v1/echo/search?${params.toString()}`)
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `echo_logs_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Export error:', err)
    }
  }

  // Real-time streaming
  const toggleStreaming = () => {
    if (isStreaming) {
      // Stop streaming
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      setIsStreaming(false)
    } else {
      // Start streaming
      const params = new URLSearchParams()
      if (level) params.set('level', level)
      if (agentId) params.set('agent_id', agentId)
      
      const eventSource = new EventSource(`/api/v1/echo/stream?${params.toString()}`)
      
      eventSource.onmessage = (event) => {
        try {
          const eventData = JSON.parse(event.data)
          setStreamingEvents(prev => [eventData, ...prev.slice(0, 99)]) // Keep last 100 events
        } catch (err) {
          console.error('Error parsing stream event:', err)
        }
      }
      
      eventSource.onerror = (err) => {
        console.error('Stream error:', err)
        setIsStreaming(false)
      }
      
      eventSourceRef.current = eventSource
      setIsStreaming(true)
      setStreamingEvents([])
    }
  }

  // Clear logs
  const handleClearLogs = async () => {
    if (!confirm('Are you sure you want to clear logs? This action cannot be undone.')) {
      return
    }
    
    const params = new URLSearchParams()
    if (level) params.set('level', level)
    if (agentId) params.set('agent_id', agentId)
    
    try {
      const res = await fetch(`/api/v1/echo/clear?${params.toString()}`, {
        method: 'DELETE'
      })
      
      if (res.ok) {
        const data = await res.json()
        alert(`Cleared ${data.cleared_count} log entries`)
        handleSearch() // Refresh results
        loadStats() // Refresh stats
      }
    } catch (err) {
      console.error('Clear logs error:', err)
    }
  }

  // Load more results
  const loadMore = () => {
    if (offset && !loading) {
      handleSearch(false)
    }
  }

  // Format timestamp
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString()
  }

  // Get level color
  const getLevelColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'ERROR': return 'text-red-600 bg-red-50'
      case 'WARN': return 'text-yellow-600 bg-yellow-50'
      case 'INFO': return 'text-blue-600 bg-blue-50'
      case 'DEBUG': return 'text-gray-600 bg-gray-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  // Event row component
  const EventRow = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const events = activeTab === 'stream' ? streamingEvents : results
    const event = events[index]
    if (!event) return null

    const isExpanded = expandedEvent === index
    
    return (
      <div style={style} className="border-b border-gray-200 hover:bg-gray-50">
        <div 
          className="px-3 py-2 cursor-pointer"
          onClick={() => setExpandedEvent(isExpanded ? null : index)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelColor(event.level)}`}>
                {event.level}
              </span>
              <span className="text-xs text-gray-500 font-mono">
                {formatTimestamp(event.timestamp)}
              </span>
              <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                {event.agent_id}
              </span>
              <span className="text-sm text-gray-900 truncate flex-1">
                {event.message}
              </span>
            </div>
            <button className="text-gray-400 hover:text-gray-600">
              {isExpanded ? '−' : '+'}
            </button>
          </div>
          
          {isExpanded && event.payload && (
            <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono">
              <pre className="whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Load stats on mount
  useEffect(() => {
    loadStats()
  }, [loadStats])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  return (
    <div className="my-4 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Echo Log Index</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-3 py-1 text-sm rounded ${
                activeTab === 'search' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Search
            </button>
            <button
              onClick={() => setActiveTab('stream')}
              className={`px-3 py-1 text-sm rounded ${
                activeTab === 'stream' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Live Stream
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`px-3 py-1 text-sm rounded ${
                activeTab === 'stats' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Statistics
            </button>
          </div>
        </div>
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <>
          {/* Search Controls */}
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search logs..."
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
              <select 
                value={level} 
                onChange={e => setLevel(e.target.value)} 
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="">All Levels</option>
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARN">Warning</option>
                <option value="ERROR">Error</option>
                <option value="CRITICAL">Critical</option>
              </select>
              <input
                value={agentId}
                onChange={e => setAgentId(e.target.value)}
                placeholder="Agent ID..."
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
              <select 
                value={sortOrder} 
                onChange={e => setSortOrder(e.target.value)} 
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
              <input
                type="datetime-local"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
                placeholder="Start time"
              />
              <input
                type="datetime-local"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
                placeholder="End time"
              />
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={includePayload}
                  onChange={e => setIncludePayload(e.target.checked)}
                  className="rounded"
                />
                <span>Include payload</span>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleSearch()} 
                  disabled={loading}
                  className="bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600 disabled:opacity-50"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
                <button 
                  onClick={handleExport}
                  className="bg-green-500 text-white px-4 py-2 rounded text-sm hover:bg-green-600"
                >
                  Export CSV
                </button>
                <button 
                  onClick={handleClearLogs}
                  className="bg-red-500 text-white px-4 py-2 rounded text-sm hover:bg-red-600"
                >
                  Clear Logs
                </button>
              </div>
              
              {totalResults > 0 && (
                <span className="text-sm text-gray-600">
                  Showing {results.length} of {totalResults} results
                </span>
              )}
            </div>
          </div>

          {/* Search Results */}
          <div style={{ height: '400px' }}>
            {results.length > 0 ? (
              <List 
                height={400} 
                itemCount={results.length} 
                itemSize={expandedEvent !== null ? 120 : 60} 
                width="100%"
              >
                {EventRow}
              </List>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                {loading ? 'Searching...' : 'No results found'}
              </div>
            )}
          </div>
          
          {offset && (
            <div className="p-4 border-t border-gray-200 text-center">
              <button 
                onClick={loadMore}
                disabled={loading}
                className="bg-gray-500 text-white px-4 py-2 rounded text-sm hover:bg-gray-600 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </>
      )}

      {/* Stream Tab */}
      {activeTab === 'stream' && (
        <>
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={toggleStreaming}
                  className={`px-4 py-2 rounded text-sm font-medium ${
                    isStreaming 
                      ? 'bg-red-500 text-white hover:bg-red-600' 
                      : 'bg-green-500 text-white hover:bg-green-600'
                  }`}
                >
                  {isStreaming ? 'Stop Stream' : 'Start Stream'}
                </button>
                
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  <span className="text-sm text-gray-600">
                    {isStreaming ? 'Live' : 'Stopped'}
                  </span>
                </div>
              </div>
              
              <span className="text-sm text-gray-600">
                {streamingEvents.length} events
              </span>
            </div>
          </div>

          <div style={{ height: '400px' }}>
            {streamingEvents.length > 0 ? (
              <List 
                height={400} 
                itemCount={streamingEvents.length} 
                itemSize={60} 
                width="100%"
              >
                {EventRow}
              </List>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                {isStreaming ? 'Waiting for events...' : 'Start streaming to see live events'}
              </div>
            )}
          </div>
        </>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && (
        <div className="p-4">
          {stats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Total Events</h4>
                <p className="text-2xl font-bold text-blue-600">{stats.total_events.toLocaleString()}</p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Active Agents</h4>
                <p className="text-2xl font-bold text-green-600">{stats.agent_count}</p>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-semibold text-yellow-900 mb-2">Recent Activity</h4>
                <p className="text-2xl font-bold text-yellow-600">{stats.recent_activity.last_hour}</p>
                <p className="text-sm text-yellow-700">events in last hour</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg md:col-span-2">
                <h4 className="font-semibold text-gray-900 mb-2">Events by Level</h4>
                <div className="space-y-2">
                  {Object.entries(stats.events_by_level).map(([level, count]) => (
                    <div key={level} className="flex justify-between items-center">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelColor(level)}`}>
                        {level}
                      </span>
                      <span className="font-mono text-sm">{count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-900 mb-2">Active Agents</h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {stats.active_agents.map(agent => (
                    <div key={agent} className="text-sm text-purple-700 bg-purple-100 px-2 py-1 rounded">
                      {agent}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">Loading statistics...</div>
          )}
          
          <div className="mt-4 text-center">
            <button 
              onClick={loadStats}
              className="bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600"
            >
              Refresh Stats
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
