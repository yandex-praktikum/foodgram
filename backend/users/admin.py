from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """
    Админ-зона пользователя.
    """
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'role', 'avatar')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)
    empty_value_display = '-'


admin.site.register(User, UserAdmin)
