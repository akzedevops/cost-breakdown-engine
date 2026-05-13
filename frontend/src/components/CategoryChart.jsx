import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const COLORS = {
  compute: '#4f46e5',
  storage: '#0891b2',
  network: '#7c3aed',
}

export default function CategoryChart({ categories }) {
  const data = {
    labels: categories.map(c => `${capitalize(c.category)} (${c.percentage}%)`),
    datasets: [{
      data: categories.map(c => c.total_cost),
      backgroundColor: categories.map(c => COLORS[c.category] || '#94a3b8'),
      borderColor: '#fff',
      borderWidth: 3,
      hoverOffset: 8,
    }],
  }

  const options = {
    cutout: '62%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { padding: 16, font: { size: 13, family: 'Inter' }, usePointStyle: true },
      },
      tooltip: {
        callbacks: {
          label: ctx => ` $${ctx.parsed.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
        },
      },
    },
  }

  return (
    <div>
      <div style={{ maxWidth: 280, margin: '0 auto' }}>
        <Doughnut data={data} options={options} />
      </div>
      <div style={styles.legend}>
        {categories.map(c => (
          <div key={c.category} style={styles.legendRow}>
            <span style={{ ...styles.dot, background: COLORS[c.category] || '#94a3b8' }} />
            <span style={styles.name}>{capitalize(c.category)}</span>
            <span style={styles.cost}>${c.total_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            <span style={styles.pct}>{c.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }

const styles = {
  legend: { marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 },
  legendRow: { display: 'flex', alignItems: 'center', gap: 10, fontSize: 14 },
  dot: { width: 10, height: 10, borderRadius: '50%', flexShrink: 0 },
  name: { flex: 1, color: '#374151', fontWeight: 500 },
  cost: { color: '#1a1a2e', fontWeight: 600 },
  pct: { color: '#6b7280', width: 46, textAlign: 'right' },
}
