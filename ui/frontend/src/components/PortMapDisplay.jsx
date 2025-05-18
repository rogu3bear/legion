import React, { useEffect, useState } from 'react'

export default function PortMapDisplay() {
  const [ports, setPorts] = useState({})

  useEffect(() => {
    fetch('http://localhost:5001/ports')
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
