from django.contrib import admin
from .models import User, Message, PasswordManage, Calendar, PasswordGroup, PasswordTag, Inquiry, InquiryCategory

# Register your models here.
admin.site.register(User)
admin.site.register(Message)
admin.site.register(PasswordManage)
admin.site.register(Calendar)
admin.site.register(PasswordTag)
admin.site.register(PasswordGroup)
admin.site.register(Inquiry)
admin.site.register(InquiryCategory)
