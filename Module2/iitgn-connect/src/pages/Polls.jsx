import { useState, useEffect, useCallback } from 'react';
import { BarChart3, Clock, Plus, CheckCircle2, User, X } from 'lucide-react';
import { pollsApi } from '../api';
import { useAuth } from '../contexts/AuthContext';

const PRIMARY = '#4F46E5';

const s = {
  container: { maxWidth: 960, margin: '0 auto', padding: '32px 16px' },
  headerRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 },
  headingGroup: { display: 'flex', alignItems: 'center', gap: 12 },
  heading: { fontSize: 28, fontWeight: 700, color: '#1E1B4B', margin: 0 },
  subtitle: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  btnCreate: {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    padding: '10px 20px', borderRadius: 10, border: 'none',
    background: PRIMARY, color: '#fff', fontWeight: 600,
    fontSize: 14, cursor: 'pointer',
  },
  card: {
    background: '#fff', borderRadius: 12, padding: 24, marginBottom: 20,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
    border: '1px solid #F3F4F6',
  },
  question: { fontSize: 18, fontWeight: 700, color: '#1E1B4B', margin: '0 0 4px' },
  meta: { display: 'flex', alignItems: 'center', gap: 14, fontSize: 13, color: '#9CA3AF', marginBottom: 16, flexWrap: 'wrap' },
  metaItem: { display: 'flex', alignItems: 'center', gap: 4 },
  optionRow: {
    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
    borderRadius: 8, marginBottom: 8, cursor: 'pointer',
    border: '2px solid #E5E7EB', transition: 'all 0.2s',
  },
  optionRowVoted: {
    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
    borderRadius: 8, marginBottom: 8, cursor: 'default',
    border: `2px solid ${PRIMARY}`, background: '#EEF2FF',
  },
  optionText: { flex: 1, fontSize: 14, fontWeight: 500, color: '#1E1B4B' },
  optionVotes: { fontSize: 13, fontWeight: 700, color: PRIMARY, minWidth: 40, textAlign: 'right' },
  barBg: { flex: 2, height: 8, background: '#E5E7EB', borderRadius: 99, overflow: 'hidden' },
  barFill: (pct) => ({ width: `${pct}%`, height: '100%', background: PRIMARY, borderRadius: 99, transition: 'width 0.4s ease' }),
  totalVotes: { fontSize: 13, color: '#6B7280', fontWeight: 600, marginTop: 8 },
  timeTag: (active) => ({
    display: 'inline-flex', alignItems: 'center', gap: 4,
    padding: '3px 10px', borderRadius: 99, fontSize: 12, fontWeight: 600,
    background: active ? '#D1FAE5' : '#FEE2E2',
    color: active ? '#065F46' : '#991B1B',
  }),
  sectionLabel: { fontSize: 20, fontWeight: 700, color: '#1E1B4B', marginBottom: 16, marginTop: 40 },
  formCard: {
    background: '#fff', borderRadius: 12, padding: 24, marginBottom: 28,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
    border: `2px solid ${PRIMARY}`,
  },
  input: {
    width: '100%', padding: '10px 14px', borderRadius: 8,
    border: '1px solid #D1D5DB', fontSize: 14, outline: 'none',
    boxSizing: 'border-box', marginBottom: 10,
  },
  optionInputRow: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 },
  btnSmall: {
    padding: '6px 14px', borderRadius: 8, border: 'none',
    background: '#E5E7EB', color: '#374151', fontWeight: 600,
    fontSize: 13, cursor: 'pointer',
  },
  btnSubmit: {
    padding: '10px 20px', borderRadius: 8, border: 'none',
    background: PRIMARY, color: '#fff', fontWeight: 600,
    fontSize: 14, cursor: 'pointer', marginTop: 8,
  },
  removeBtn: {
    background: 'none', border: 'none', cursor: 'pointer', padding: 2,
    display: 'flex', alignItems: 'center',
  },
};

export default function Polls() {
  const { user } = useAuth();
  const now = new Date();
  const [pollList, setPollList] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newOptions, setNewOptions] = useState(['', '']);

  const fetchPolls = useCallback(async () => {
    try {
      const data = await pollsApi.getAll();
      setPollList(data);
    } catch (err) { console.error('Failed to fetch polls:', err); }
  }, []);

  useEffect(() => { fetchPolls(); }, [fetchPolls]);

  const isActive = (poll) => new Date(poll.ExpiresAt) > now;
  const activePolls = pollList.filter(isActive);
  const expiredPolls = pollList.filter(p => !isActive(p));

  const getTimeRemaining = (expiresAt) => {
    const diff = new Date(expiresAt) - now;
    if (diff <= 0) return 'Expired';
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days}d ${hours % 24}h left`;
    return `${hours}h left`;
  };

  const handleVote = async (pollId, optionId) => {
    const poll = pollList.find(p => p.PollID === pollId);
    if (poll?.userVotedOptionId) return;
    try {
      await pollsApi.vote(pollId, optionId);
      await fetchPolls();
    } catch (err) { console.error('Failed to vote:', err); }
  };

  const handleCreatePoll = async () => {
    const filtered = newOptions.filter(o => o.trim());
    if (!newQuestion.trim() || filtered.length < 2) return;
    try {
      await pollsApi.create({
        question: newQuestion.trim(),
        expiresAt: new Date(Date.now() + 7 * 86400000).toISOString(),
        options: filtered.map(o => o.trim()),
      });
      setNewQuestion('');
      setNewOptions(['', '']);
      setShowForm(false);
      await fetchPolls();
    } catch (err) { console.error('Failed to create poll:', err); }
  };

  const renderPoll = (poll) => {
    const pollOpts = poll.options || [];
    const totalVotes = pollOpts.reduce((sum, o) => sum + o.votes, 0);
    const active = isActive(poll);
    const userVote = poll.userVotedOptionId;

    return (
      <div key={poll.PollID} style={s.card}>
        <h3 style={s.question}>{poll.Question}</h3>
        <div style={s.meta}>
          <span style={s.metaItem}><User size={13} /> {poll.CreatorName || 'Unknown'}</span>
          <span style={s.timeTag(active)}>
            <Clock size={12} />
            {active ? getTimeRemaining(poll.ExpiresAt) : 'Expired'}
          </span>
        </div>
        {pollOpts.map(opt => {
          const pct = totalVotes > 0 ? Math.round((opt.votes / totalVotes) * 100) : 0;
          const isVoted = userVote === opt.OptionID;
          return (
            <div
              key={opt.OptionID}
              style={isVoted ? s.optionRowVoted : s.optionRow}
              onClick={() => active && handleVote(poll.PollID, opt.OptionID)}
            >
              {isVoted && <CheckCircle2 size={16} color={PRIMARY} />}
              <span style={s.optionText}>{opt.OptionText}</span>
              <div style={s.barBg}>
                <div style={s.barFill(pct)} />
              </div>
              <span style={s.optionVotes}>{pct}%</span>
            </div>
          );
        })}
        <div style={s.totalVotes}>{totalVotes} total votes</div>
      </div>
    );
  };

  return (
    <div style={s.container}>
      <div style={s.headerRow}>
        <div style={s.headingGroup}>
          <BarChart3 size={28} color={PRIMARY} />
          <div>
            <h1 style={s.heading}>Polls</h1>
            <p style={s.subtitle}>Vote and share your opinion</p>
          </div>
        </div>
        <button style={s.btnCreate} onClick={() => setShowForm(!showForm)}>
          <Plus size={16} />
          Create Poll
        </button>
      </div>

      {showForm && (
        <div style={s.formCard}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#1E1B4B', marginBottom: 12 }}>New Poll</h3>
          <input
            style={s.input}
            placeholder="Enter your question..."
            value={newQuestion}
            onChange={e => setNewQuestion(e.target.value)}
          />
          {newOptions.map((opt, i) => (
            <div key={i} style={s.optionInputRow}>
              <input
                style={{ ...s.input, marginBottom: 0, flex: 1 }}
                placeholder={`Option ${i + 1}`}
                value={opt}
                onChange={e => {
                  const copy = [...newOptions];
                  copy[i] = e.target.value;
                  setNewOptions(copy);
                }}
              />
              {newOptions.length > 2 && (
                <button style={s.removeBtn} onClick={() => setNewOptions(prev => prev.filter((_, j) => j !== i))}>
                  <X size={16} color="#9CA3AF" />
                </button>
              )}
            </div>
          ))}
          <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
            <button style={s.btnSmall} onClick={() => setNewOptions(prev => [...prev, ''])}>+ Add Option</button>
            <button style={s.btnSubmit} onClick={handleCreatePoll}>Create Poll</button>
          </div>
        </div>
      )}

      {activePolls.length > 0 && (
        <>
          <h2 style={s.sectionLabel}>Active Polls</h2>
          {activePolls.map(renderPoll)}
        </>
      )}

      {expiredPolls.length > 0 && (
        <>
          <h2 style={s.sectionLabel}>Past Polls</h2>
          {expiredPolls.map(renderPoll)}
        </>
      )}
    </div>
  );
}
