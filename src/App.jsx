import { useEffect, useState } from 'react'

import './App.css'
import WorkoutDashboard from './components/WorkoutDashboard'
import { supabase } from './lib/supabaseClient'

function AuthPanel({ authMode, email, password, onSubmit, onToggleMode, onEmailChange, onPasswordChange, authError, authNotice, loading }) {
  return (
    <section className="auth-shell">
      <div className="auth-card">
        <p className="eyebrow">Supabase Auth</p>
        <h1>Sign in to your workout tracker</h1>
        <p className="auth-copy">
          Log in with your Supabase user so the dashboard can read workouts and save sets through the backend.
        </p>

        <form className="auth-form" onSubmit={onSubmit}>
          <label>
            Email
            <input value={email} onChange={(event) => onEmailChange(event.target.value)} type="email" required />
          </label>
          <label>
            Password
            <input value={password} onChange={(event) => onPasswordChange(event.target.value)} type="password" required />
          </label>

          {authError ? <p className="error-message">{authError}</p> : null}
          {authNotice ? <p className="auth-notice">{authNotice}</p> : null}

          <div className="auth-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Working...' : authMode === 'sign-in' ? 'Sign in' : 'Create account'}
            </button>
            <button type="button" className="ghost-button" onClick={onToggleMode}>
              {authMode === 'sign-in' ? 'Need an account?' : 'I already have an account'}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}

function SessionBar({ session, onSignOut }) {
  return (
    <header className="session-bar">
      <div>
        <span className="section-label">Signed in as</span>
        <strong>{session.user.email ?? session.user.id}</strong>
      </div>
      <button type="button" className="ghost-button" onClick={onSignOut}>
        Sign out
      </button>
    </header>
  )
}

export default function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [authMode, setAuthMode] = useState('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [authNotice, setAuthNotice] = useState('')
  const [authSubmitting, setAuthSubmitting] = useState(false)

  useEffect(() => {
    if (!supabase) {
      setLoading(false)
      setAuthError('Missing Vite Supabase environment variables.')
      return undefined
    }

    let active = true

    supabase.auth.getSession().then(({ data }) => {
      if (!active) {
        return
      }

      setSession(data.session)
      setLoading(false)
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      setLoading(false)
    })

    return () => {
      active = false
      subscription.unsubscribe()
    }
  }, [])

  async function handleAuthSubmit(event) {
    event.preventDefault()
    if (!supabase) {
      return
    }

    setAuthSubmitting(true)
    setAuthError('')
    setAuthNotice('')

    const result =
      authMode === 'sign-in'
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password })

    if (result.error) {
      setAuthError(result.error.message)
    } else if (authMode === 'sign-up' && !result.data.session) {
      setAuthNotice('Account created. Check your email to confirm your sign-up, then log in.')
    }

    setAuthSubmitting(false)
  }

  async function handleSignOut() {
    if (!supabase) {
      return
    }

    await supabase.auth.signOut()
  }

  if (loading) {
    return <main className="app-shell loading-shell">Loading session...</main>
  }

  if (!session) {
    return (
      <AuthPanel
        authMode={authMode}
        email={email}
        password={password}
        onSubmit={handleAuthSubmit}
        onToggleMode={() => setAuthMode((currentMode) => (currentMode === 'sign-in' ? 'sign-up' : 'sign-in'))}
        onEmailChange={setEmail}
        onPasswordChange={setPassword}
        authError={authError}
        authNotice={authNotice}
        loading={authSubmitting}
      />
    )
  }

  return (
    <main className="app-shell">
      <SessionBar session={session} onSignOut={handleSignOut} />
      <WorkoutDashboard session={session} />
    </main>
  )
}
