__author__ = 'jcranwellward'
import datetime

from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.admin.models import LogEntry

from partners.models import PCA, PartnerOrganization, PCASectorOutput
from reports.models import Sector, ResultStructure, Indicator
from locations.models import CartoDBTable, GatewayType, Governorate, Region
from funds.models import Donor
from trips.models import Trip, ActionPoint


class DashboardView(TemplateView):

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):

        sectors = {}
        now = datetime.datetime.now()
        structure = self.request.GET.get('structure', ResultStructure.objects.filter(
            from_date__lte=now, to_date__gte=now))
        try:
            current_structure = ResultStructure.objects.get(id=structure)
        except ResultStructure.DoesNotExist:
            current_structure = None
        for sector in Sector.objects.all():
            indicators = sector.indicator_set.filter(
                view_on_dashboard=True,
            )
            if current_structure:
                indicators = indicators.filter(
                    result_structure=current_structure
                )
            if not indicators:
                continue

            sectors[sector.name] = []
            for indicator in indicators:
                programmed = indicator.programmed(
                    result_structure=current_structure
                )
                sectors[sector.name].append(
                    {
                        'indicator': indicator,
                        'programmed': programmed,
                    }
                )

        return {
            'sectors': sectors,
            'current_structure': current_structure,
            'structures': ResultStructure.objects.all(),
            'pcas': {
                'active': PCA.objects.filter(
                    result_structure=current_structure,
                    status=PCA.ACTIVE,
                    amendment_number=0,
                ).count(),
                'implemented': PCA.objects.filter(
                    result_structure=current_structure,
                    status=PCA.IMPLEMENTED,
                    amendment_number=0,
                ).count(),
                'in_process': PCA.objects.filter(
                    result_structure=current_structure,
                    status=PCA.IN_PROCESS,
                ).count(),
                'cancelled': PCA.objects.filter(
                    result_structure=current_structure,
                    status=PCA.CANCELLED,
                    amendment_number=0,
                ).count(),
            }
        }


class MapView(TemplateView):

    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        return {
            'gateway_list': GatewayType.objects.all(),
            'governorate_list': Governorate.objects.all(),
            'sectors_list': Sector.objects.all(),
            'result_structure_list': ResultStructure.objects.all(),
            'region_list': Region.objects.all(),
            'partner_list': PartnerOrganization.objects.all(),
            'indicator_list': Indicator.objects.all(),
            'output_list': PCASectorOutput.objects.all(),
            'donor_list': Donor.objects.all()
        }


class CmtView(TemplateView):

    template_name = 'cmt_dashboard.html'

    def get_context_data(self, **kwargs):
        return {
            'tables': CartoDBTable.objects.all(),
            'gateway_list': GatewayType.objects.all(),
            'governorate_list': Governorate.objects.all(),
            'sectors_list': Sector.objects.all(),
            'result_structure_list': ResultStructure.objects.all(),
            'region_list': Region.objects.all(),
            'partner_list': PartnerOrganization.objects.all(),
            'indicator_list': Indicator.objects.all(),
            'output_list': PCASectorOutput.objects.all(),
            'donor_list': Donor.objects.all()
        }


class UserDashboardView(TemplateView):
    template_name = 'user_dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        now = datetime.datetime.now()
        current_structure = ResultStructure.objects.filter(
            from_date__lte=now, to_date__gte=now)

        return {
            'trips_current': Trip.objects.filter(
                Q(status=Trip.PLANNED) | Q(status=Trip.SUBMITTED) | Q(status=Trip.APPROVED),
                owner=user),
            'trips_previous': Trip.objects.filter(
                Q(status=Trip.COMPLETED) | Q(status=Trip.CANCELLED),
                owner=user),
            'trips_supervised': user.supervised_trips.filter(
                Q(status=Trip.APPROVED) | Q(status=Trip.SUBMITTED)),
            'log': LogEntry.objects.select_related().filter(
                user=self.request.user).order_by("-id")[:10],
            'pcas': PCA.objects.filter(
                unicef_managers=user, status=PCA.ACTIVE).order_by("number", "-amendment_number")[:10],
            'action_points': ActionPoint.objects.filter(
                Q(status='open') | Q(status='ongoing'),
                person_responsible=user).order_by("-due_date")[:10]
        }
