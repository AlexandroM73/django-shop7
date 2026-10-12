from django.http import HttpResponse

def home(request):
    return HttpResponse("Привет! API доступно по адресу /api/")
