const TYPE_STYLES = {
  category:    { border: '#4f46e5', bg: '#eef2ff', icon: '📊' },
  service:     { border: '#0891b2', bg: '#ecfeff', icon: '⚙️' },
  environment: { border: '#059669', bg: '#ecfdf5', icon: '🌍' },
  general:     { border: '#d97706', bg: '#fffbeb', icon: '💡' },
}

export default function InsightsPanel({ insights }) {
  return (
    <div>
      {/* Overall summary sentence */}
      <div style={styles.summary}>{insights.summary}</div>

      {/* Individual insight cards */}
      <div style={styles.grid}>
        {insights.insights.map((item, i) => {
          const s = TYPE_STYLES[item.type] || TYPE_STYLES.general
          return (
            <div key={i} style={{ ...styles.card, borderLeft: `4px solid ${s.border}`, background: s.bg }}>
              <span style={styles.icon}>{s.icon}</span>
              <p style={styles.msg}>{item.message}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const styles = {
  summary: {
    background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10,
    padding: '14px 18px', fontSize: 15, color: '#1e293b', lineHeight: 1.6,
    marginBottom: 20, fontWeight: 500,
  },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 },
  card: {
    borderRadius: 10, padding: '14px 16px',
    display: 'flex', alignItems: 'flex-start', gap: 10,
  },
  icon: { fontSize: 18, flexShrink: 0, marginTop: 1 },
  msg: { fontSize: 14, color: '#1e293b', lineHeight: 1.55 },
}
