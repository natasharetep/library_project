from django.contrib import admin
from .models import *

admin.site.register(LoginModel)
admin.site.register(BookAdd)
admin.site.register(BookIssue)
admin.site.register(ReturnBook)
admin.site.register(Notification)
admin.site.register(BookRequest)