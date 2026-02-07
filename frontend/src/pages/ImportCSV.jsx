import React, { useState } from 'react'
import { useAuth } from '../state/AuthContext.jsx'
import { apiFetch } from '../lib/api.js'

export default function ImportCSV() {
  const { token } = useAuth()
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!file) return setError('Please choose a CSV file.')

    const form = new FormData()
    form.append('file', file)

    try {
      const data = await apiFetch('/api/imports', { token, method: 'POST', body: form, isForm: true })
      setResult(data)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="container">
      <h1>Import Transactions CSV</h1>
      <div className="card">
        <p>
          Upload a CSV export from your bank/card. The importer tries common column names such as
          <em> date/transaction_date, merchant/description, amount</em>.
        </p>
        <div className="tip">
          <small className="muted">
          For best results, import at least <strong>3-6 months</strong> of transaction history. Recurring subscriptions are detected by finding repeating charges over time, so short date ranges may not generate candidates as expected.
        </small>
        </div>
        {error && <p style={{color:'#ff8899'}}>{error}</p>}
        <form onSubmit={onSubmit}>
          <input type="file" accept=".csv,text/csv" onChange={(e)=>setFile(e.target.files?.[0] || null)} />
          <div style={{height:12}} />
          <button className="primary" type="submit">Upload & Detect</button>
        </form>

        {result && (
          <>
            <hr />
            <h3>Import Result</h3>
            <ul>
              <li>Rows added: <strong>{result.rows_added}</strong></li>
              <li>Rows skipped: <strong>{result.rows_skipped}</strong></li>
              <li>Candidates created: <strong>{result.candidates_created}</strong></li>
              <li>Candidates updated: <strong>{result.candidates_updated}</strong></li>
            </ul>
            <p><small className="muted">Go to Candidates to confirm detected subscriptions.</small></p>
          </>
        )}
      </div>
    </div>
  )
}
