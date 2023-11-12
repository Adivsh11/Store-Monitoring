from django.db import models


class Store(models.Model):
    store_id = models.CharField(max_length=50, primary_key=True)
    timezone_str = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'store'
        managed = True


class StoreStatus(models.Model):
    store_id = models.CharField(max_length=50, null=True)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=25)

    class Meta:
        db_table = 'store_status'
        managed = True


class StoreHours(models.Model):
    store_id = models.CharField(max_length=50, null=True)
    day_of_week = models.IntegerField(null=True, blank=True)
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    class Meta:
        db_table = 'store_hours'
        managed = True


class StoreFileStatus(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE,
                              related_name="file_status",
                              to_field='store_id',
                              null=True, blank=True)

    status = models.CharField(max_length=50)
    report_url = models.FileField(upload_to="reports", null=True, blank=True)
    report_id = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'store_file_status'
        managed = True




