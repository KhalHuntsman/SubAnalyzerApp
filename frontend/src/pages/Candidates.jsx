import React, { useEffect, useState } from 'react'
import { useAuth } from '../state/AuthContext.jsx'
import { apiFetch } from '../lib/api.js'
import ConfirmModal from "../components/ConfirmModal.jsx"

export default function Candidates() {
  const { token } = useAuth()

  const [cands, setCands] = useState([])
  const [error, setError] = useState(null)
  const [status, setStatus] = useState('pending')

  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pendingDelete, setPendingDelete] = useState(null)

  async function load(s = status) {
    setError(null)
    try {
      const data = await apiFetch(`/api/candidates?status=${encodeURIComponent(s)}`, { token })
      setCands(data)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => { load() }, [status])

  async function confirmCand(c) {
    try {
      await apiFetch(`/api/candidates/${c.id}/confirm`, { token, method: 'POST' })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  async function ignoreCand(c) {
    try {
      await apiFetch(`/api/candidates/${c.id}`, { token, method: 'PATCH', body: { status: 'ignored' } })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  function requestDelete(c) {
    setPendingDelete(c)
    setConfirmOpen(true)
  }

  async function confirmDelete() {
    if (!pendingDelete) return
    try {
      await apiFetch(`/api/candidates/${pendingDelete.id}`, { token, method: 'DELETE' })
      setConfirmOpen(false)
      setPendingDelete(null)
      await load()
    } catch (e) {
      setError(e.message)
      setConfirmOpen(false)
      setPendingDelete(null)
    }
  }

  function cancelDelete() {
    setConfirmOpen(false)
    setPendingDelete(null)
  }

  return (
    <div className="container">
      <h1>Recurring Candidates</h1>
      {error && <p style={{ color: '#ff8899' }}>{error}</p>}

      <div className="card">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <label><small className="muted">View:</small></label>
          <select value={status} onChange={(e) => setStatus(e.target.value)} style={{ maxWidth: 220 }}>
            <option value="pending">pending</option>
            <option value="confirmed">confirmed</option>
            <option value="ignored">ignored</option>
          </select>
          <small className="muted">
            Confirm saves the charge as a subscription, Ignore saves the charge and ignores it in calculations,
            and Delete removes the charge permanently.
          </small>
        </div>

        <hr />

        {cands.length === 0 ? (
          <p><small className="muted">No candidates in this status.</small></p>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Merchant</th><th>Avg</th><th>Cadence</th><th>Confidence</th><th>Next</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {cands.map(c => (
                <tr key={c.id}>
                  <td>{c.display_name}</td>
                  <td>${c.avg_amount}</td>
                  <td><span className="badge">{c.cadence_guess}</span></td>
                  <td>{Math.round(c.confidence * 100)}%</td>
                  <td>{c.next_predicted}</td>
                  <td style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {status === 'pending' && (
                      <>
                        <button className="primary" onClick={() => confirmCand(c)}>Confirm</button>
                        <button onClick={() => ignoreCand(c)}>Ignore</button>
                      </>
                    )}
                    <button className="danger" onClick={() => requestDelete(c)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <ConfirmModal
        open={confirmOpen}
        title="Delete Candidate"
        message={`Are you sure you want to delete the candidate "${pendingDelete?.display_name || ''}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  )
}
