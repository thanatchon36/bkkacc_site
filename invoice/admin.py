from django.contrib import admin
from .models import Company, Service, Notification, Holiday, Report, ReportDetailStatus, ReportDetail
from django.db.models import Avg, Count, Min, Sum
from invoice.models import Service, Company, Report
# from admin_auto_filters.filters import AutocompleteFilter
test = 5

class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 3
    autocomplete_fields = ['service']

class ReportDetailInline(admin.TabularInline):
    model = ReportDetail
    extra = 0
    autocomplete_fields = ['service']

class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'tax_id', 'email','start_date')
    list_display = ('name', 'tax_id', 'email','start_date')
    inlines = [NotificationInline]

class ServiceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'detail')

class NotificationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['company','service']


class HolidayAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'date', 'month','created_at')

class ReportAdmin(admin.ModelAdmin):
    search_fields = ['id','company','start_date','end_date']
    list_display = ['id','company','start_date','end_date','get_sum_price','note','created_at']
    autocomplete_fields = ['company']
    inlines = [ReportDetailInline]
    
    def get_sum_price(self, obj):
        return obj.sum_price
    get_sum_price.short_description = 'ค่าบริการรวม'
    get_sum_price.admin_order_field = 'ค่าบริการรวม'

    # def get_queryset(self, request):
    #     qs = super(ReportAdmin, self).get_queryset(request)
    #     print(qs[0].id)
    #     # print(qs.id)
    #     # return qs.annotate(num_fixture_metas=Count('fixturemeta'))
    #     # qs = qs.objects.get(id=self.id)

    #     # b = Report.objects.get(id=qs[0].id)
    #     # b = b.reportdetail_set.all()
    #     # b.aggregate(sum_price = Sum('price'))
        
    #     qs = qs.reportdetail_set.all()
    #     return qs.aggregate(sum_price = Sum('price'))

    # def num_sum_price(self, obj):
    #   return obj.sum_price


# class FixtureAdmin(admin.ModelAdmin): 
#     list_display = ["id", "title", "date", "num_fixture_metas_count"]

#     def get_queryset(self, request):
#         qs = super(FixtureAdmin, self).get_queryset(request)
#         return qs.annotate(num_fixture_metas=Count('fixturemeta'))

#     def num_fixture_metas_count(self, obj):
#       return obj.num_fixture_metas
#     num_fixture_metas_count.short_description = 'Fixture Count'
#     num_fixture_metas_count.admin_order_field = 'num_fixture_metas'

class ReportDetailAdmin(admin.ModelAdmin):
    autocomplete_fields = ['service']
    list_display = ['id','get_company','service','invoice_date','status','created_at']

    def get_company(self, obj):
        return obj.report.company.name
    get_company.short_description = 'บริษัท'
    get_company.admin_order_field = 'บริษัท'

class ReportDetailStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','created_at')

admin.site.register(Company,CompanyAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(Holiday,HolidayAdmin)
admin.site.register(Report,ReportAdmin)
admin.site.register(ReportDetailStatus,ReportDetailStatusAdmin)
admin.site.register(ReportDetail,ReportDetailAdmin)
# admin.site.register(Notification, NotificationAdmin)
# Register your models here.
