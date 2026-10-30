export type User = { id: string; full_name: string; email: string; role: 'patient' | 'doctor' | 'admin'; availability?: string };
export type Case = { id: string; created_at: string; status: string; assigned_doctor_name?: string; prediction?: { label: string; confidence: number; probabilities: Record<string, number>; model_version: string; gradcam_status?: string }; review?: { decision: string; assessment: string; notes?: string }; report_id?: string };
export function normalizeApiBase(value: string) { return value.trim().replace(/\/+$/, ''); }
export const apiBase = normalizeApiBase(import.meta.env['VITE_API_BASE_URL'] || '');
export const appName = import.meta.env['VITE_APP_NAME'] || 'LungCare AI';
export class ApiError extends Error { constructor(message: string, public status = 0) { super(message); } }
async function request(path: string, options: RequestInit = {}) {
  if (!apiBase) throw new ApiError('The LungCare service is not connected yet. A deployed Flask API address is required.');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  try {
    return await fetch(`${apiBase}${path}`, { ...options, credentials: 'include', signal: controller.signal, headers: { ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }), 'X-LungCare-Request': '1', ...options.headers } });
  } catch { if (controller.signal.aborted) throw new ApiError('The LungCare request timed out. Please try again.'); throw new ApiError('The LungCare service could not be reached. Please try again.'); }
  finally { clearTimeout(timer); }
}
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await request(path, options);
    const payload = await response.json().catch(() => { throw new ApiError('The service returned an invalid response. Check that the API address points to Flask, not the frontend.', response.status); });
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new ApiError('The service returned an invalid response. Check the Flask API address.', response.status);
    if (!response.ok) throw new ApiError(payload.error || 'The request could not be completed.', response.status);
    return payload as T;
}
export const jsonBody = (data: unknown) => JSON.stringify(data);
export function dateTime(value?: string) { return value ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kolkata' }).format(new Date(value)) : '—'; }
export async function privateFile(path: string) {
  const response = await request(path);
  if (!response.ok) throw new ApiError('This file is unavailable or access was denied.', response.status);
  const contentType = response.headers.get('content-type') || '';
  if (!/^(image\/(jpeg|png)|application\/pdf)(;|$)/i.test(contentType)) throw new ApiError('The service returned an invalid private file.', response.status);
  return URL.createObjectURL(await response.blob());
}
export function validateImage(file: File, limitMb: number) {
  if (!['image/jpeg', 'image/png'].includes(file.type)) return 'Choose a JPG, JPEG, or PNG image.';
  if (file.size > limitMb * 1024 * 1024) return `The image must be smaller than ${limitMb} MB.`;
  if (!file.size) return 'The image is empty.';
  return null;
}
