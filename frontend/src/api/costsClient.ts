import axios from 'axios';
import { Api } from './generated/CostsApi';

export const costsApi = new Api({ baseURL: '', withCredentials: true, timeout: 10000 });
export const costUsersApi = axios.create({ baseURL: '/api/users', withCredentials: true, timeout: 10000 });

export function costMediaUrl(url: string) {
  if (!url) return '';
  const parsed = new URL(url, window.location.origin);
  if (['localhost', '127.0.0.1'].includes(parsed.hostname) && parsed.port === '9000') {
    return `/s3${parsed.pathname}${parsed.search}`;
  }
  return url;
}

export function costError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 401) return 'Сессия истекла. Войдите снова.';
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (error.response?.status === 422) return 'Проверьте заполнение полей.';
    if (!error.response) return 'Сервер недоступен. Повторите действие позже.';
  }
  return 'Не удалось выполнить действие.';
}
