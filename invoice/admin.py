from django.contrib import admin
from .models import Company, Service, Notification, Holiday, Report, ReportDetailStatus, ReportDetail
from django.db.models import Avg, Count, Min, Sum
from invoice.models import Service, Company, Report
from django.forms import DateField, CharField, ChoiceField, TextInput
from django.db.models import Q
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from advanced_filters.admin import AdminAdvancedFiltersMixin

admin.site.site_header = "BKK ACC Admin"
admin.site.site_title = "BKK ACC Admin Portal"
admin.site.index_title = "Welcome to BKK ACC Portal"

class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 3
    autocomplete_fields = ['service']

class ReportDetailInline(admin.TabularInline):
    model = ReportDetail
    extra = 0
    autocomplete_fields = ['service']

    
# class UIDFilter(InputFilter):
#     parameter_name = 'name'
#     title = ('ชื่อบริษัท')
 
#     def queryset(self, request, queryset):
#         if self.value() is not None:
#             uid = self.value()
#             return queryset.filter(
#                 Q(name=uid)
#             )

# class TAXFilter(InputFilter):
#     parameter_name = 'tax_id'
#     title = ('เลข')
 
#     def queryset(self, request, queryset):
#         if self.value() is not None:
#             uid = self.value()
#             return queryset.filter(
#                 Q(tax_id=uid)
#             )

# class CompanyAdmin(admin.ModelAdmin):
class CompanyAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    search_fields = ('name', 'tax_id', 'email')
    list_display = ('name', 'tax_id', 'email','start_date')
    inlines = [NotificationInline]
    list_filter = (
        'start_date',
        ('start_date', DateRangeFilter),
    )

    advanced_filter_fields = (
        'name',
        'tax_id',
        'email',
        'start_date',
        # # even use related fields as lookup fields
        # 'country__name',
        # 'posts__title',
        # 'comments__content',
    )
    
    # readonly_fields=('get_id',)

    # fieldsets = [
    #     (None,               {'fields': ['get_id','name','tax_id','email','start_date']}),
    # ]

    # def get_id(self, obj):
    #     return obj.id
    # get_id.short_description = 'เลขที่บริษัท'

    # fieldsets = [
    #     (None,               {'fields': ['question_text']}),
    #     ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    # ]

class ServiceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'detail')


class NotificationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['company','service']


class HolidayAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'date', 'month','created_at')

class ReportAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    search_fields = ['id','company__name']
    list_display = ('id','company','notpaid_sum','price_sum','start_date','end_date','first_invoice')

    autocomplete_fields = ['company']
    inlines = [ReportDetailInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _price_sum = Sum("reportdetail__price"),
            _notpaid_sum = Sum("reportdetail__price",filter=Q(reportdetail__status=1)),
            _first_invoice = Min("reportdetail__invoice_date",filter=Q(reportdetail__status=1)),
        )
        return queryset
    def price_sum(self, obj):
        return obj._price_sum
    price_sum.admin_order_field = '_price_sum'
    price_sum.short_description = 'ค่าบริการรวม'
    def notpaid_sum(self, obj):
        return obj._notpaid_sum
    notpaid_sum.admin_order_field = '_notpaid_sum'
    notpaid_sum.short_description = 'ยังไม่จ่าย'

    def first_invoice(self, obj):
        return obj._first_invoice
    first_invoice.admin_order_field = '_first_invoice'
    first_invoice.short_description = 'วันค้างชำระล่าสุด'

    list_filter = [ 'company',
                    'start_date',
                    # 'first_invoice',
                    # '_first_invoice',
                    # ('_first_invoice', DateRangeFilter),
                    ('start_date', DateRangeFilter),
                    ('end_date', DateRangeFilter),
                ]

    advanced_filter_fields = (
        'company',
        'start_date',
        'end_date',
        # '_price_sum',
        # 'notpaid_sum',
        # 'first_invoice',
        # # even use related fields as lookup fields
        # 'country__name',
        # 'posts__title',
        # 'comments__content',
    )


    # readonly_fields=('get_id',)
    # def get_id(self, obj):
    #     return obj.id
    # get_id.short_description = 'เลขที่รายงาน'
    # get_id.admin_order_field = 'id'

    # list_filter = [ 'created_at',
    #                 'end_date',
    #                 ('start_date', DateRangeFilter),
    #                 ('end_date', DateRangeFilter),
    #             ]
    


def make_printed(modeladmin, request, queryset):
    queryset.update(status=2)
make_printed.short_description = "สั่งพิมพ์ทั้งหมด"

def make_not_printed(modeladmin, request, queryset):
    queryset.update(status=1)
make_not_printed.short_description = "ไม่พิมพ์ทั้งหมด"


class ReportDetailAdmin(admin.ModelAdmin):
    search_fields = ['report__company__name','report__id','service__name','report__company__tax_id']
    # search_fields = ['service__name']
    autocomplete_fields = ['service']
    list_display = ['get_report_id','company','service','price','invoice_date','status','is_activated','created_at']
    actions = [make_printed,make_not_printed]

    list_filter = [ 'status',
                    'service',
                    'invoice_date',
                    # ('invoice_date', DateTimeRangeFilter),
                    ('invoice_date', DateRangeFilter),
                ]

    date_hierarchy = 'invoice_date'

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def company(self, obj):
        return obj.report.company
    company.short_description = 'บริษัท'

    def get_report_id(self, obj):
        return obj.report.id
    get_report_id.short_description = 'เลขที่รายงาน'
    
    def is_activated(self, obj):
        if obj.status.id == 1:
            return False
        return True
    is_activated.boolean = True
    is_activated.short_description = "สถานะ"

class ReportDetailStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','created_at')

admin.site.register(Company,CompanyAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(Holiday,HolidayAdmin)
admin.site.register(Report,ReportAdmin)
admin.site.register(ReportDetail,ReportDetailAdmin)
# admin.site.register(ReportDetailStatus,ReportDetailStatusAdmin)
# admin.site.register(Notification, NotificationAdmin)
# Register your models here.
