from django.contrib import admin
from homepage_stock_list.models import Homepage_stock_list

class Homepage_stock_list_admin(admin.ModelAdmin):
    list_display = ('tradingsymbol','symboltoken')

admin.site.register(Homepage_stock_list, Homepage_stock_list_admin)
