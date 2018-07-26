import json

from rangefilter.filter import DateRangeFilter
import requests
import xlwt

from django.contrib import admin
from django.http import HttpResponse

from .models import Bid


class WmIDListFilter(admin.SimpleListFilter):

    title = 'Указан wm ID'

    parameter_name = 'wm_id__exact'

    def lookups(self, request, model_admin):

        return (
            ('empty', 'Пустое'),
            ('filled', 'Указано'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'empty':
            return queryset.filter(wm_id__exact='')

        if self.value() == 'filled':
            return queryset.exclude(wm_id__exact='')


def linkprofit_check(modeladmin, request, queryset):
    data_for_sending = []
    for q in queryset:
        data_for_sending.append(
            {
                "id": q.id,
                "contact_phone": q.contact_phone,
                "city": q.city,
                "name": q.name,
                "credit_sum": q.credit_sum,
                "termin": q.termin,
                "termin_type": q.termin_type,
                "wm_id": q.wm_id,
                "any_param": q.any_param,
                "created_dt": q.created_dt.strftime("%Y-%m-%d"),
                "updated_dt": q.updated_dt.strftime("%Y-%m-%d"),
            }
        )

    request_headers = {
        "Content-Type": "application/json"
    }

    endpoint = "https://saleshub.co.ua/api/v1/linkprofit/"
    r = requests.post(
        endpoint,
        data=json.dumps(data_for_sending),
        headers=request_headers
    )

    bids = json.loads(r.text())

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="linkprofit.xls"'

    # Excel file settings
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('linkprofit')

    # first row to write
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    fields = [
        "id", "contact_phone", "city",
        "name", "credit_sum", "termin",
        "termin_type", "wm_id", "any_param",
        "created_dt", "status"]
    # write column names in row_num row
    for col, field in enumerate(fields):
        ws.write(
            row_num,
            col,
            field,
            font_style
        )

    font_style = xlwt.XFStyle()

    for col, bid in enumerate(bids):
        row_num += 1
        ws.write(
            row_num,
            col,
            bid[fields[col]],
            font_style
        )

    wb.save(response)
    return response


linkprofit_check.short_description = 'Send to check'


def save_as_excel(modeladmin, request, queryset):
    bid_model = queryset.model

    # get verbose name of Model's fields
    fields_verbose_names_list = [
        field.name for field in bid_model._meta.get_fields()
    ]

    # get names of Model's fields
    fields_names_list = [field.name for field in bid_model._meta.get_fields()]

    # response settings
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bids.xls"'

    # Excel file settings
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Broker and Turnes')

    # first row to write
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # write column names in row_num row
    for col_num in range(len(fields_verbose_names_list)):
        ws.write(
            row_num,
            col_num,
            fields_verbose_names_list[col_num],
            font_style
        )

    # set default styles
    font_style = xlwt.XFStyle()

    # get list of queryset values
    rows = queryset.values_list(
        *fields_names_list
    )

    # write all rows
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):

            # formatting datetime objects
            if col_num == 9 or col_num == 10:
                ws.write(
                    row_num,
                    col_num,
                    row[col_num].strftime("%Y-%m-%d %H:%M:%S"),
                    font_style
                )
            # else just write values
            else:
                ws.write(
                    row_num,
                    col_num,
                    row[col_num],
                    font_style
                )

    # save file and return file to browser
    wb.save(response)
    return response


save_as_excel.short_description = 'Save as Excel'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = (
        'contact_phone',
        'city',
        'wm_id',
        'any_param',
        'created_dt',
        'updated_dt'
    )
    list_filter = (
        ('created_dt', DateRangeFilter),
        WmIDListFilter
    )
    actions = [linkprofit_check, save_as_excel]
