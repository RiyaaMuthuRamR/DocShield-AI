export default function Metric({ label, value, detail, tone = 'neutral' }) {
  return <div className={`metric metric-${tone}`}>
    <span className="metric-label">{label}</span>
    <strong>{value}</strong>
    {detail && <small>{detail}</small>}
  </div>;
}
