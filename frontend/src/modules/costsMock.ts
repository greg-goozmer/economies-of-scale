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

// Опубликованные карточки из seed ЛР2; все медиа локальные, API не нужен.
export const COSTS_MOCK: CostItem[] = [
  { cost_id: 1, cost_name: 'Аренда кофемашины', cost_code: 25, cost_behavior: 'fixed',
    cost_description: 'Аренда производственного оборудования относится к постоянным издержкам: платёж не зависит от количества приготовленных напитков в пределах выбранного периода.',
    cost_image_url: '/media/coffee_machine_rental.png', cost_video_url: '/media/coffee_machine_rental.mp4', like_count: 3 },
  { cost_id: 2, cost_name: 'Подписка для кассы', cost_code: 26, cost_behavior: 'fixed',
    cost_description: 'Подписка обеспечивает работу кассового программного обеспечения. Регулярный платёж считается постоянной издержкой и относится к счёту 26.',
    cost_image_url: '/media/cash_register_subscription.png', cost_video_url: '/media/cash_register_subscription.mp4', like_count: 1 },
  { cost_id: 3, cost_name: 'Кофейное зерно', cost_code: 20, cost_behavior: 'variable',
    cost_description: 'Кофейное зерно непосредственно расходуется при приготовлении напитков, поэтому относится к переменным издержкам и учитывается на счёте 20.',
    cost_image_url: '/media/coffee_beans.png', cost_video_url: '/media/coffee_beans.mp4', like_count: 4 },
  { cost_id: 4, cost_name: 'Молоко', cost_code: 20, cost_behavior: 'variable',
    cost_description: 'Расход молока изменяется вместе с объёмом выпуска молочных напитков, поэтому статья является переменной и относится к счёту 20.',
    cost_image_url: '/media/milk.png', cost_video_url: '/media/milk.mp4', like_count: 2 },
  { cost_id: 5, cost_name: 'Бумажные стаканы', cost_code: 44, cost_behavior: 'variable',
    cost_description: 'Одноразовая упаковка расходуется по мере продажи напитков и образует переменные издержки, учитываемые на счёте 44.',
    cost_image_url: '/media/paper_cups.png', cost_video_url: '/media/paper_cups.mp4', like_count: 1 },
  { cost_id: 6, cost_name: 'Крышки для стаканов', cost_code: 44, cost_behavior: 'variable',
    cost_description: 'Крышки используются вместе со стаканами, поэтому их расход растёт с количеством продаж. Это переменная издержка счёта 44.',
    cost_image_url: '', cost_video_url: '', like_count: 2 },
];

export function filterCosts(costs: CostItem[], minimum: string, maximum: string) {
  return costs.filter(cost => (minimum === '' || cost.cost_code >= Number(minimum)) &&
    (maximum === '' || cost.cost_code <= Number(maximum)));
}

export function nextCost(costs: CostItem[], currentId: number) {
  const index = costs.findIndex(cost => cost.cost_id === currentId);
  return index < 0 ? undefined : costs[index + 1]; // Следующий элемент, а не ID + 1.
}
