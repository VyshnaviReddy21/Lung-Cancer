import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, apiBase, type User } from '@/lib/api';
const AuthContext = createContext<{ user: User | null; loading: boolean; error: string; refresh: () => Promise<void>; logout: () => Promise<void> }>({ user: null, loading: true, error: '', refresh: async () => {}, logout: async () => {} });
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  async function refresh() { setLoading(true); try { const data = await api<{ user: User }>('/api/auth/me'); setUser(data.user); setError(''); } catch (e) { setUser(null); setError(e instanceof Error ? e.message : 'Session unavailable'); } finally { setLoading(false); } }
  useEffect(() => { if (apiBase) void refresh(); else setLoading(false); }, []);
  async function logout() { await api('/api/auth/logout', { method: 'POST' }); setUser(null); }
  return <AuthContext.Provider value={{ user, loading, error, refresh, logout }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
