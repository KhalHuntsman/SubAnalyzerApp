import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from 'react'

const AuthContext = createContext(null)

function parseJwt(token) {
  // Decode JWT payload (no signature validation; used only for exp countdown on the client).
  try {
    const base64 = token.split(".")[1]
    const json = atob(base64.replace(/-/g, "+").replace(/_/g, "/"))
    return JSON.parse(json)
  } catch {
    return null
  }
}

function formatCountdown(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function getSecondsUntilExpiry(accessToken) {
  const payload = parseJwt(accessToken)
  if (!payload?.exp) return 0
  const now = Math.floor(Date.now() / 1000)
  return payload.exp - now
}

export function AuthProvider({ children }) {
  // Access token is used for API calls; refresh token is stored separately for silent refresh.
  const [token, setToken] = useState(() => (
    localStorage.getItem('access_token') || localStorage.getItem('token') || null
  ))

  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })

  const [showExpiryModal, setShowExpiryModal] = useState(false)
  const [countdown, setCountdown] = useState(0)

  // Used to throttle refresh calls so rapid clicks/keypresses don't spam /refresh.
  const lastRefreshRef = useRef(0)

  function logout() {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    localStorage.removeItem("token") // legacy
    setToken(null)
    setUser(null)
    setShowExpiryModal(false)
    setCountdown(0)
  }

  async function refreshAccessToken() {
    const refresh = localStorage.getItem("refresh_token")
    if (!refresh) throw new Error("Missing refresh token")

    // Refresh endpoint uses the refresh token as a Bearer token.
    const res = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { Authorization: `Bearer ${refresh}` },
    })

    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data?.error || data?.msg || "Refresh failed")

    localStorage.setItem("access_token", data.access_token)
    setToken(data.access_token)
    return data.access_token
  }

  async function noteActivity() {
    const now = Date.now()

    // Throttle refresh attempts (max once per 30s).
    if (now - lastRefreshRef.current < 30000) return

    const access = localStorage.getItem("access_token")
    if (!access) return

    const secondsLeft = getSecondsUntilExpiry(access)

    // Only refresh when within 3 minutes of expiry to reduce unnecessary calls.
    if (secondsLeft <= 180) {
      try {
        lastRefreshRef.current = now
        await refreshAccessToken()
        setShowExpiryModal(false)
      } catch {
        // If refresh fails, treat as expired session.
        logout()
      }
    }
  }

  async function continueSession() {
    try {
      await refreshAccessToken()
      setShowExpiryModal(false)
    } catch {
      logout()
    }
  }

  // Keep legacy key in sync so old code paths won't break.
  useEffect(() => {
    if (token) {
      localStorage.setItem("access_token", token)
      localStorage.setItem("token", token)
    } else {
      localStorage.removeItem("access_token")
      localStorage.removeItem("token")
    }
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  // Countdown + auto logout + listen for activity.
  useEffect(() => {
    function onAnyActivity() {
      noteActivity()
    }

    // Capture phase helps catch events even if inner components stop propagation.
    window.addEventListener("click", onAnyActivity, true)
    window.addEventListener("keydown", onAnyActivity, true)

    const interval = setInterval(() => {
      const access = localStorage.getItem("access_token")
      if (!access) return

      const secondsLeft = getSecondsUntilExpiry(access)

      if (secondsLeft <= 0) {
        logout()
        return
      }

      // Show warning modal during the final 3 minutes before expiry.
      if (secondsLeft <= 180) {
        setShowExpiryModal(true)
        setCountdown(secondsLeft)
      } else {
        setShowExpiryModal(false)
        setCountdown(0)
      }
    }, 1000)

    return () => {
      window.removeEventListener("click", onAnyActivity, true)
      window.removeEventListener("keydown", onAnyActivity, true)
      clearInterval(interval)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const value = useMemo(() => ({
    token,
    user,
    isAuthed: Boolean(token),
    login: ({ access_token, refresh_token, user }) => {
      // Persist tokens so apiFetch can work across refreshes/reloads.
      if (access_token) {
        localStorage.setItem("access_token", access_token)
        localStorage.setItem("token", access_token) // legacy
        setToken(access_token)
      }

      if (refresh_token) {
        localStorage.setItem("refresh_token", refresh_token)
      }

      if (user) setUser(user)
    },
    logout,
    refreshAccessToken,
  }), [token, user])

  return (
    <AuthContext.Provider value={value}>
      {showExpiryModal && (
        <div className="modalOverlay">
          <div className="modal">
            <h3>Session Expiring</h3>
            <p>
              You&apos;ve been inactive for a while. You will be automatically logged out in{" "}
              <strong>{formatCountdown(countdown)}</strong>. Hit Continue to extend your session.
            </p>

            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <button className="danger" onClick={logout}>Logout</button>
              <button className="primary" onClick={continueSession}>Continue</button>
            </div>
          </div>
        </div>
      )}

      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
