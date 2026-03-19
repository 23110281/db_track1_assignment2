import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Users, UserPlus, Check, Search, Shield } from 'lucide-react';
import { groupsApi } from '../api';

/* ── styles ── */
const s = {
  page: { maxWidth: 900, margin: '0 auto' },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 24,
    flexWrap: 'wrap',
    gap: 16,
  },
  title: { fontSize: 26, fontWeight: 700, color: '#111827', margin: 0, display: 'flex', alignItems: 'center', gap: 10 },
  searchWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: '#fff',
    border: '1.5px solid #e5e7eb',
    borderRadius: 10,
    padding: '8px 14px',
    width: 280,
  },
  searchInput: {
    border: 'none',
    outline: 'none',
    fontSize: 14,
    color: '#374151',
    flex: 1,
    background: 'transparent',
    fontFamily: 'inherit',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: 20,
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    padding: 24,
    display: 'flex',
    flexDirection: 'column',
    transition: 'box-shadow 0.2s, transform 0.2s',
    cursor: 'pointer',
    textDecoration: 'none',
    color: 'inherit',
  },
  cardHover: {
    boxShadow: '0 4px 16px rgba(79,70,229,0.13)',
    transform: 'translateY(-2px)',
  },
  groupIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    marginBottom: 14,
    flexShrink: 0,
  },
  groupName: {
    fontSize: 17,
    fontWeight: 700,
    color: '#111827',
    marginBottom: 6,
    lineHeight: 1.3,
  },
  groupDesc: {
    fontSize: 13,
    color: '#6b7280',
    lineHeight: 1.5,
    marginBottom: 16,
    flex: 1,
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  metaRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 8,
    marginTop: 'auto',
  },
  memberCount: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 13,
    color: '#6b7280',
    fontWeight: 500,
  },
  adminTag: {
    fontSize: 12,
    color: '#4F46E5',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
  },
  joinBtn: {
    padding: '8px 20px',
    borderRadius: 10,
    border: 'none',
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    transition: 'background 0.15s',
    marginTop: 14,
  },
  joinBtnDefault: {
    background: '#4F46E5',
    color: '#fff',
  },
  joinBtnJoined: {
    background: '#D1FAE5',
    color: '#059669',
    cursor: 'default',
  },
  empty: { fontSize: 14, color: '#9ca3af', textAlign: 'center', padding: 40 },
};

export default function Groups() {
  const [searchTerm, setSearchTerm] = useState('');
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hoveredCard, setHoveredCard] = useState(null);

  const fetchGroups = useCallback(async (search = '') => {
    try {
      const data = await groupsApi.getAll(search);
      setGroups(data);
    } catch (err) {
      console.error('Failed to fetch groups:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      fetchGroups(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, fetchGroups]);

  const handleJoinLeave = async (e, groupId, isMember) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      if (isMember) {
        await groupsApi.leave(groupId);
      } else {
        await groupsApi.join(groupId);
      }
      await fetchGroups(searchTerm);
    } catch (err) {
      console.error('Failed to join/leave group:', err);
    }
  };

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>
          <Users size={24} color="#4F46E5" /> Campus Groups
        </h1>
        <div style={s.searchWrap}>
          <Search size={16} color="#9ca3af" />
          <input
            style={s.searchInput}
            placeholder="Search groups..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <p style={s.empty}>Loading groups...</p>
      ) : groups.length === 0 ? (
        <p style={s.empty}>No groups found.</p>
      ) : (
        <div style={s.grid}>
          {groups.map(group => {
            const count = group.memberCount || 0;
            const joined = group.isMember;

            return (
              <Link
                key={group.GroupID}
                to={`/groups/${group.GroupID}`}
                style={{
                  ...s.card,
                  ...(hoveredCard === group.GroupID ? s.cardHover : {}),
                }}
                onMouseEnter={() => setHoveredCard(group.GroupID)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div style={s.groupIcon}>
                  <Users size={22} />
                </div>
                <div style={s.groupName}>{group.Name}</div>
                <div style={s.groupDesc}>{group.Description}</div>

                <div style={s.metaRow}>
                  <div style={s.memberCount}>
                    <Users size={14} />
                    {count} member{count !== 1 ? 's' : ''}
                  </div>
                  {group.AdminName && (
                    <div style={s.adminTag}>
                      <Shield size={12} />
                      {group.AdminName.split(' ')[0]}
                    </div>
                  )}
                </div>

                <button
                  style={{
                    ...s.joinBtn,
                    ...(joined ? s.joinBtnJoined : s.joinBtnDefault),
                  }}
                  onClick={(e) => handleJoinLeave(e, group.GroupID, joined)}
                  onMouseEnter={e => {
                    if (!joined) e.currentTarget.style.background = '#4338CA';
                  }}
                  onMouseLeave={e => {
                    if (!joined) e.currentTarget.style.background = '#4F46E5';
                  }}
                >
                  {joined ? (
                    <><Check size={14} /> Joined</>
                  ) : (
                    <><UserPlus size={14} /> Join Group</>
                  )}
                </button>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
