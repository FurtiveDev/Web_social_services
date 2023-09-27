from django.shortcuts import render
from django.http import HttpResponse

def services(request):
    return render(request, 'services.html')
def GetData():
    return  [
            {
                'title': 'Консультации и поддержка психолога.',
                'description': 'Предоставление профессиональных консультаций и эмоциональной поддержки социальным работником или психологом.',
                'image':'https://static.sobaka.ru/images/image/01/28/05/68/_normal.jpg?v=1585214887',
                'id': 1
            },
            {
                'title': 'Реабилитационные занятия с физиотерапевтом.',
                'description': 'Проведение специальных физических упражнений и процедур для восстановления и улучшения физического состояния инвалида.',
                'image':'https://физиоздоровье.рф/wp-content/uploads/2020/08/kompleksnaya-reabilitacziya-2.jpg',
                'id': 2
            },
            {
                'title': 'Помощь в получении медицинских средств реабилитации (протезы, ортезы и т.д.).',
                'description': 'Помощь в оформлении и получении медицинских приспособлений, таких как протезы, ортезы и другие средства реабилитации.',
                'image':'https://riamo.ru/files/image/17/42/07/-list!08we.jpg',
                'id': 3
            },
            {
                'title': 'Помощь в освоении навыков самообслуживания (оформление группы инвалидности, получение льгот и документов).',
                'description': 'Помощь в оформлении необходимых документов, получении льгот и развитии навыков самообслуживания для повышения качества жизни инвалида.',
                'image':'https://www.pravmir.ru/wp-content/uploads/2021/10/photo-1534423861386-85a16f5d13fd-936x560.jpeg',
                'id': 4
            },
            {
                'title': 'Помощь в поиске специализированного транспорта и адаптивной техники.',
                'description': 'Помощь в поиске и организации специализированного транспорта и адаптивной техники, чтобы обеспечить инвалиду удобство и мобильность в повседневной жизни.',
                'image':'https://globe4all.net/admin/uploads/post/files/RZD%20Railways/51375.jpg',
                'id': 5
            },
            {
                'title': 'Обучение навыкам использования компьютера и интернета для повышения доступности информации.',
                'description': 'Обучение инвалидов навыкам использования компьютера и интернета для доступа к информации, коммуникации и повышения возможностей в современном информационном обществе.',
                'image':'https://internet-lab.ru/sites/internet-lab.ru/files/styles/shirokiy/public/2019-05/computer.png?itok=CJoYKVhS',
                'id': 6
            },
        ]
services_data = GetData()
def GetServices(request):
    search_query = request.GET.get('search', '')
    result = []
    if search_query is None:
        return render (request, 'services.html', {'data': services_data
    })
    else:
        for service in services_data:
            if search_query.lower() in service['title'].lower():
                result.append(service)
        return render(request, 'services.html', {'data': result, 'search_query':search_query})
def GetService(request, id):
    return render(request, 'service.html', {'data' : services_data[id-1]['description'],'imag': services_data[id-1]['image']
    })