import React, { useEffect, useState } from 'react'
import { useAuth } from '../state/AuthContext.jsx'
import { apiFetch } from '../lib/api.js'
import ConfirmModal from "../components/ConfirmModal.jsx"

const CADENCES = ['weekly','monthly','quarterly','yearly']
const STATUSES = ['active','canceled']

function isoToUs(iso) {
  if (!iso || typeof iso !== "string") return ""
  const parts = iso.split("-")
  if (parts.length !== 3) return iso
  const [y, m, d] = parts
  return `${m}/${d}/${y}`
}

function usToIso(us) {
  if (!us || typeof us !== "string") return ""
  const parts = us.split("/")
  if (parts.length !== 3) return us
  const [m, d, y] = parts.map(p => p.trim())
  if (!m || !d || !y) return us
  return `${y.padStart(4, "0")}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`
}

function isUsDate(us) {
  // Keep UI input strict so the backend can safely parse + store ISO.
  return /^\d{2}\/\d{2}\/\d{4}$/.test(us)
}

function truncateAfter12(text) {
  const t = (text ?? "").toString()
  if (t.length <= 12) return t
  return t.slice(0, 12) + "..."
}

export default function Subscriptions() {
  const { token } = useAuth()
  const [subs, setSubs] = useState([])
  const [error, setError] = useState(null)

  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pendingDelete, setPendingDelete] = useState(null)

  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({
    name: '',
    amount: '',
    cadence: 'monthly',
    next_due_date: '',
    status: 'active',
  })

  const [form, setForm] = useState({
    name: '',
    amount: '',
    cadence: 'monthly',
    next_due_date: '',
    category: '',
    notes: '',
  })

  async function load() {
    setError(null)
    try {
      const data = await apiFetch('/api/subscriptions', { token })
      setSubs(data)
    } catch (e) {
      setError(e.message)
    }
  }

  // Load once on mount (token is stable in this app flow; AuthContext/localStorage handles auth changes).
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function onChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function create(e) {
    e.preventDefault()
    setError(null)

    // Fast client-side validation for immediate feedback (backend still validates).
    if (!form.name.trim()) {
      setError("Name is required.")
      return
    }
    if (!isUsDate(form.next_due_date)) {
      setError("Next Due Date must be in MM/DD/YYYY format.")
      return
    }

    const payload = {
      ...form,
      name: form.name.trim(),
      // UI uses MM/DD/YYYY but API stores ISO.
      next_due_date: usToIso(form.next_due_date),
    }

    try {
      await apiFetch('/api/subscriptions', { token, method: 'POST', body: payload })
      setForm({ name:'', amount:'', cadence:'monthly', next_due_date:'', category:'', notes:'' })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  async function toggleCancel(sub) {
    const nextStatus = sub.status === 'active' ? 'canceled' : 'active'
    await apiFetch(`/api/subscriptions/${sub.id}`, { token, method:'PATCH', body: { status: nextStatus } })
    await load()
  }

  // ---- Delete (modal) ----
  function requestDelete(sub) {
    setPendingDelete(sub)
    setConfirmOpen(true)
  }

  async function confirmDelete() {
    if (!pendingDelete) return
    setError(null)

    try {
      await apiFetch(`/api/subscriptions/${pendingDelete.id}`, { token, method:'DELETE' })
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

  // ---- Edit mode ----
  function startEdit(sub) {
    setError(null)
    setEditingId(sub.id)
    setEditForm({
      name: sub.name ?? '',
      amount: String(sub.amount ?? ''),
      cadence: sub.cadence ?? 'monthly',
      next_due_date: isoToUs(sub.next_due_date),
      status: sub.status ?? 'active',
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setEditForm({ name:'', amount:'', cadence:'monthly', next_due_date:'', status:'active' })
  }

  function onEditChange(e) {
    setEditForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function saveEdit(subId) {
    setError(null)

    if (!editForm.name.trim()) {
      setError("Name is required.")
      return
    }
    if (!isUsDate(editForm.next_due_date)) {
      setError("Next Due Date must be in MM/DD/YYYY format.")
      return
    }
    if (!CADENCES.includes(editForm.cadence)) {
      setError("Cadence is invalid.")
      return
    }
    if (!STATUSES.includes(editForm.status)) {
      setError("Status is invalid.")
      return
    }

    const payload = {
      name: editForm.name.trim(),
      amount: editForm.amount,
      cadence: editForm.cadence,
      next_due_date: usToIso(editForm.next_due_date),
      status: editForm.status,
    }

    try {
      await apiFetch(`/api/subscriptions/${subId}`, { token, method:'PATCH', body: payload })
      cancelEdit()
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="container containerWide">
      <h1>Subscriptions</h1>
      {error && <p style={{color:'#ff8899'}}>{error}</p>}

      <div className="row">
        <div className="card">
          <h3>Add Subscription</h3>
          <form onSubmit={create}>
            <label>Name</label>
            <input name="name" value={form.name} onChange={onChange} placeholder="Netflix" />

            <div style={{height:10}} />
            <label>Amount</label>
            <input name="amount" value={form.amount} onChange={onChange} placeholder="15.99" />

            <div style={{height:10}} />
            <label>Cadence</label>
            <select name="cadence" value={form.cadence} onChange={onChange}>
              {CADENCES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            <div style={{height:10}} />
            <label>Next Due Date</label>
            <input name="next_due_date" value={form.next_due_date} onChange={onChange} placeholder="MM/DD/YYYY" />

            <div style={{height:10}} />
            <label>Category (optional)</label>
            <input name="category" value={form.category} onChange={onChange} placeholder="Streaming" />

            <div style={{height:10}} />
            <label>Notes (optional)</label>
            <textarea name="notes" value={form.notes} onChange={onChange} rows={3} placeholder="Anything useful..." />

            <div style={{height:14}} />
            <button className="primary" type="submit">Save</button>
          </form>
        </div>

        <div className="card">
          <h3>Your Subscriptions</h3>

          {subs.length === 0 ? (
            <p><small className="muted">No subscriptions yet.</small></p>
          ) : (
            // Wrapper enables horizontal scroll on small screens without breaking table-layout: fixed.
            <div className="tableWrap">
              <table className="table">
                {/* Force predictable widths with table-layout: fixed */}
                <colgroup>
                  <col style={{ width: "20%" }} /> {/* Name */}
                  <col style={{ width: "12%" }} /> {/* Amount */}
                  <col style={{ width: "14%" }} /> {/* Cadence */}
                  <col style={{ width: "16%" }} /> {/* Next Due */}
                  <col style={{ width: "12%" }} /> {/* Status */}
                  <col style={{ width: "20%" }} /> {/* Actions */}
                </colgroup>

                <thead>
                  <tr>
                    <th className="col-name">Name</th>
                    <th className="col-amt">Amount</th>
                    <th className="col-cadence">Cadence</th>
                    <th className="col-next">Next Due</th>
                    <th className="col-status">Status</th>
                    <th className="col-actions">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {subs.map(s => {
                    const isEditing = editingId === s.id

                    return (
                      <tr key={s.id}>
                        <td className="col-name" title={s.name}>
                          {isEditing ? (
                            <input
                              className="tableControl"
                              name="name"
                              value={editForm.name}
                              onChange={onEditChange}
                              placeholder="Name"
                            />
                          ) : (
                            <span className="truncate12">{truncateAfter12(s.name)}</span>
                          )}
                        </td>

                        <td className="col-amt">
                          {isEditing ? (
                            <input
                              className="tableControl"
                              name="amount"
                              value={editForm.amount}
                              onChange={onEditChange}
                              placeholder="15.99"
                            />
                          ) : (
                            <>${s.amount}</>
                          )}
                        </td>

                        <td className="col-cadence">
                          {isEditing ? (
                            <select
                              className="tableControl"
                              name="cadence"
                              value={editForm.cadence}
                              onChange={onEditChange}
                            >
                              {CADENCES.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                          ) : (
                            <span className="badge">{s.cadence}</span>
                          )}
                        </td>

                        <td className="col-next">
                          {isEditing ? (
                            <input
                              className="tableControl"
                              name="next_due_date"
                              value={editForm.next_due_date}
                              onChange={onEditChange}
                              placeholder="MM/DD/YYYY"
                            />
                          ) : (
                            isoToUs(s.next_due_date)
                          )}
                        </td>

                        <td className="col-status">
                          {isEditing ? (
                            <select
                              className="tableControl"
                              name="status"
                              value={editForm.status}
                              onChange={onEditChange}
                            >
                              {STATUSES.map(st => <option key={st} value={st}>{st}</option>)}
                            </select>
                          ) : (
                            <span className="badge">{s.status}</span>
                          )}
                        </td>

                        <td className="col-actions">
                          <div className="actionsRow">
                            {isEditing ? (
                              <>
                                <button
                                  type="button"
                                  className="primary"
                                  onClick={() => saveEdit(s.id)}
                                >
                                  Save
                                </button>
                                <button
                                  type="button"
                                  onClick={cancelEdit}
                                >
                                  Cancel
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  type="button"
                                  onClick={() => toggleCancel(s)}
                                >
                                  {s.status === 'active' ? 'Cancel' : 'Re-activate'}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => startEdit(s)}
                                >
                                  Edit
                                </button>
                                <button
                                  type="button"
                                  className="danger"
                                  onClick={() => requestDelete(s)}
                                >
                                  Delete
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          <hr />
        </div>
      </div>

      <ConfirmModal
        open={confirmOpen}
        title="Delete Subscription"
        message={`Are you sure you want to delete the subscription "${pendingDelete?.name || ''}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  )
}
