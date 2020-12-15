from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('serp.urls'), name='serp'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.index_title = _('Administration panel')
