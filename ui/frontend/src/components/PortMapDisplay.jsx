import React, { useEffect, useState } from 'react'

// Use PORT_ALLOCATOR_PORTMAP_API for port (default 5001)
const PORTMAP_API_PORT = import.meta.env.VITE_PORTMAP_API_PORT || '5001';

export default function PortMapDisplay() {
  const [ports, setPorts] = useState({})

  useEffect(() => {
    fetch(`http://localhost:${PORTMAP_API_PORT}/ports`)
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
