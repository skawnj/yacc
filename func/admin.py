from django.contrib import admin

# Register your models here.
from .models import UserBase
from .models import RestrBase
from .models import BldgBase
from .models import UserReview
from .models import NicknameSrcAdj
from .models import NicknameSrcNoun

class RestrBaseAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RestrBase._meta.fields]
admin.site.register(RestrBase, RestrBaseAdmin)

class UserBaseAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserBase._meta.fields]
admin.site.register(UserBase, UserBaseAdmin)

class BldgBaseAdmin(admin.ModelAdmin):
    list_display = [f.name for f in BldgBase._meta.fields]
admin.site.register(BldgBase, BldgBaseAdmin)

class UserReviewAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserReview._meta.fields]
admin.site.register(UserReview, UserReviewAdmin)

class NicknameSrcAdjAdmin(admin.ModelAdmin):
    list_display = [f.name for f in NicknameSrcAdj._meta.fields]
admin.site.register(NicknameSrcAdj, NicknameSrcAdjAdmin)

class NicknameSrcNounAdmin(admin.ModelAdmin):
    list_display = [f.name for f in NicknameSrcNoun._meta.fields]
admin.site.register(NicknameSrcNoun, NicknameSrcNounAdmin)