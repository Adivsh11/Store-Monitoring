import traceback
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .store_report_helper import generate_report_id, \
    generate_store_report
from .constants import ReportStatus
from .models import StoreFileStatus, StoreFileStatus
from .serializers import ReportIdSerializer
from django.conf import settings
from django.http import HttpResponse
from .generic_response_utils import log_and_respond


class StoreReport(APIView):

    def get(self, request):
        try:
            report_id = generate_report_id()

            # TODO All the db query operations need to have a utils function

            report_object = StoreFileStatus.objects.create(
                report_id=report_id,
                status=ReportStatus.CREATED
            )
            # TODO to run this function asynchrously using celery ,redis

            generate_store_report(report_object)
            return log_and_respond(
                message_code=200,
                response_data={"report_id": report_id}
            )
        except:
            return log_and_respond(
                message_code=500,
                exception=str(traceback.format_exc())
            )

    def post(self, request):
        try:
            serializer = ReportIdSerializer(data=request.data)
            if not serializer.is_valid():
                return log_and_respond(
                    message_code=400,
                    field_name='report_id'
                )

            report_id = serializer.validated_data.get("report_id")
            # TODO All the db query operations need to have a utils function
            report_object = StoreFileStatus.objects.filter(
                report_id=report_id
            ).order_by('id').last()

            if report_object.status == ReportStatus.COMPLETED:
                report_path = os.path.join(settings.MEDIA_ROOT, report_object.report_url.name)
                with open(report_path, 'r') as csv_file:
                    content = csv_file.read()
                response = HttpResponse(content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{report_object.report_url.name}"'
                return response
            else:
                return log_and_respond(
                    message_code=200,
                    response_data={"status": ReportStatus.RUNNING}
                )
        except:
            return log_and_respond(
                message_code=500,
                exception=str(traceback.format_exc())
            )
