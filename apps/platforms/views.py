from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.platforms.forms import PlatformForm

@role_required(User.ADMIN)
def admin_platforms_view(request):
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_platforms')
    else:
        form = PlatformForm()
    platforms = Platform.objects.all()
    return render(request, 'platforms/admin_platforms.html', {
        'platforms': platforms, 'form': form,
    })

@role_required(User.ADMIN)
@require_POST
def platform_toggle_view(request, pk):
    p = get_object_or_404(Platform, pk=pk)
    p.activa = not p.activa
    p.save()
    return redirect('admin_platforms')

@role_required(User.ADMIN)
@require_POST
def platform_delete_view(request, pk):
    get_object_or_404(Platform, pk=pk).delete()
    return redirect('admin_platforms')
