import { useState } from 'react';
import { ArrowLeftRight, LoaderCircle } from 'lucide-react';
import { compareIdentity } from '../services/api';

const blank = { name: '', dob: '', document_number: '', document_type: '' };
export default function IdentityCheck() {
  const [one, setOne] = useState({ ...blank });
  const [two, setTwo] = useState({ ...blank });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const update = (setter, key, value) => setter((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    try { setResult(await compareIdentity({ document1: one, document2: two })); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  const fields = [['name', 'Full name'], ['dob', 'Date of birth'], ['document_number', 'Document number'], ['document_type', 'Document type (e.g. passport)']];
  return <section className="panel identity-panel">
    <div className="section-heading"><div><p className="eyebrow">CROSS-DOCUMENT CHECK</p><h2>Identity consistency</h2><p className="muted">Compare two documents for the same person. Document numbers are compared only when both types match.</p></div><span className="section-icon"><ArrowLeftRight size={21}/></span></div>
    <form onSubmit={submit}>
      <div className="identity-grid">{[[one, setOne, 'Document A'], [two, setTwo, 'Document B']].map(([values, setter, title]) => <div className="identity-doc" key={title}>
        <h3>{title}</h3>{fields.map(([key, label]) => <label className="field" key={key}>{label}<input value={values[key]} onChange={(e) => update(setter, key, e.target.value)} required={key === 'name' || key === 'dob'} placeholder={key === 'dob' ? 'DD/MM/YYYY' : label}/></label>)}
      </div>)}</div>
      <button className="primary-button" type="submit" disabled={busy}>{busy ? <LoaderCircle className="spin" size={17}/> : <ArrowLeftRight size={17}/>} Compare documents</button>
    </form>
    {error && <p className="error-box">{error}</p>}
    {result && <div className="identity-result"><div><span className="eyebrow">RESULT</span><h3>{result.status}</h3><p>Consistency score: <b>{result.identity_score}/100</b></p></div><pre>{JSON.stringify(result.checks, null, 2)}</pre></div>}
    <p className="fine-print">This checks field consistency only. It does not confirm that either document is genuine.</p>
  </section>;
}
