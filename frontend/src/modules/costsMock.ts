export interface CostItem {
  cost_id: number;
  cost_name: string;
  cost_description: string;
  cost_behavior: 'fixed' | 'variable';
  cost_code: number;
  cost_image_url: string;
  cost_video_url: string;
  like_count: number;
}

// Только локальная коллекция. Сервер, сессия и MinIO для ЛР5 не нужны.
export const COSTS_MOCK: CostItem[] = [
  { cost_id: 1, cost_name: 'Аренда кофемашины', cost_code: 25, cost_behavior: 'fixed',
    cost_description: 'Аренда оборудования относится к постоянным издержкам. Платёж не зависит от количества приготовленных напитков в пределах выбранного периода. Код 25 — учебный код карточки, а не сумма расходов.',
    cost_image_url: '/media/cost-equipment.svg', cost_video_url: '/media/cost-preview.mp4', like_count: 12 },
  { cost_id: 3, cost_name: 'Кофейное зерно', cost_code: 20, cost_behavior: 'variable',
    cost_description: 'Кофейное зерно расходуется при приготовлении каждой порции. При увеличении количества напитков общий расход сырья растёт. Это пример переменных производственных издержек.',
    cost_image_url: '/media/cost-beans.svg', cost_video_url: '/media/cost-preview.mp4', like_count: 8 },
  { cost_id: 8, cost_name: 'Подписка для кассы', cost_code: 26, cost_behavior: 'fixed',
    cost_description: 'Регулярный платёж за программное обеспечение кассы не зависит от объёма выпуска. В пределах периода подписка рассматривается как постоянная издержка.',
    cost_image_url: '', cost_video_url: '', like_count: 5 },
  { cost_id: 12, cost_name: 'Стаканы и крышки', cost_code: 10, cost_behavior: 'variable',
    cost_description: 'Одноразовая упаковка используется для каждого напитка навынос. Суммарные затраты зависят от числа проданных порций.',
    cost_image_url: '/media/cost-cups.svg', cost_video_url: '/media/cost-preview.mp4', like_count: 3 },
];

export function filterCosts(costs: CostItem[], minimum: string, maximum: string) {
  return costs.filter(cost => (minimum === '' || cost.cost_code >= Number(minimum)) &&
    (maximum === '' || cost.cost_code <= Number(maximum)));
}

export function nextCost(costs: CostItem[], currentId: number) {
  const index = costs.findIndex(cost => cost.cost_id === currentId);
  return costs[index + 1]; // ID не обязан быть последовательным; конец списка без зацикливания.
}
