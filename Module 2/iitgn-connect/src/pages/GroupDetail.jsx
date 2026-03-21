import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Users, Shield, UserCog, User, ArrowLeft, Calendar,
} from 'lucide-react';
import { groupsApi, postsApi } from '../api';
import { useAuth } from '../contexts/AuthContext';
import PostCard from '../components/PostCard';
import CreatePost from '../components/CreatePost';

/* ── helpers ── */
function getInitials(name) {
  if (!name) return '?';
  const parts = name.split(' ');
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return name[0].toUpperCase();
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

const roleIcon = {
  Admin: Shield,
  Moderator: UserCog,
  Member: User,
};
const roleBadgeColor = {
  Admin: { bg: '#FEF3C7', text: '#D97706' },
  Moderator: { bg: '#EDE9FE', text: '#7C3AED' },
  Member: { bg: '#F3F4F6', text: '#6b7280' },
};

/* ── styles ── */
const s = {
  page: { maxWidth: 800, margin: '0 auto' },
  backLink: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 14,
    color: '#4F46E5',
    textDecoration: 'none',
    fontWeight: 600,
    marginBottom: 16,
  },
  headerCard: {
    background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
    borderRadius: 16,
    padding: 32,
    color: '#fff',
    marginBottom: 24,
    position: 'relative',
    overflow: 'hidden',
  },
  headerPattern: {
    position: 'absolute',
    top: 0, right: 0, bottom: 0, left: 0,
    opacity: 0.07,
    backgroundImage: 'radial-gradient(circle at 20% 50%, #fff 1px, transparent 1px), radial-gradient(circle at 80% 20%, #fff 1px, transparent 1px)',
    backgroundSize: '60px 60px',
  },
  headerContent: { position: 'relative', zIndex: 1 },
  groupName: { fontSize: 28, fontWeight: 800, margin: '0 0 8px' },
  groupDesc: { fontSize: 15, opacity: 0.9, lineHeight: 1.6, marginBottom: 20 },
  headerMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: 24,
    flexWrap: 'wrap',
    fontSize: 14,
    opacity: 0.9,
  },
  headerMetaItem: { display: 'flex', alignItems: 'center', gap: 6 },
  section: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    padding: 24,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: '#111827',
    margin: '0 0 16px',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  memberRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 0',
    borderBottom: '1px solid #f3f4f6',
  },
  memberAvatar: {
    width: 38,
    height: 38,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    fontWeight: 700,
    fontSize: 14,
    flexShrink: 0,
  },
  memberName: {
    fontSize: 14,
    fontWeight: 600,
    color: '#111827',
    textDecoration: 'none',
  },
  memberUsername: { fontSize: 12, color: '#9ca3af' },
  roleBadge: {
    marginLeft: 'auto',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '3px 10px',
    borderRadius: 8,
    fontSize: 12,
    fontWeight: 600,
  },
  empty: { fontSize: 14, color: '#9ca3af', textAlign: 'center', padding: 24 },
  twoCol: {
    display: 'grid',
    gridTemplateColumns: '1fr 300px',
    gap: 24,
    alignItems: 'start',
  },
};

export default function GroupDetail() {
  const { groupId } = useParams();
  const gid = Number(groupId);
  const { user: currentUser } = useAuth();

  const [group, setGroup] = useState(null);
  const [groupMembers, setGroupMembers] = useState([]);
  const [groupPosts, setGroupPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const fetchGroup = useCallback(async () => {
    try {
      const data = await groupsApi.getOne(gid);
      setGroup(data);
      setGroupMembers(
        (data.members || []).sort((a, b) => {
          const order = { Admin: 0, Moderator: 1, Member: 2 };
          return (order[a.Role] ?? 2) - (order[b.Role] ?? 2);
        })
      );
    } catch (err) {
      console.error('Failed to fetch group:', err);
      setNotFound(true);
    }
  }, [gid]);

  const fetchPosts = useCallback(async () => {
    try {
      const data = await groupsApi.getPosts(gid);
      setGroupPosts(data);
    } catch (err) {
      console.error('Failed to fetch group posts:', err);
    }
  }, [gid]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      await Promise.all([fetchGroup(), fetchPosts()]);
      setLoading(false);
    }
    load();
  }, [fetchGroup, fetchPosts]);

  if (loading) {
    return (
      <div style={s.page}>
        <Link to="/groups" style={s.backLink}>
          <ArrowLeft size={16} /> Back to Groups
        </Link>
        <div style={s.section}>
          <p style={s.empty}>Loading...</p>
        </div>
      </div>
    );
  }

  if (notFound || !group) {
    return (
      <div style={s.page}>
        <Link to="/groups" style={s.backLink}>
          <ArrowLeft size={16} /> Back to Groups
        </Link>
        <div style={s.section}>
          <p style={s.empty}>Group not found.</p>
        </div>
      </div>
    );
  }

  const handleNewPost = async (content) => {
    try {
      await postsApi.create(content, gid);
      await fetchPosts();
    } catch (err) {
      console.error('Failed to create post:', err);
    }
  };

  return (
    <div style={s.page}>
      <Link to="/groups" style={s.backLink}>
        <ArrowLeft size={16} /> Back to Groups
      </Link>

      {/* Group Header */}
      <div style={s.headerCard}>
        <div style={s.headerPattern} />
        <div style={s.headerContent}>
          <h1 style={s.groupName}>{group.Name}</h1>
          <p style={s.groupDesc}>{group.Description}</p>
          <div style={s.headerMeta}>
            <div style={s.headerMetaItem}>
              <Users size={16} />
              {groupMembers.length} member{groupMembers.length !== 1 ? 's' : ''}
            </div>
            {group.AdminName && (
              <div style={s.headerMetaItem}>
                <Shield size={16} />
                Admin: {group.AdminName}
              </div>
            )}
            <div style={s.headerMetaItem}>
              <Calendar size={16} />
              Created {formatDate(group.CreatedAt || '2025-01-01')}
            </div>
          </div>
        </div>
      </div>

      {/* Two-column layout: Feed + Members sidebar */}
      <div style={s.twoCol}>
        {/* Feed Column */}
        <div>
          <CreatePost user={currentUser} onPost={handleNewPost} />

          {groupPosts.length === 0 ? (
            <div style={s.section}>
              <p style={s.empty}>No posts in this group yet. Be the first to post!</p>
            </div>
          ) : (
            groupPosts.map(post => (
              <PostCard
                key={post.PostID}
                post={post}
              />
            ))
          )}
        </div>

        {/* Members Sidebar */}
        <div style={s.section}>
          <h3 style={s.sectionTitle}>
            <Users size={18} color="#4F46E5" /> Members
          </h3>
          {groupMembers.map((member) => {
            const RoleIcon = roleIcon[member.Role] || User;
            const colors = roleBadgeColor[member.Role] || roleBadgeColor.Member;
            return (
              <div key={member.MemberID} style={s.memberRow}>
                <div style={{ ...s.memberAvatar, backgroundColor: member.avatarColor || '#4F46E5' }}>
                  {getInitials(member.Name)}
                </div>
                <div>
                  <Link to={`/profile/${member.MemberID}`} style={s.memberName}>
                    {member.Name}
                  </Link>
                  <div style={s.memberUsername}>@{member.Username}</div>
                </div>
                <span style={{ ...s.roleBadge, background: colors.bg, color: colors.text }}>
                  <RoleIcon size={12} />
                  {member.Role}
                </span>
              </div>
            );
          })}
          {groupMembers.length === 0 && (
            <p style={s.empty}>No members yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
