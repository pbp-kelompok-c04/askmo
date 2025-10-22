"""
askmo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    # URL default untuk panel admin bawaan Django (tidak kita gunakan, tapi baik untuk ada)
    path('admin/', admin.site.urls),

    # INI BAGIAN PALING PENTING:
    # Semua URL yang dimulai dengan 'coach/' akan diteruskan ke file 'coach/urls.py'
    path('coach/', include('coach.urls', namespace='coach')),

    # Anda bisa menambahkan URL untuk aplikasi lain di sini di masa depan
    # Contoh: path('lapangan/', include('lapangan.urls', namespace='lapangan')),
    # Contoh: path('event/', include('event.urls', namespace='event')),
    path('', include('main.urls')),
]

# Konfigurasi ini PENTING untuk menampilkan gambar yang di-upload (seperti foto coach)
# saat mode DEBUG (pengembangan) aktif.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)