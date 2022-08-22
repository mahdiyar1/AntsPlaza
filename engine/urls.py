from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views


router = SimpleRouter()
router.register('orders', views.OrderViewSet)
router.register('strategy_settings', views.StrategySettingViewSet)
router.register('strategy_symbols', views.StrategySymbolViewSet)
router.register('symbols', views.SymbolViewSet)
router.register('strategy_executions', views.PeriodicTaskViewSet)

urlpatterns = [
    path('run_short/', views.run_short_all_strategies),
    path('run_long/', views.run_long_all_strategies),
    path('terminate_short/', views.terminate_short_all_strategies),
    path('terminate_long/', views.terminate_long_all_strategies),
    path('terminate/', views.terminate_all_strategies),
    path('check_risk/', views.check_risk_all_strategies),
    path('update_strategy_symbol/', views.update_strategy_symbol),
]

urlpatterns += router.urls
