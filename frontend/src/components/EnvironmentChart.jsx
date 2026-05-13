import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const ENV_COLORS = {
  production: '#4f46e5',
  staging:    '#0891b2',
  dev:        '#7c3aed',
}

export default function EnvironmentChart({ environments }) {
  const data = {
    labels: environments.map(e => capitalize(e.environment)),
    datasets: [{
      label: 'Monthly Cost (USD)',
      data: environments.map(e => e.total_cost),
      backgroundColor: environments.map(e => ENV_COLORS[e.environment] || '#94a3b8'),
      borderRadius: 8,
      borderSkipped: false,
    }],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` $${ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 13, family: 'Inter' } } },
      y: {
        grid: { color: '#f1f5f9' },
        ticks: {
          font: { size: 12, family: 'Inter' },
          callback: v => `$${(v / 1000).toFixed(1)}k`,
        },
      },
    },
  }

  return (
    <div>
      <Bar data={data} options={options} />
      <div style={styles.table}>
        {environments.map(e => (
          <div key={e.environment} style={styles.row}>
            <span style={{ ...styles.dot, background: ENV_COLORS[e.environment] }} />
            <span style={styles.name}>{capitalize(e.environment)}</span>
            <span style={styles.resources}>{e.resource_count} resources</span>
            <span style={styles.cost}>${e.total_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            <span style={styles.pct}>{e.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }

const styles = {
  table: { marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 },
  row: { display: 'flex', alignItems: 'center', gap: 10, fontSize: 14 },
  dot: { width: 10, height: 10, borderRadius: '50%', flexShrink: 0 },
  name: { flex: 1, color: '#374151', fontWeight: 500 },
  resources: { color: '#9ca3af', fontSize: 12 },
  cost: { color: '#1a1a2e', fontWeight: 600 },
  pct: { color: '#6b7280', width: 46, textAlign: 'right' },
}
