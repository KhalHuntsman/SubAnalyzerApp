import React, { useEffect, useState } from 'react'
import { useAuth } from '../state/AuthContext.jsx'
import { apiFetch } from '../lib/api.js'

export default function Dashboard() {
  const { token } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Guard against setting state if the component unmounts before the request completes.
    // (Avoids React warnings and racey UI state.)
    let cancelled = false

    async function load() {
      try {
        const d = await apiFetch('/api/dashboard', { token })
        if (!cancelled) setData(d)
      } catch (e) {
        if (!cancelled) setError(e.message)
      }
    }

    load()
    return () => { cancelled = true }
  }, [token]) // Reload if auth token changes (login/logout/refresh)

  return (
    <div className="container">
      <h1>Dashboard</h1>
      {error && <p style={{color:'#ff8899'}}>{error}</p>}
      {!data ? (
        <p><small className="muted">Loading...</small></p>
      ) : (
        <>
          <div className="row">
            <div className="card">
              <h3>Monthly Total</h3>
              <div style={{fontSize: 28}}>${data.monthly_total}</div>
              <small className="muted">Monthly-equivalent cost of active subscriptions.</small>
            </div>
            <div className="card">
              <h3>Annual Total</h3>
              <div style={{fontSize: 28}}>${data.annual_total}</div>
              <small className="muted">Projection based on cadence normalization.</small>
            </div>
            <div className="card">
              <h3>Active Subscriptions</h3>
              <div style={{fontSize: 28}}>{data.active_count}</div>
              <small className="muted">Currently active subscriptions.</small>
            </div>
          </div>

          <div className="row" style={{marginTop: 16}}>
            <div className="card">
              <h3>Upcoming (Next 30 Days)</h3>
              {data.upcoming_30_days.length === 0 ? (
                <p><small className="muted">No upcoming charges in the next 30 days.</small></p>
              ) : (
                <table className="table">
                  <thead>
                    <tr><th>Name</th><th>Due</th><th>Amount</th><th>Cadence</th></tr>
                  </thead>
                  <tbody>
                    {data.upcoming_30_days.map(u => (
                      <tr key={u.subscription_id}>
                        <td>{u.name}</td>
                        <td>{u.due_date}</td>
                        <td>${u.amount}</td>
                        <td><span className="badge">{u.cadence}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="card">
              <h3>Top Subscriptions</h3>
              {data.top_subscriptions.length === 0 ? (
                <p><small className="muted">Add subscriptions to see this list.</small></p>
              ) : (
                <table className="table">
                  <thead>
                    <tr><th>Name</th><th>Amount</th><th>Cadence</th></tr>
                  </thead>
                  <tbody>
                    {data.top_subscriptions.map(s => (
                      <tr key={s.id}>
                        <td>{s.name}</td>
                        <td>${s.amount}</td>
                        <td><span className="badge">{s.cadence}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Full-width separator */}
          <hr style={{ margin: '26px 0' }} />

          {/* Full-width Future Improvements card */}
          <div className="row">
            <div className="card" style={{ flexBasis: '100%' }}>
              <h3>Future Improvements</h3>
              <ul style={{ margin: '10px 0 0 18px' }}>
                <li>Subscription analytics graph</li>
                <li>Improved recurring payment detection</li>
                <li>User edits to subscriptions</li>
                <li>Category insights (spend by category)</li>
                <li>Export subscriptions to CSV</li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
