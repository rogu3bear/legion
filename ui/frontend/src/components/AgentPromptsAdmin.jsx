import React, { useState, useEffect, useMemo } from 'react'

// Simple Searchable MultiSelect Component (can be moved to its own file if reused)
const SearchableMultiSelect = ({ options, selected, onChange, placeholder }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const filteredOptions = useMemo(() =>
    options.filter(opt =>
      opt.toLowerCase().includes(searchTerm.toLowerCase())
    ), [options, searchTerm])

  const toggleOption = (option) => {
    if (selected.includes(option)) {
      onChange(selected.filter(item => item !== option))
    } else {
      onChange([...selected, option])
    }
  }

  return (
    <div className="relative">
      <button
        type="button"
        className="w-full p-2 border rounded-lg text-left bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        onClick={() => setIsOpen(!isOpen)}
      >
        {selected.length > 0
          ? `${selected.length} skill(s) selected`
          : placeholder || 'Select skills...'}
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
        </span>
      </button>
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
          <input
            type="text"
            className="w-full p-2 border-b sticky top-0 bg-white z-10"
            placeholder="Search skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <ul>
            {filteredOptions.length > 0 ? filteredOptions.map(option => (
              <li
                key={option}
                className={`p-2 hover:bg-gray-100 cursor-pointer flex items-center ${
                  selected.includes(option) ? 'bg-blue-50 font-semibold' : ''
                }`}
                onClick={() => toggleOption(option)}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(option)}
                  readOnly
                  className="mr-2 pointer-events-none"
                />
                {option}
              </li>
            )) : (
              <li className="p-2 text-gray-500">No skills found.</li>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function AgentPromptsAdmin() {
  const [agentsData, setAgentsData] = useState({ agents: {}, all_skills: [] })
  const [selectedAgentName, setSelectedAgentName] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [currentSystemPrompt, setCurrentSystemPrompt] = useState('')
  const [currentSelectedSkills, setCurrentSelectedSkills] = useState([])

  const [loadingModal, setLoadingModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [reverting, setReverting] = useState(false)
  const [toast, setToast] = useState(null) // { message: string, type: 'success' | 'error' }

  // API endpoint prefix
  const API_PREFIX = 'http://localhost:7602/api/admin/prompts'

  useEffect(() => {
    loadAgentsAndSkills()
  }, [])

  const showToast = (message, type) => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000) // Auto-hide after 3s
  }

  const loadAgentsAndSkills = async () => {
    try {
      const response = await fetch(API_PREFIX)
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail?.message || `HTTP error ${response.status}`)
      }
      const data = await response.json()
      setAgentsData({
        agents: data.agents || {},
        all_skills: data.all_skills || []
      })
    } catch (error) {
      showToast(`Failed to load agents & skills: ${error.message}`, 'error')
      setAgentsData({ agents: {}, all_skills: [] }) // Reset or keep stale data?
    }
  }

  const openAgentModal = async (agentName) => {
    setLoadingModal(true)
    setSelectedAgentName(agentName)
    setModalOpen(true)

    try {
      const response = await fetch(`${API_PREFIX}/${agentName}`)
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail?.message || `HTTP error ${response.status}`)
      }
      const data = await response.json()
      setCurrentSystemPrompt(data.system || '')
      setCurrentSelectedSkills(data.skills || [])
    } catch (error) {
      showToast(`Failed to load prompt for ${agentName}: ${error.message}`, 'error')
      // Keep modal open with empty/default values or close it?
      setCurrentSystemPrompt('') // Reset on error
      setCurrentSelectedSkills([])
    } finally {
      setLoadingModal(false)
    }
  }

  const handleSavePrompt = async () => {
    if (!selectedAgentName) return
    setSaving(true)

    try {
      const response = await fetch(`${API_PREFIX}/${selectedAgentName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system: currentSystemPrompt,
          skills: currentSelectedSkills
        })
      })

      const responseData = await response.json().catch(() => ({}))

      if (response.ok) {
        showToast('Prompt saved successfully!', 'success')
        setModalOpen(false)
        // Optimistically update local state or re-fetch all agents?
        // For now, just close and let next open reflect changes.
        // Or update the specific agent in agentsData.agents if responseData.updated_prompt is reliable
        if (responseData.updated_prompt) {
            setAgentsData(prev => ({
                ...prev,
                agents: {
                    ...prev.agents,
                    [selectedAgentName]: {
                        ...prev.agents[selectedAgentName],
                        system_prompt: responseData.updated_prompt.system,
                        function_tags: responseData.updated_prompt.skills
                    }
                }
            }))
        } else {
            loadAgentsAndSkills() // Fallback to reload all if specific update data not present
        }

      } else {
        const errorMsg = responseData.detail?.message || responseData.detail || `Failed to save (HTTP ${response.status})`
        showToast(errorMsg, 'error')
      }
    } catch (error) {
      showToast(`Save error: ${error.message}`, 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleRevertPrompt = async () => {
    if (!selectedAgentName) return
    setReverting(true)
    try {
      const response = await fetch(`${API_PREFIX}/${selectedAgentName}/revert`, {
        method: 'POST'
      })
      const responseData = await response.json().catch(() => ({}))

      if (response.ok) {
        showToast('Prompt reverted successfully!', 'success')
        if (responseData.reverted_prompt) {
          setCurrentSystemPrompt(responseData.reverted_prompt.system)
          setCurrentSelectedSkills(responseData.reverted_prompt.skills)
           // Also update the main agent list display
            setAgentsData(prev => ({
                ...prev,
                agents: {
                    ...prev.agents,
                    [selectedAgentName]: {
                        ...prev.agents[selectedAgentName],
                        system_prompt: responseData.reverted_prompt.system,
                        function_tags: responseData.reverted_prompt.skills
                    }
                }
            }))
        } else {
            // If no specific data, re-fetch to update modal
            openAgentModal(selectedAgentName) // Re-fetch for the current agent
        }
      } else {
        const errorMsg = responseData.detail?.message || responseData.detail || `Failed to revert (HTTP ${response.status})`
        showToast(errorMsg, 'error')
      }
    } catch (error) {
      showToast(`Revert error: ${error.message}`, 'error')
    } finally {
      setReverting(false)
    }
  }

  const closeModal = () => {
    setModalOpen(false)
    setSelectedAgentName(null)
    // Resetting fields, though they'd be overwritten on next openAgentModal
    setCurrentSystemPrompt('')
    setCurrentSelectedSkills([])
  }

  // Hide admin page if NEXT_PUBLIC_HIDE_ADMIN is set (example)
  // This is a Vite app, so it would be import.meta.env.VITE_HIDE_ADMIN
  if (import.meta.env.VITE_HIDE_ADMIN === 'true') {
      return <div className="p-4">Admin interface is hidden.</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1 className="text-2xl font-bold mb-6">Agent Prompt Manager</h1>

      {toast && (
        <div className={`fixed top-5 right-5 p-4 rounded-lg shadow-xl z-[100] text-white ${
          toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`}>
          {toast.message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Object.entries(agentsData.agents).map(([agentName, agentInfo]) => (
          <div key={agentName} className="border rounded-lg p-4 shadow hover:shadow-lg transition-shadow flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-lg mb-1">{agentName}</h3>
              <p className="text-xs text-gray-500 mb-2">Priority: {agentInfo.priority}</p>
              <p className="text-xs text-gray-600 mb-1 font-medium">Current Skills:</p>
              <div className="text-xs text-gray-700 mb-3 max-h-20 overflow-y-auto break-all">
                {agentInfo.function_tags && agentInfo.function_tags.length > 0
                  ? agentInfo.function_tags.join(', ')
                  : 'No skills assigned'}
              </div>
            </div>
            <button
              onClick={() => openAgentModal(agentName)}
              className="w-full bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-600 transition-colors text-sm mt-2"
            >
              Edit Prompt
            </button>
          </div>
        ))}
      </div>

      {modalOpen && selectedAgentName && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Edit: {selectedAgentName}</h2>
                <button onClick={closeModal} className="text-gray-500 hover:text-gray-800 text-2xl">&times;</button>
              </div>
            </div>

            {loadingModal ? (
              <div className="p-8 text-center text-lg">Loading prompt data...</div>
            ) : (
              <>
                <div className="p-6 space-y-5 overflow-y-auto flex-grow">
                  <div>
                    <label htmlFor="systemPrompt" className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
                    <textarea
                      id="systemPrompt"
                      value={currentSystemPrompt}
                      onChange={(e) => setCurrentSystemPrompt(e.target.value)}
                      className="w-full h-48 p-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter system prompt (min 5, max 8000 chars)..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Skills ({currentSelectedSkills.length} selected)</label>
                    <SearchableMultiSelect
                      options={agentsData.all_skills}
                      selected={currentSelectedSkills}
                      onChange={setCurrentSelectedSkills}
                      placeholder="Select or search skills..."
                    />
                  </div>
                </div>

                <div className="p-6 border-t flex justify-between items-center bg-gray-50">
                  <button
                    onClick={handleRevertPrompt}
                    disabled={reverting || saving}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {reverting ? 'Reverting...' : 'Revert to Previous'}
                  </button>
                  <div className="space-x-3">
                    <button
                      onClick={closeModal}
                      disabled={saving || reverting}
                      className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-100 disabled:opacity-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSavePrompt}
                      disabled={saving || reverting || currentSystemPrompt.length < 5 || currentSystemPrompt.length > 8000}
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {saving ? 'Saving...' : 'Save Prompt'}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
