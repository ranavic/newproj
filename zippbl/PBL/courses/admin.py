from django.contrib import admin
from .models import (
    Category, Skill, Course, Module, TextContent, VideoContent, 
    ResourceContent, Assignment, Enrollment, Progress, Review
)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['parent']

class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name']
    list_filter = ['category']

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'price', 'status', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'overview', 'description', 'tags']
    list_filter = ['level', 'category', 'status', 'is_featured', 'certificate_available']
    filter_horizontal = ['skills', 'prerequisites']
    inlines = [ModuleInline]

class TextContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'estimated_reading_time']
    search_fields = ['title', 'content']
    list_filter = ['module__course']

class VideoContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'duration']
    search_fields = ['title', 'description']
    list_filter = ['module__course']

class ResourceContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'file_type', 'file_size']
    search_fields = ['title', 'description']
    list_filter = ['module__course', 'file_type']

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'due_date', 'total_points', 'assignment_type']
    search_fields = ['title', 'instructions']
    list_filter = ['module__course', 'assignment_type']

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date_enrolled', 'status', 'completion_percentage', 'certificate_issued']
    search_fields = ['student__username', 'student__email', 'course__title']
    list_filter = ['status', 'certificate_issued']
    readonly_fields = ['date_enrolled']

class ProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'module', 'content_type', 'completed', 'last_accessed']
    search_fields = ['enrollment__student__username', 'enrollment__course__title']
    list_filter = ['completed', 'content_type']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'rating', 'created_at', 'is_featured']
    search_fields = ['comment', 'student__username', 'course__title']
    list_filter = ['rating', 'is_featured']
    readonly_fields = ['created_at']

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(TextContent, TextContentAdmin)
admin.site.register(VideoContent, VideoContentAdmin)
admin.site.register(ResourceContent, ResourceContentAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Review, ReviewAdmin)
