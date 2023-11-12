
import uuid
from .models import Store, StoreStatus, StoreHours
from django.utils import timezone
from pytz import timezone as pytz_timezone
import datetime
import csv
import os
import tempfile
from .constants import ReportStatus, StoreStatusConstant, BATCH_SIZE


def generate_store_report(report):
    csv_data = []
    #TODO Processing Records in Batches and the function would be
    # running in a seperate thread

    stores = Store.objects.all()[:BATCH_SIZE]
    for store in stores:
        data = generate_report_data(store)
        csv_data.append(data)

    generate_csv_file(report, csv_data)


def generate_report_data(store):
    tz = store.timezone_str or 'America/Chicago'
    target_timezone = pytz_timezone(tz)

    # hard coding current time as max of all the logs
    time = StoreStatus.objects.all().order_by('-timestamp_utc').first().timestamp_utc
    local_time = time.astimezone(target_timezone)
    utc_timezone = pytz_timezone('UTC')
    utc_time = time.astimezone(utc_timezone)
    current_day = local_time.weekday()
    current_time = local_time.time()

    # last one hour
    last_one_hour_data = get_last_one_hour_data(store.store_id, utc_time, current_day, current_time)
    # last one day
    last_one_day_data = get_last_one_day_data(store.store_id, utc_time, current_day, current_time)
    # last one week
    last_one_week_data = get_last_one_week_data(store.store_id, utc_time, current_day, current_time)
    data = []

    data.append(store.store_id)
    data.extend(list(last_one_hour_data.values()))
    data.extend(list(last_one_day_data.values()))
    data.extend(list(last_one_week_data.values()))

    return data


def generate_csv_file(report, csv_data):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = f"{report.pk}.csv"
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id", "last_one_hour uptime",
                                 "last_one_hour downtime",
                                 "last_one_hour unit",
                                 "last_one_day uptime",
                                 "last_one_day downtime",
                                 "last_one_day unit",
                                 "last_one_week uptime",
                                 "last_one_week downtime",
                                 "last_one_week unit"])
            for data in csv_data:
                csv_writer.writerow(data)

        report.report_url.save(file_name, open(temp_file_path, "rb"))
        report.status = ReportStatus.COMPLETED
        report.save()


def get_last_one_hour_data(store_id, utc_time, current_day, current_time):
    last_one_hour_data = {"uptime": 0, "downtime": 0, "unit": "minutes"}
    # checking if store is open in last one hour
    is_store_open = StoreHours.objects.filter(day_of_week=current_day,
                                              start_time_local__lte=current_time,
                                              end_time_local__gte=current_time,
                                              store_id=store_id).exists()
    if not is_store_open:
        return last_one_hour_data

    last_one_hour_logs = StoreStatus.objects.filter(
        timestamp_utc__gte=utc_time - datetime.timedelta(hours=1),
        store_id=store_id
    ).order_by('timestamp')

    # checking if store is open in last one hour and last log status is active
    if last_one_hour_logs:
        last_one_hour_log_status = last_one_hour_logs[0].status.upper()
        if last_one_hour_log_status == StoreStatus.ACTIVE:
            last_one_hour_data["uptime"] = 60
        else:
            last_one_hour_data["downtime"] = 60

    return last_one_hour_data


def get_last_one_day_data(store_id, utc_time, current_day, current_time):
    last_one_day_data = {"uptime": 0, "downtime": 0, "unit": "hours"}
    one_day_ago = current_day - 1 if current_day > 0 else 6
    # checking if store is open in last one day
    is_store_open = StoreHours.objects.filter(day_of_week__gte=one_day_ago,
                                              day_of_week__lte=current_day,
                                              start_time_local__lte=current_time,
                                              end_time_local__gte=current_time,
                                              store_id=store_id).exists()
    if not is_store_open:
        return last_one_day_data
    # getting all the logs in last one day
    last_one_day_logs = StoreStatus.objects.filter(
        timestamp_utc__gte=utc_time - datetime.timedelta(days=1),
        store_id=store_id
    ).order_by('timestamp')

    for log in last_one_day_logs:
        # checkig if log is in store business hours
        log_in_store_business_hours = StoreHours.objects.filter(
            day_of_week=log.timestamp.weekday(),
            start_time_local__lte=log.timestamp.time(),
            end_time_local__gte=log.timestamp.time(),
            store_id=store_id
            ).exists()
        # checking if log is in store business hours and status is active
        if not log_in_store_business_hours:
            continue
        if log.status.upper() == StoreStatusConstant.ACTIVE:
            last_one_day_data["uptime"] += 1
        else:
            last_one_day_data["downtime"] += 1
    return last_one_day_data


def get_last_one_week_data(store_id, utc_time, current_day, current_time):
    last_one_week_data = {"uptime": 0, "downtime": 0, "unit": "hours"}
    one_week_ago = current_day - 7 if current_day > 0 else 0
    # checking if store is open in last one week
    is_store_open = StoreHours.objects.filter(day_of_week__gte=one_week_ago,
                                              day_of_week__lte=current_day,
                                              start_time_local__lte=current_time,
                                              end_time_local__gte=current_time,
                                              store_id=store_id).exists()
    if not is_store_open:
        return last_one_week_data
    # getting all the logs in last one week
    last_one_week_logs = StoreStatus.objetcs.filter(
        timestamp_utc__gte=utc_time - datetime.timedelta(days=7),
        store_id=store_id
    ).order_by('timestamp')

    for log in last_one_week_logs:
        # checking if log is in store business hours
        log_in_store_business_hours = StoreHours.objects.filter(
            day_of_week=log.timestamp.weekday(),
            start_time_local__lte=log.timestamp.time(),
            end_time_local__gte=log.timestamp.time(),
            store_id=store_id
            ).exists()
        # checking if log is in store business hours and status is active
        if not log_in_store_business_hours:
            continue
        if log.status.upper() == StoreStatus.ACTIVE:
            last_one_week_data["uptime"] += 1
        else:
            last_one_week_data["downtime"] += 1

    return last_one_week_data


def generate_report_id():
    return str(uuid.uuid4())


