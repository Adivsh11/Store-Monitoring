from rest_framework import serializers


class ReportIdSerializer(serializers.Serializer):
    report_id = serializers.CharField(max_length=50, min_length=1)
