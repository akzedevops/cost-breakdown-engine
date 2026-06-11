import { useEffect, useState } from 'react'
import SummaryCards from './components/SummaryCards'
import CategoryChart from './components/CategoryChart'
import EnvironmentChart from './components/EnvironmentChart'
import ServiceTable from './components/ServiceTable'
import InsightsPanel from './components/InsightsPanel'

const API = ''  // empty = same origin via Vite proxy

async function fetchAll() {
  const [summary, categories, services, environments, insights] = await Promise.all([
    fetch(`${API}/api/summary`).then(r => r.json()),
    fetch(`${API}/api/costs/by-category`).then(r => r.json()),
    fetch(`${API}/api/costs/by-service`).then(r => r.json()),
    fetch(`${API}/api/costs/by-environment`).then(r => r.json()),
    fetch(`${API}/api/insights`).then(r => r.json()),
  ])
  return { summary, categories, services, environments, insights }
}

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAll()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={styles.center}>
      <div style={styles.spinner} />
      <p style={{ marginTop: 16, color: '#666' }}>Loading cost data…</p>
    </div>
  )

  if (error) return (
    <div style={styles.center}>
      <p style={{ color: '#e53e3e', fontWeight: 600 }}>⚠ Could not reach the backend</p>
      <p style={{ color: '#666', marginTop: 8, fontSize: 14 }}>{error}</p>
      <p style={{ color: '#666', marginTop: 4, fontSize: 13 }}>Make sure the FastAPI server is running on port 8000.</p>
    </div>
  )

  return (
    <div style={styles.page}>
      {/* ── Header ── */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div>
            <h1 style={styles.title}>☁ Cost Breakdown Engine</h1>
            <p style={styles.subtitle}>AWS Infrastructure Cost Visibility — FinOps Layer</p>
          </div>
          <span style={styles.badge}>Mock Data · May 2026</span>
        </div>
      </header>

      <main style={styles.main}>
        {/* ── Summary cards ── */}
        <SummaryCards summary={data.summary} />

        {/* ── Charts row ── */}
        <div style={styles.row}>
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Cost by Category</h2>
            <CategoryChart categories={data.categories} />
          </div>
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Cost by Environment</h2>
            <EnvironmentChart environments={data.environments} />
          </div>
        </div>

        {/* ── Service table ── */}
        <div style={{ ...styles.card, marginBottom: 24 }}>
          <h2 style={styles.cardTitle}>Service-Level Cost Breakdown</h2>
          <ServiceTable services={data.services} />
        </div>

        {/* ── Insights ── */}
        <div style={{ ...styles.card, marginBottom: 24 }}>
          <h2 style={styles.cardTitle}>💡 Cost Insights</h2>
          <InsightsPanel insights={data.insights} />
        </div>
      </main>

      <footer style={styles.footer}>
        Cost Breakdown Engine · FastAPI + React · mock data simulating AWS Cost Explorer
      </footer>
    </div>
  )
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', minHeight: '100vh' },
  center: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' },
  spinner: {
    width: 40, height: 40, borderRadius: '50%',
    border: '4px solid #e2e8f0', borderTopColor: '#4f46e5',
    animation: 'spin 0.8s linear infinite',
  },
  header: { background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)', color: '#fff', padding: '20px 0' },
  headerInner: { maxWidth: 1200, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
  title: { fontSize: 24, fontWeight: 700, letterSpacing: '-0.3px' },
  subtitle: { fontSize: 14, color: '#c7d2fe', marginTop: 4 },
  badge: { background: 'rgba(255,255,255,0.15)', borderRadius: 20, padding: '6px 14px', fontSize: 13, color: '#e0e7ff' },
  main: { maxWidth: 1200, margin: '0 auto', padding: '32px 24px', width: '100%' },
  row: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 },
  card: { background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' },
  cardTitle: { fontSize: 16, fontWeight: 600, marginBottom: 20, color: '#1e1b4b' },
  footer: {
    marginTop: 'auto', padding: '20px 24px', fontSize: 13,
    color: '#64748b', textAlign: 'center', borderTop: '1px solid #e2e8f0',
    background: '#fafafa',
  },
}
