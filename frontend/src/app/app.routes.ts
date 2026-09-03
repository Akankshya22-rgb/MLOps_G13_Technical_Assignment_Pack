import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'models' },
  {
    path: 'models',
    loadComponent: () => import('./features/models/model-list.component').then((m) => m.ModelListComponent)
  },
  {
    path: 'models/:modelId',
    loadComponent: () => import('./features/models/model-detail.component').then((m) => m.ModelDetailComponent)
  },
  {
    path: 'deployments',
    loadComponent: () =>
      import('./features/deployments/deployment-list.component').then((m) => m.DeploymentListComponent)
  },
  {
    path: 'deployments/:deploymentId',
    loadComponent: () =>
      import('./features/deployments/deployment-detail.component').then((m) => m.DeploymentDetailComponent)
  },
  {
    path: 'monitoring',
    loadComponent: () =>
      import('./features/monitoring/monitoring-dashboard.component').then((m) => m.MonitoringDashboardComponent)
  },
  { path: '**', redirectTo: 'models' }
];
