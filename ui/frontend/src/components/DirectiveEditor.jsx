import React from 'react'

export default function DirectiveEditor({ value, onChange }) {
  return (
    <textarea
      className="w-full border p-2"
      rows="6"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder="Enter directive"
    />
  )
}
