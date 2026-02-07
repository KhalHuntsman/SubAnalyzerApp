import React from "react"
import { Link, NavLink } from "react-router-dom"
import { useAuth } from "../state/AuthContext.jsx"

export default function Header() {
  const { user, logout, isAuthed } = useAuth()

  const navClass = ({ isActive }) =>
    "navBtn" + (isActive ? " navBtnActive" : "")

  return (
    <header className="headerBar">
      <div className="headerInner">
        <div className="brand">
          <Link to={isAuthed ? "/" : "/login"} className="brandLink">Sub Finder</Link>
        </div>

        {isAuthed ? (
          <>
            <nav className="navButtons">
              <NavLink to="/" end className={navClass}>Dashboard</NavLink>
              <NavLink to="/subscriptions" className={navClass}>Subscriptions</NavLink>
              <NavLink to="/import" className={navClass}>Import CSV</NavLink>
              <NavLink to="/candidates" className={navClass}>Candidates</NavLink>
            </nav>

            <div className="headerRight">
              <span className="headerEmail">{user?.email || ""}</span>
              <button className="navBtn" onClick={logout}>Logout</button>
            </div>
          </>
        ) : (
          <div className="headerRight">
            <NavLink to="/login" className={navClass}>Login</NavLink>
            <NavLink to="/register" className={navClass}>Register</NavLink>
          </div>
        )}
      </div>
    </header>
  )
}
