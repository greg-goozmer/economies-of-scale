import { describe, expect, it } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { COSTS_MOCK, filterCosts, nextCost } from '../modules/costsMock';
import { CostImage, CostVideo, DEFAULT_COST_IMAGE, DEFAULT_COST_VIDEO } from '../components/CostMedia';

const open = (route = '/costs') => render(<MemoryRouter initialEntries={[route]}><App /></MemoryRouter>);

describe('Коллекция издержек', () => {
  it('пустые границы возвращают все карточки', () => expect(filterCosts(COSTS_MOCK, '', '')).toHaveLength(6));
  it('диапазон включительный', () => expect(filterCosts(COSTS_MOCK, '20', '25').map(cost => cost.cost_id)).toEqual([1, 3, 4]));
  it('нижняя граница отдельно', () => expect(filterCosts(COSTS_MOCK, '26', '')).toHaveLength(3));
  it('верхняя граница отдельно', () => expect(filterCosts(COSTS_MOCK, '', '20')).toHaveLength(2));
  it('нет результатов', () => expect(filterCosts(COSTS_MOCK, '45', '50')).toHaveLength(0));
  it('следующая по массиву, а не ID + 1', () => expect(nextCost([COSTS_MOCK[0], COSTS_MOCK[2]], 1)?.cost_id).toBe(3));
  it('на последней нет следующей', () => expect(nextCost(COSTS_MOCK, 6)).toBeUndefined());
});

describe('Гостевой интерфейс', () => {
  it('показывает шесть карточек и две недоступные вкладки', () => {
    open();
    expect(screen.getByText('Найдено: 6')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Добавление/ })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Вход/ })).toBeDisabled();
  });
  it('фильтр срабатывает по кнопке, сброс возвращает все', () => {
    open();
    fireEvent.change(screen.getByLabelText('Код издержки от'), { target: { value: '25' } });
    fireEvent.change(screen.getByLabelText('Код издержки до'), { target: { value: '26' } });
    expect(screen.getByText('Найдено: 6')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Применить' }));
    expect(screen.getByText('Найдено: 2')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Сбросить' }));
    expect(screen.getByText('Найдено: 6')).toBeInTheDocument();
  });
  it('сохраняет границы фильтра после возврата из ленты', () => {
    open();
    fireEvent.change(screen.getByLabelText('Код издержки от'), { target: { value: '25' } });
    fireEvent.change(screen.getByLabelText('Код издержки до'), { target: { value: '26' } });
    fireEvent.click(screen.getByRole('button', { name: 'Применить' }));
    fireEvent.click(screen.getByRole('link', { name: /Аренда кофемашины/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Плитка' }));
    expect(screen.getByLabelText('Код издержки от')).toHaveValue(25);
    expect(screen.getByLabelText('Код издержки до')).toHaveValue(26);
    expect(screen.getByText('Найдено: 2')).toBeInTheDocument();
  });
  it('не применяет перевёрнутый диапазон', () => {
    open();
    fireEvent.change(screen.getByLabelText('Код издержки от'), { target: { value: '50' } });
    fireEvent.change(screen.getByLabelText('Код издержки до'), { target: { value: '10' } });
    expect(screen.getByRole('button', { name: 'Применить' })).toBeDisabled();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });
  it('переходит по карточке в ленту и к следующей', () => {
    open();
    fireEvent.click(screen.getByRole('link', { name: /Аренда кофемашины/ }));
    expect(screen.getByRole('heading', { name: 'Аренда кофемашины' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Следующая издержка/ }));
    expect(screen.getByRole('heading', { name: 'Подписка для кассы' })).toBeInTheDocument();
  });
  it('раскрывает описание и параметры', () => {
    open('/costs/feed/1');
    fireEvent.click(screen.getByRole('button', { name: 'Ещё' }));
    expect(screen.getByRole('button', { name: 'Свернуть' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Параметры издержки' }));
    expect(screen.getByText('Код издержки')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument();
  });
  it('открывается по прямой ссылке и показывает отсутствие неизвестного ID', () => {
    open('/costs/feed/999');
    expect(screen.getByRole('heading', { name: 'Издержка не найдена' })).toBeInTheDocument();
  });
  it('в пустом списке отключает вкладку ленты', () => {
    open();
    fireEvent.change(screen.getByLabelText('Код издержки от'), { target: { value: '99' } });
    fireEvent.click(screen.getByRole('button', { name: 'Применить' }));
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Лента/ })).toBeDisabled();
  });
});

describe('Локальные медиа по умолчанию', () => {
  it('подставляет изображение при пустом URL', () => {
    render(<CostImage url="" name="Подписка" />);
    expect(screen.getByRole('img')).toHaveAttribute('src', DEFAULT_COST_IMAGE);
  });
  it('подставляет изображение при ошибке загрузки', () => {
    render(<CostImage url="/missing.svg" name="Подписка" />);
    fireEvent.error(screen.getByRole('img'));
    expect(screen.getByRole('img')).toHaveAttribute('src', DEFAULT_COST_IMAGE);
  });
  it('подставляет настоящее локальное видео при пустом URL', () => {
    render(<CostVideo url="" image="" />);
    expect(screen.getByLabelText('Видео издержки')).toHaveAttribute('src', DEFAULT_COST_VIDEO);
  });
});
