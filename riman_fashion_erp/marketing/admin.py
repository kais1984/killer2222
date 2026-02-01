from django.contrib import admin
from .models import *

# Simple registration of all marketing models
admin.site.register(EmailCampaign)
admin.site.register(SMSCampaign)
admin.site.register(CustomerSegment)
admin.site.register(SegmentMember)
admin.site.register(LoyaltyProgram)
admin.site.register(LoyaltyMember)
admin.site.register(LoyaltyTransaction)
admin.site.register(RedemptionReward)
