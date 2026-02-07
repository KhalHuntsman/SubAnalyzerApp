import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext.jsx'
import { apiFetch } from '../lib/api.js'

export default function Register() {
  const { login } = useAuth()
  const nav = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      const data = await apiFetch('/api/auth/register', { method: 'POST', body: { email, password } })
      login(data)
      nav('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="container">
      <div className="card" style={{maxWidth: 520, margin: '24px auto'}}>
        <h2>Create Account</h2>
        <p><small className="muted">Password must be at least 8 characters.</small></p>
        {error && <p style={{color:'#ff8899'}}>{error}</p>}
        <form onSubmit={onSubmit}>
          <label>Email</label>
          <input value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@example.com" />
          <div style={{height:10}} />
          <label>Password</label>
          <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="••••••••" />
          <div style={{height:16}} />
          <button className="primary" type="submit">Register</button>
        </form>
        <hr />
        <p><small className="muted">Already have an account? <Link to="/login">Log in</Link>.</small></p>
      </div>
    </div>
  )
}
