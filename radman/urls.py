"""
URL configuration for radman project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from radiopharma import views as rpv
from procedures import views as pv
from patients import views as ptv
from schedule import views as sv  # Import the schedule views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('radiopharma/compund', rpv.CompoundListView.as_view(), name='compound_list'),
    path('radiopharma/compound/add/', rpv.CompoundCreateView.as_view(), name='compound_add'),
    path('radiopharma/compound/<int:pk>/', rpv.CompoundUpdateView.as_view(), name='compound_edit'),
    path('radiopharma/', rpv.BatchListView.as_view(), name='batch_list'),
    path('radiopharma/add/', rpv.BatchCreateView.as_view(), name='batch_add'),
    path('radiopharma/useddose/add/', rpv.UsedDoseCreateView.as_view(), name='useddose_add'),
    path('radiopharma/batch/<int:pk>/discard/', rpv.BatchDiscardView.as_view(), name='batch_discard'),
    path('procedures/', pv.ProcedureListView.as_view(), name='procedure_list'),
    path('procedures/create/', pv.ProcedureCreateView.as_view(), name='procedure_create'),
    path('procedures/<int:pk>/edit/', pv.ProcedureUpdateView.as_view(), name='procedure_edit'),

    path('patients/', ptv.PatientListView.as_view(), name='patient_list'),
    path('patients/add', ptv.AddPatientView.as_view(), name='patient_add'),
    path('patients/<int:pk>/edit', ptv.EditPatientView.as_view(), name='patient_edit'),
    path('patients/<int:pk>/delete/', ptv.DeletePatientView.as_view(), name='patient_delete'),

    path('', sv.ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/add', sv.ScheduleCreateView.as_view(), name='schedule_add'),
    path('schedule/clear/', sv.ClearScheduleView.as_view(), name='schedule_clear'),
    path('schedule/calculate/', sv.CalculateScheduleView.as_view(), name='schedule_calculate'),
]
