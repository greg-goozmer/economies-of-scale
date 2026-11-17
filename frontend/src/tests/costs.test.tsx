import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { AxiosError, type AxiosResponse } from 'axios';
import App from '../App';
import { costsApi } from '../api/costsClient';
import { COSTS_MOCK, filterCosts, nextCost } from '../modules/costsMock';
import { createCostsStore, loadCosts, mockCost, resetCostUser, setCostMinimum, setCostUser } from '../store/costsStore';
import { CostImage, CostVideo, DEFAULT_COST_IMAGE, DEFAULT_COST_VIDEO } from '../components/CostMedia';

beforeEach(() => { vi.restoreAllMocks(); });
const response = <T,>(data: T) => ({ data } as AxiosResponse<T>);
const offline = () => new AxiosError('Offline', 'ERR_NETWORK');

describe('Redux и API издержек', () => {
  it('передаёт границы фильтра сгенерированному клиенту', async () => {
    const api = vi.spyOn(costsApi.api, 'listCosts').mockResolvedValue(response([]));
    const store = createCostsStore();
    await store.dispatch(loadCosts({ minimum: '25', maximum: '26' }));
    expect(api.mock.calls[0][0]).toEqual({ min_cost_code: 25, max_cost_code: 26 });
    expect(store.getState().costs.appliedMinimum).toBe('25');
    expect(store.getState().costs.mock).toBe(false);
  });
  it('возвращает отфильтрованные mock только гостю при сетевой ошибке', async () => {
    vi.spyOn(costsApi.api, 'listCosts').mockRejectedValue(offline());
    const store = createCostsStore();
    await store.dispatch(loadCosts({ minimum: '25', maximum: '26' }));
    expect(store.getState().costs.items.map(item => item.cost_id)).toEqual([1, 2]);
    expect(store.getState().costs.mock).toBe(true);
    store.dispatch(setCostUser({ user_id: 1, user_name: 'test' }));
    const result = await store.dispatch(loadCosts({ minimum: '', maximum: '' }));
    expect(loadCosts.rejected.match(result)).toBe(true);
    expect(store.getState().costs.items).toEqual([]);
  });
  it('не скрывает ошибки HTTP 422 демонстрационными данными', async () => {
    vi.spyOn(costsApi.api, 'listCosts').mockRejectedValue(new AxiosError('Invalid', 'ERR_BAD_REQUEST', undefined, undefined, { ...response({ detail: 'Invalid range' }), status: 422 }));
    const store = createCostsStore();
    await store.dispatch(loadCosts({ minimum: '', maximum: '' }));
    expect(store.getState().costs.mock).toBe(false);
    expect(store.getState().costs.error).toBe('Invalid range');
  });
  it('игнорирует запоздалый ответ предыдущего фильтра', async () => {
    let finish: (value: AxiosResponse) => void = () => {};
    vi.spyOn(costsApi.api, 'listCosts')
      .mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }))
      .mockResolvedValueOnce(response([mockCost(COSTS_MOCK[1])]));
    const store = createCostsStore();
    const first = store.dispatch(loadCosts({ minimum: '', maximum: '' }));
    await store.dispatch(loadCosts({ minimum: '26', maximum: '26' }));
    finish(response(COSTS_MOCK.map(mockCost)));
    await first;
    expect(store.getState().costs.items.map(item => item.cost_id)).toEqual([2]);
    expect(store.getState().costs.pending).toBe(0);
  });
  it('новое хранилище после F5 гостевое, выход очищает фильтры', () => {
    const store = createCostsStore();
    store.dispatch(setCostUser({ user_id: 1, user_name: 'test' }));
    store.dispatch(setCostMinimum('25'));
    expect(createCostsStore().getState().costs.user).toBeNull();
    store.dispatch(resetCostUser());
    expect(store.getState().costs.minimum).toBe('');
    expect(store.getState().costs.user).toBeNull();
  });
});

describe('Интерфейс гостя', () => {
  it('показывает mock, применяет фильтр и открывает вход', async () => {
    vi.spyOn(costsApi.api, 'listCosts').mockRejectedValue(offline());
    render(<Provider store={createCostsStore()}><MemoryRouter><App /></MemoryRouter></Provider>);
    await screen.findByText('Найдено: 6');
    expect(screen.getByRole('button', { name: 'Добавление' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Вход' })).not.toBeDisabled();
    fireEvent.change(screen.getByLabelText('Код издержки от'), { target: { value: '25' } });
    fireEvent.change(screen.getByLabelText('Код издержки до'), { target: { value: '26' } });
    fireEvent.click(screen.getByRole('button', { name: 'Применить' }));
    await screen.findByText('Найдено: 2');
    fireEvent.click(screen.getByRole('button', { name: 'Вход' }));
    await screen.findByRole('heading', { name: 'Вход пользователя' });
  });
  it('сохраняет включительную фильтрацию и порядок локальной коллекции', () => {
    expect(filterCosts(COSTS_MOCK, '20', '25').map(cost => cost.cost_id)).toEqual([1, 3, 4]);
    expect(nextCost([COSTS_MOCK[0], COSTS_MOCK[2]], 1)?.cost_id).toBe(3);
  });
});

describe('Медиа по умолчанию', () => {
  it('подставляет изображение при пустом URL', () => {
    render(<CostImage url="" name="Издержка" />);
    expect(screen.getByRole('img')).toHaveAttribute('src', DEFAULT_COST_IMAGE);
  });
  it('подставляет изображение после ошибки загрузки', () => {
    render(<CostImage url="/missing.png" name="Издержка" />);
    fireEvent.error(screen.getByRole('img'));
    expect(screen.getByRole('img')).toHaveAttribute('src', DEFAULT_COST_IMAGE);
  });
  it('подставляет видео при пустом URL', () => {
    render(<CostVideo url="" image="" />);
    expect(screen.getByLabelText('Видео издержки')).toHaveAttribute('src', DEFAULT_COST_VIDEO);
  });
});
