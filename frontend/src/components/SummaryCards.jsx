export default function SummaryCards({ summary }) {
  const cards = [
    {
      label: 'Total Monthly Cost',
      value: `$${summary.total_monthly_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      sub: `${summary.total_resources} resources tracked`,
      color: '#4f46e5',
      bg: '#eef2ff',
      icon: '💰',
    },
    {
      label: 'Top Cost Category',
      value: capitalize(summary.top_category),
      sub: 'Largest spend category',
      color: '#0891b2',
      bg: '#ecfeff',
      icon: '📊',
    },
    {
      label: 'Top AWS Service',
      value: summary.top_service,
      sub: 'Highest individual service spend',
      color: '#7c3aed',
      bg: '#f5f3ff',
      icon: '⚙️',
    },
    {
      label: 'Top Environment',
      value: capitalize(summary.top_environment),
      sub: 'Highest spend environment',
      color: '#059669',
      bg: '#ecfdf5',
      icon: '🌍',
    },
  ]

  return (
    <div style={styles.grid}>
      {cards.map(card => (
        <div key={card.label} style={{ ...styles.card, borderTop: `3px solid ${card.color}` }}>
          <div style={styles.row}>
            <span style={styles.icon}>{card.icon}</span>
            <span style={{ ...styles.label, color: card.color }}>{card.label}</span>
          </div>
          <p style={styles.value}>{card.value}</p>
          <p style={styles.sub}>{card.sub}</p>
        </div>
      ))}
    </div>
  )
}

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''
}

const styles = {
  grid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginBottom: 24 },
  card: { background: '#fff', borderRadius: 12, padding: '20px 22px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' },
  row: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 },
  icon: { fontSize: 18 },
  label: { fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' },
  value: { fontSize: 26, fontWeight: 700, color: '#1a1a2e', marginBottom: 4 },
  sub: { fontSize: 12, color: '#6b7280' },
}
