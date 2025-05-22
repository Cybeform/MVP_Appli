// src/pages/Login.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [code, setCode] = useState('')
  const navigate = useNavigate()

  const submit = async e => {
    e.preventDefault()
    const res = await fetch('http://localhost:8000/validate-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    })
    if (!res.ok) {
      alert('Code invalide ou expiré')
      return
    }
    const { token } = await res.json()
    localStorage.setItem('accessToken', token)
    navigate('/app')
  }

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-8">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-4">
          Accès Démo BTP Meetings
        </h1>

        <form onSubmit={submit} className="space-y-4">
          <input
            type="password"                     // ← ici !
            value={code}
            onChange={e => setCode(e.target.value.toUpperCase())}
            placeholder="Entrez votre code d’accès"
            required
            className="
              w-full border border-gray-300 rounded-md
              px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500
            "
          />

          <button
            type="submit"
            className="
              w-full bg-blue-600 hover:bg-blue-700
              text-white font-semibold rounded-md
              px-4 py-2 transition
            "
          >
            Valider
          </button>
        </form>
      </div>
    </div>
  )
}
