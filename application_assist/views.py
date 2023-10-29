from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import redirect
from application_assist.models import Services


def GetServices(request):
    result = []
    service_data = Services.objects.filter(status="действует").order_by('service_name')
    search_query = request.GET.get('search_services')
    if not search_query:
        return render (request, 'services.html', {'data': service_data
        })
    else:
        for service in service_data:
            if search_query.lower() in service.service_name.lower():
                result.append(service)
        return render(request, 'services.html', {'data': result, 'search_query':search_query})


def GetService(request, id):
    service = Services.objects.filter(id_service=id)[0]
    return render(request, 'service.html', {'data': service.description, 'imag': service.image, 'location': service.location_service, 'support_hours': service.support_hours})

def delete_service(request, id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE services SET status = 'удален' WHERE id_service = %s", [id])
    return redirect('/')