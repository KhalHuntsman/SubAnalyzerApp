import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext.jsx'

export default function NavBar() {
  const { isAuthed, user, logout } = useAuth()
  const nav = useNavigate()

  function handleLogout() {
    logout()
    nav('/login')
  }

  return (
    <nav className="container">
      <div><strong>Subscription Analyzer</strong></div>
      <div className="links">
        {isAuthed && (
          <>
            <Link to="/">Dashboard</Link>
            <Link to="/subscriptions">Subscriptions</Link>
            <Link to="/import">Import CSV</Link>
            <Link to="/candidates">Candidates</Link>
          </>
        )}
      </div>
      <div>
        {isAuthed ? (
          <>
            <small className="muted" style={{marginRight: 10}}>{user?.email}</small>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  )
}
