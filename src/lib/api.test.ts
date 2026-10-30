import { describe, it, expect, vi, afterEach } from 'vitest';
import { validateImage, normalizeApiBase } from './api';
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.resetModules(); });
describe('Flask connection configuration', () => {
  it('removes whitespace and every trailing slash', () => expect(normalizeApiBase(' https://api.example.test/// ')).toBe('https://api.example.test'));
  it('never reports success when the API address is missing', async () => {
    vi.stubEnv('VITE_API_BASE_URL', ''); vi.resetModules();
    const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher);
    const { api } = await import('./api');
    await expect(api('/api/auth/login', { method: 'POST' })).rejects.toThrow('A deployed Flask API address is required');
    expect(fetcher).not.toHaveBeenCalled();
  });
  it('preserves the exact Flask endpoint and credentialed CSRF header', async () => {
    vi.stubEnv('VITE_API_BASE_URL', ' https://api.example.test/// '); vi.resetModules();
    const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ api: 'ok' }), { status: 200 })); vi.stubGlobal('fetch', fetcher);
    const { api } = await import('./api');
    await expect(api('/health')).resolves.toEqual({ api: 'ok' });
    expect(fetcher).toHaveBeenCalledWith('https://api.example.test/health', expect.objectContaining({ credentials: 'include', headers: expect.objectContaining({ 'X-LungCare-Request': '1' }) }));
  });
  it('rejects an HTML response instead of treating the frontend as a successful API', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.test'); vi.resetModules();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>not Flask</html>', { status: 200 })));
    const { api } = await import('./api');
    await expect(api('/health')).rejects.toThrow('invalid response');
  });
  it('rejects null JSON instead of accepting fabricated success', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.test'); vi.resetModules();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('null')));
    const { api } = await import('./api');
    await expect(api('/health')).rejects.toThrow('invalid response');
  });
  it('never creates a private image URL from a frontend HTML page', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.test'); vi.resetModules();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>login</html>', { headers: { 'Content-Type': 'text/html' } })));
    const { privateFile } = await import('./api');
    await expect(privateFile('/api/cases/123/image')).rejects.toThrow('invalid private file');
  });
});
describe('CT upload rules', () => {
  it('accepts JPG and PNG', () => { for (const type of ['image/jpeg', 'image/png']) expect(validateImage(new File(['image'], 'scan', { type }), 10)).toBe(null); });
  it('rejects unsupported content types', () => expect(validateImage(new File(['gif'], 'scan.gif', { type: 'image/gif' }), 10)).toBeTruthy());
  it('enforces the configured MB limit', () => expect(validateImage(new File([new Uint8Array(1024 * 1024 + 1)], 'scan.png', { type: 'image/png' }), 1)).toBeTruthy());
});
