import { useState } from 'react'

const CATEGORY_COLORS = {
  compute: { bg: '#eef2ff', text: '#4f46e5' },
  storage: { bg: '#ecfeff', text: '#0891b2' },
  network: { bg: '#f5f3ff', text: '#7c3aed' },
}

export default function ServiceTable({ services, total }) {
  const [filter, setFilter] = useState('all')

  const filtered = filter === 'all' ? services : services.filter(s => s.category === filter)

  return (
    <div>
      {/* Filter tabs */}
      <div style={styles.tabs}>
        {['all', 'compute', 'storage', 'network'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{ ...styles.tab, ...(filter === f ? styles.tabActive : {}) }}
          >
            {capitalize(f)}
          </button>
        ))}
      </div>

      {/* Table */}
      <div style={styles.tableWrap}>
        <table style={styles.table}>
          <thead>
            <tr>
              {['Service', 'Category', 'Resources', 'Monthly Cost', '% of Total', 'Cost Bar'].map(h => (
                <th key={h} style={styles.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((s, i) => {
              const colors = CATEGORY_COLORS[s.category] || { bg: '#f3f4f6', text: '#374151' }
              return (
                <tr key={`${s.service}-${i}`} style={i % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                  <td style={styles.td}>
                    <span style={styles.svcName}>{s.service}</span>
                  </td>
                  <td style={styles.td}>
                    <span style={{ ...styles.badge, background: colors.bg, color: colors.text }}>
                      {capitalize(s.category)}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: 'center' }}>{s.resource_count}</td>
                  <td style={{ ...styles.td, fontWeight: 600 }}>
                    ${s.total_cost.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td style={{ ...styles.td, color: '#6b7280' }}>{s.percentage}%</td>
                  <td style={{ ...styles.td, minWidth: 120 }}>
                    <div style={styles.barBg}>
                      <div style={{ ...styles.barFill, width: `${s.percentage}%`, background: colors.text }} />
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }

const styles = {
  tabs: { display: 'flex', gap: 8, marginBottom: 16 },
  tab: {
    padding: '6px 16px', borderRadius: 20, border: '1px solid #e5e7eb',
    background: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 500,
    color: '#6b7280', transition: 'all 0.15s',
  },
  tabActive: { background: '#4f46e5', color: '#fff', borderColor: '#4f46e5' },
  tableWrap: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: {
    padding: '10px 16px', textAlign: 'left', fontSize: 12,
    fontWeight: 600, color: '#6b7280', textTransform: 'uppercase',
    letterSpacing: '0.05em', borderBottom: '2px solid #f1f5f9',
  },
  td: { padding: '12px 16px', borderBottom: '1px solid #f9fafb', color: '#1a1a2e' },
  rowEven: { background: '#fff' },
  rowOdd:  { background: '#fafafa' },
  svcName: { fontWeight: 600 },
  badge: { padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600 },
  barBg: { height: 8, borderRadius: 4, background: '#f1f5f9', overflow: 'hidden' },
  barFill: { height: '100%', borderRadius: 4, transition: 'width 0.6s ease' },
}
