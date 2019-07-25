from django.shortcuts import render

from WineApp.models import Wine


def index(request):
    wine = Wine.objects.get(pk=2)
    history = list(wine.weatherhistory_set.all()[:10])
    history.append("...")
    history += list(wine.weatherhistory_set.all().order_by('-pk')[:10])[::-1]
    return render(request, 'WineApp/index.html', {'list': history})
