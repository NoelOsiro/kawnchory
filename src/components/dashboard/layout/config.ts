import type { NavItemConfig } from '@/types/nav';
import { paths } from '@/paths';

export const navItems = [
  { key: 'overview', title: 'Overview', href: paths.dashboard.overview, icon: 'chart-pie' },
  { key: 'records', title: 'Cattle Records', href: paths.dashboard.animals, icon: 'treeStructure' },
  { key: 'inventory', title: 'Inventory Management', href: paths.dashboard.inventory, icon: 'vault' },
  { key: 'tracking', title: 'Tracking/Localization', href: paths.dashboard.tracking, icon: 'mappin' },
  { key: 'integrations', title: 'Integrations', href: paths.dashboard.integrations, icon: 'plugs-connected' },
  { key: 'settings', title: 'Settings', href: paths.dashboard.settings, icon: 'gear-six' },
  { key: 'account', title: 'Account', href: paths.dashboard.account, icon: 'user' },
  { key: 'error', title: 'Error', href: paths.errors.notFound, icon: 'x-square' },
] satisfies NavItemConfig[];
