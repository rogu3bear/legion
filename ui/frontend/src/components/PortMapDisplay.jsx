import React, { useEffect, useState } from 'react'

export default function PortMapDisplay() {
  const [ports, setPorts] = useState({})

  // ${PORT_ALLOCATOR_PORTMAP_API:-5001}
  const apiPort = import.meta.env.VITE_PORTMAP_API || '5001'
  useEffect(() => {
    fetch(`http://localhost:${apiPort}/ports`)
      .then(res => res.json())
      .then(data => setPorts(data))
  }, [])

  return (
    <div className="my-2">
      <h3 className="font-bold">Port Map</h3>
      <ul>
        {Object.entries(ports).map(([k, v]) => (
          <li key={k}>{k}: {v}</li>
        ))}
      </ul>
    </div>
  )
}
