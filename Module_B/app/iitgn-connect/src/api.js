const API_BASE = 'http://localhost:5001/api';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function api(path, options = {}) {
  const { method = 'GET', body, headers = {} } = options;
  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...headers,
    },
  };
  if (body) config.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, config);
  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(data?.error || `Request failed: ${res.status}`);
  }
  return data;
}

// Auth
export const authApi = {
  login: (username, password) => api('/auth/login', { method: 'POST', body: { username, password } }),
  register: (data) => api('/auth/register', { method: 'POST', body: data }),
  sendOtp: (email) => api('/auth/send-otp', { method: 'POST', body: { email } }),
  verifyOtp: (email, otp) => api('/auth/verify-otp', { method: 'POST', body: { email, otp } }),
};

// Posts
export const postsApi = {
  getFeed: (feed = 'global') => api(`/posts?feed=${feed}`),
  create: (content, groupId) => api('/posts', { method: 'POST', body: { content, groupId } }),
  update: (id, content) => api(`/posts/${id}`, { method: 'PUT', body: { content } }),
  delete: (id) => api(`/posts/${id}`, { method: 'DELETE' }),
  getComments: (postId) => api(`/posts/${postId}/comments`),
  addComment: (postId, content) => api(`/posts/${postId}/comments`, { method: 'POST', body: { content } }),
  updateComment: (commentId, content) => api(`/comments/${commentId}`, { method: 'PUT', body: { content } }),
  deleteComment: (commentId) => api(`/comments/${commentId}`, { method: 'DELETE' }),
  toggleLike: (postId) => api(`/posts/${postId}/like`, { method: 'POST' }),
};

// Groups
export const groupsApi = {
  getAll: (search = '') => api(`/groups/?search=${encodeURIComponent(search)}`),
  getOne: (id) => api(`/groups/${id}`),
  join: (id) => api(`/groups/${id}/join`, { method: 'POST' }),
  leave: (id) => api(`/groups/${id}/leave`, { method: 'POST' }),
  getPosts: (id) => api(`/groups/${id}/posts`),
};

// Jobs
export const jobsApi = {
  getAll: () => api('/jobs'),
  create: (data) => api('/jobs', { method: 'POST', body: data }),
  update: (id, data) => api(`/jobs/${id}`, { method: 'PUT', body: data }),
  delete: (id) => api(`/jobs/${id}`, { method: 'DELETE' }),
  getReferrals: () => api('/referrals'),
  createReferral: (data) => api('/referrals', { method: 'POST', body: data }),
  updateReferral: (id, status) => api(`/referrals/${id}`, { method: 'PUT', body: { status } }),
};

// Polls
export const pollsApi = {
  getAll: () => api('/polls/'),
  create: (data) => api('/polls/', { method: 'POST', body: data }),
  vote: (pollId, optionId) => api(`/polls/${pollId}/vote`, { method: 'POST', body: { optionId } }),
};

// Attendance
export const attendanceApi = {
  getClass: (studentId, month, year) => api(`/attendance/class?studentId=${studentId}&month=${month}&year=${year}`),
  getMess: (studentId, month, year) => api(`/attendance/mess?studentId=${studentId}&month=${month}&year=${year}`),
  getStreaks: (studentId) => api(`/attendance/streaks?studentId=${studentId}`),
  getLeaderboard: () => api('/attendance/leaderboard'),
};

// Profile
export const profileApi = {
  get: (id) => api(`/profile/${id}`),
  getClaims: (id) => api(`/profile/${id}/claims`),
  createClaim: (id, data) => api(`/profile/${id}/claims`, { method: 'POST', body: data }),
  updateClaim: (claimId, data) => api(`/claims/${claimId}`, { method: 'PUT', body: data }),
  deleteClaim: (claimId) => api(`/claims/${claimId}`, { method: 'DELETE' }),
  voteClaim: (claimId, isAgree) => api(`/claims/${claimId}/vote`, { method: 'POST', body: { isAgree } }),
};

// Members
export const membersApi = {
  getAll: (search = '', type = 'All') => api(`/members/?search=${encodeURIComponent(search)}&type=${encodeURIComponent(type)}`),
};

// Admin
export const adminApi = {
  getStats: () => api('/admin/stats'),
  getMembers: () => api('/admin/members'),
  updateMember: (id, data) => api(`/admin/members/${id}`, { method: 'PUT', body: data }),
  deleteMember: (id) => api(`/admin/members/${id}`, { method: 'DELETE' }),
  getGroups: () => api('/admin/groups'),
  deleteGroup: (id) => api(`/admin/groups/${id}`, { method: 'DELETE' }),
};

// Settings
export const settingsApi = {
  updateProfile: (data) => api('/settings/profile', { method: 'PUT', body: data }),
  changePassword: (data) => api('/settings/password', { method: 'PUT', body: data }),
  deleteAccount: () => api('/settings/account', { method: 'DELETE' }),
};
