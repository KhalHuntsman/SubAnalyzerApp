export async function apiFetch(path, { token, method='GET', body, isForm=false } = {}) {
  const headers = {}

  // Default to JSON unless sending FormData (browser sets multipart headers automatically).
  if (!isForm) headers['Content-Type'] = 'application/json'

  // Prefer explicit token, fall back to localStorage for convenience.
  const access = token || localStorage.getItem("access_token") || localStorage.getItem("token")
  if (access) headers['Authorization'] = `Bearer ${access}`

  const res = await fetch(path, {
    method,
    headers,
    body: isForm ? body : (body ? JSON.stringify(body) : undefined),
  })

  // Read as text first so we can safely handle empty or non-JSON responses.
  const text = await res.text()
  let data
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = { raw: text }
  }

  // Normalize backend errors into a consistent thrown message.
  if (!res.ok) {
    const msg = data?.error || data?.msg || `Request failed (${res.status})`
    throw new Error(msg)
  }

  return data
}
