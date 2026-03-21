import { useState } from 'react';
import { Send, Image } from 'lucide-react';

const styles = {
  card: {
    background: '#fff',
    borderRadius: 12,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
    padding: 20,
    marginBottom: 16,
  },
  wrapper: {
    display: 'flex',
    gap: 14,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    fontWeight: 700,
    fontSize: 16,
    flexShrink: 0,
  },
  inputArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  textarea: {
    width: '100%',
    minHeight: 80,
    padding: '12px 14px',
    border: '1.5px solid #e5e7eb',
    borderRadius: 10,
    fontSize: 15,
    lineHeight: 1.5,
    color: '#1f2937',
    resize: 'vertical',
    outline: 'none',
    fontFamily: 'inherit',
    transition: 'border-color 0.15s',
    boxSizing: 'border-box',
  },
  bottomRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  attachBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: 14,
    color: '#6b7280',
    padding: '6px 10px',
    borderRadius: 8,
  },
  postBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 20px',
    background: '#4F46E5',
    color: '#fff',
    border: 'none',
    borderRadius: 10,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background 0.15s',
  },
  postBtnDisabled: {
    background: '#a5b4fc',
    cursor: 'not-allowed',
  },
};

function getInitials(name) {
  if (!name) return '?';
  const parts = name.split(' ');
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return name[0].toUpperCase();
}

export default function CreatePost({ user, onPost }) {
  const [content, setContent] = useState('');
  const [focused, setFocused] = useState(false);

  const handlePost = () => {
    if (!content.trim()) return;
    onPost(content.trim());
    setContent('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handlePost();
    }
  };

  const isEmpty = !content.trim();

  return (
    <div style={styles.card}>
      <div style={styles.wrapper}>
        <div style={{ ...styles.avatar, backgroundColor: user?.avatarColor || '#4F46E5' }}>
          {getInitials(user?.Name)}
        </div>
        <div style={styles.inputArea}>
          <textarea
            style={{
              ...styles.textarea,
              borderColor: focused ? '#4F46E5' : '#e5e7eb',
            }}
            placeholder="What's on your mind?"
            value={content}
            onChange={e => setContent(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            onKeyDown={handleKeyDown}
          />
          <div style={styles.bottomRow}>
            <button
              style={styles.attachBtn}
              onMouseEnter={e => { e.currentTarget.style.background = '#f9fafb'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'none'; }}
            >
              <Image size={18} />
              Photo
            </button>
            <button
              onClick={handlePost}
              disabled={isEmpty}
              style={{
                ...styles.postBtn,
                ...(isEmpty ? styles.postBtnDisabled : {}),
              }}
              onMouseEnter={e => {
                if (!isEmpty) e.currentTarget.style.background = '#4338CA';
              }}
              onMouseLeave={e => {
                if (!isEmpty) e.currentTarget.style.background = '#4F46E5';
              }}
            >
              <Send size={16} />
              Post
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
