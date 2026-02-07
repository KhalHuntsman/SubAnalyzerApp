export async function apiFetch(path, { token, method='GET', body, isForm=false } = {}) {
  const headers = {}
  if (!isForm) headers['Content-Type'] = 'application/json'

  const access = token || localStorage.getItem("access_token") || localStorage.getItem("token")
  if (access) headers['Authorization'] = `Bearer ${access}`

  const res = await fetch(path, {
    method,
    headers,
    body: isForm ? body : (body ? JSON.stringify(body) : undefined),
  })

  const text = await res.text()
  let data
  try { data = text ? JSON.parse(text) : null } catch { data = { raw: text } }

  if (!res.ok) {
    const msg = data?.error || data?.msg || `Request failed (${res.status})`
    throw new Error(msg)
  }
  return data
}
