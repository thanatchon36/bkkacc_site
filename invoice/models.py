from django.db import models
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator, MinLengthValidator
import logging
from django.db import transaction
import pandas as pd
import datetime
from dateutil.relativedelta import *
from django.db.models import Avg, Count, Min, Sum

# Create your models here.

logger = logging.getLogger(__name__)

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='สร้างขึ้น')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='แก้ไข')
    class Meta:
        abstract = True

class Company(TimeStampMixin):
    name = models.CharField(max_length=200,verbose_name='ชื่อบริษัท')
    tax_id = models.CharField(max_length=13, validators=[MinLengthValidator(13)],verbose_name='รหัสประจำตัวผู้เสียภาษี')
    email = models.EmailField(verbose_name='อีเมล')
    start_date = models.DateField(verbose_name='วันที่เริ่มติดต่อลูกค้า')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "ข้อมูลบริษัท"
        verbose_name = "ข้อมูลบริษัท"

class Service(TimeStampMixin):
    name = models.CharField(max_length=200,verbose_name='ชื่อบริการ')
    detail = models.TextField(verbose_name='รายละเอียด')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "ข้อมูลบริการ"
        verbose_name = "ข้อมูลบริการ"



class Holiday(TimeStampMixin):
    name = models.CharField(max_length=200,verbose_name='ชื่อวันหยุด')
    date = models.IntegerField(default=1,validators=[MaxValueValidator(31), MinValueValidator(1)],verbose_name='วันที่')
    month = models.IntegerField(default=1,validators=[MaxValueValidator(12), MinValueValidator(1)],verbose_name='เดือนที่')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "ข้อมูลวันหยุด"
        verbose_name = "ข้อมูลวันหยุด"

class Notification(TimeStampMixin):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,verbose_name='ชื่อบริษัท')
    service = models.ForeignKey(Service, on_delete=models.CASCADE,verbose_name='ชื่อบริการ')
    price = models.FloatField(default=0,validators=[MinValueValidator(0)],verbose_name='ค่าบริการ')
    date = models.IntegerField(default=1,validators=[MaxValueValidator(31), MinValueValidator(1)],verbose_name='วันที่เรียกเก็บ')

    class Meta:
        verbose_name_plural = "ข้อมูลการแจ้งเตือน"
        verbose_name = "ข้อมูลการแจ้งเตือน"

    def __str__(self):
        return self.company.name + ' - ' + self.service.name



class Report(TimeStampMixin):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,verbose_name='ชื่อบริษัท')
    start_date = models.DateField(verbose_name='วันเริ่มต้นเรียกเก็บ')
    end_date = models.DateField(verbose_name='วันสิ้นสุนเรียกเก็บ')
    note = models.TextField(blank = True, verbose_name='จดบันทึก')

    def __str__(self):
        return self.company.name + ' - ' + str(self.start_date) + ' - ' + str(self.end_date)

    class Meta:
        verbose_name_plural = "รายงานเรียกเก็บเงิน"
        verbose_name = "รายงานเรียกเก็บเงิน"

    @property
    def sum_price(self):
        return self.reportdetail_set.aggregate(sum_price = Sum('price'))['sum_price']

    def save(self,*args,**kwargs):
        created = not self.pk
        super().save(*args,**kwargs)
        if created:
            print(self.company.name)            
            #(company= self.company)
            print(self.id)
            noti = Notification.objects.filter(company = self.company)
            holi_df = pd.DataFrame(list(Holiday.objects.all().values('name', 'date', 'month')))
            # print(holi_df)

            for each_1 in noti:
                date_range = pd.date_range(self.start_date, self.end_date).tolist()
                date_range = map(lambda x: x.date(), date_range)

                def filter_date(date):
                    max_date = datetime.datetime(date.year, date.month, 1) + relativedelta(months=1) - relativedelta(days=1)
                    max_date = max_date.day
                    noti_date = each_1.date 
                    if  noti_date >= max_date:
                        correct_date = max_date
                    else:
                        correct_date = noti_date

                    if date.day == correct_date:
                        return True
                    else:
                        return False

                date_range = list(filter(filter_date, date_range))
                print(date_range)

                for each_2 in date_range:
                    HOLIDAY_NOTE = []
                    noti_datetime = each_2
                    base_noti_datetime = noti_datetime
                    noti_mon = noti_datetime.month

                    while (noti_datetime.weekday() == 5 or noti_datetime.weekday() == 6) or\
                    len(holi_df[(holi_df['date'] == noti_datetime.day) &\
                    (holi_df['month'] == noti_datetime.month)]) >= 1:

                        if len(holi_df[(holi_df['date'] == noti_datetime.day) &\
                            (holi_df['month'] == noti_datetime.month)]) >= 1:
                            
                            HOLIDAY_NOTE.append(holi_df[(holi_df['date'] == noti_datetime.day) &\
                            (holi_df['month'] == noti_datetime.month)]['name'].tolist()[0])
                        
                        noti_datetime-= relativedelta(days=1)

                    
                    if noti_mon != noti_datetime.month:
                        noti_datetime = base_noti_datetime
                        HOLIDAY_NOTE = []
                        while (noti_datetime.weekday() == 5 or noti_datetime.weekday() == 6) or\
                            len(holi_df[(holi_df['date'] == noti_datetime.day) &\
                            (holi_df['month'] == noti_datetime.month)]) >= 1:

                            if len(holi_df[(holi_df['date'] == noti_datetime.day) &\
                                (holi_df['month'] == noti_datetime.month)]) >= 1:
                                
                                HOLIDAY_NOTE.append(holi_df[(holi_df['date'] == noti_datetime.day) &\
                                (holi_df['month'] == noti_datetime.month)]['name'].tolist()[0])
                        
                            noti_datetime+= relativedelta(days=1)

                    print(noti_datetime)
                    r_detail = ReportDetail(report=self,
                                            service=each_1.service,price=each_1.price,
                                            invoice_date=noti_datetime)
                    r_detail.save()

                    

class ReportDetailStatus(TimeStampMixin):
    name = models.CharField(max_length=200,verbose_name='สถานะเรียกเก็บ')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "สถานะเรียกเก็บเงิน"
        verbose_name = "สถานะเรียกเก็บเงิน"

class ReportDetail(TimeStampMixin):
    report = models.ForeignKey(Report, on_delete=models.CASCADE,verbose_name='รายงาน')
    service = models.ForeignKey(Service, on_delete=models.CASCADE,verbose_name='บริการ')
    price = models.FloatField(default=0,validators=[MinValueValidator(0)],verbose_name='ค่าบริการ')
    invoice_date = models.DateField(verbose_name='วันเรียกเก็บ')
    status = models.ForeignKey(ReportDetailStatus, on_delete=models.CASCADE,\
                                default= 1,\
                                verbose_name='สถานะ')
    note = models.CharField(blank = True, max_length=200,verbose_name='จดบันทึก')
    
    def __str__(self):
        return self.report.company.name + ' - ' + self.service.name + ' - ' + str(self.invoice_date)

    class Meta:
        verbose_name_plural = "รายละเอียดเรียกเก็บเงิน"
        verbose_name = "รายละเอียดเรียกเก็บเงิน"






