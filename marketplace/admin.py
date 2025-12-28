from django.contrib import admin
from .models import User, Job, Proposal, FreelancerProfile, Skill, Feedback

admin.site.register(User)
admin.site.register(Job)
admin.site.register(Proposal)
admin.site.register(FreelancerProfile)
admin.site.register(Skill)


# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "category", "created_at")
    list_filter = ("category", "rating", "created_at")
    search_fields = ("user__username", "message")

