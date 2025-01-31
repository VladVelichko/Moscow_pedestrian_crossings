import geojson
import json
from shapely.geometry import shape, Point


def spotting_the_district(list_of_coord, dist):
    # EN: correlating accidents (list_of_coord) with districts (dist)
    # RU: соотнесение ДТП (list_of_coord) с округами (dist)

    accidents_by_district = {
        'East': [],
        'South-east': [],
        'South': [],
        'South-west': [],
        'West': [],
        'North-west': [],
        'North': [],
        'North-east': [],
        'Centre': [],
        'Garden Ring': []
    }

    for element in list_of_coord:
        # EN: checking each district to see if it contains the point of the accident
        # RU: проверка каждого округа на попадание в него ДТП
        q = element[:-1]
        for feat in dist['features']:
            polygon = shape(feat['geometry'])
            if polygon.contains(Point(q)):
                d = accidents_by_district
                d[feat['properties']['description']] = d.get(feat['properties']['description'], []) + [tuple(element)]

    return accidents_by_district


def counting_crossings(list_of_crossings, area):
    # EN: getting the coordinates of all crossing facilities
    # RU: получение всех координат всех переходов
    with open(area) as fi:
        jsn = geojson.load(fi)
        for feat in jsn['features']:
            list_of_crossings.append(tuple(feat['geometry']['coordinates']))


def counting_matches(acc_list, letter):
    norm_acc = 0
    print('TO PROVE:')
    for elem in acc_list:
        if elem[2] == letter:
            norm_acc += 1
        else:
            print(elem)
    print(f'NORMAL: {norm_acc}')


def near_accident(dict_of_accidents, list_of_at_grades, list_of_underpasses, type_of_accident):
    # EN: checking whether any pedestrian crossing is near the accident
    # RU: проверка на наличие любого пешеходного перехода вблизи ДТП

    only_underpasses = {
        'East': [],
        'South-east': [],
        'South': [],
        'South-west': [],
        'West': [],
        'North-west': [],
        'North': [],
        'North-east': [],
        'Centre': [],
        'Garden Ring': []
    }
    only_at_grades = {
        'East': [],
        'South-east': [],
        'South': [],
        'South-west': [],
        'West': [],
        'North-west': [],
        'North': [],
        'North-east': [],
        'Centre': [],
        'Garden Ring': []
    }
    both = {
        'East': [],
        'South-east': [],
        'South': [],
        'South-west': [],
        'West': [],
        'North-west': [],
        'North': [],
        'North-east': [],
        'Centre': [],
        'Garden Ring': []
    }

    for district in dict_of_accidents:
        for point in dict_of_accidents[district]:

            # EN: creating a 200x200 metres frame around the accident
            # RU: создание рамки 200х200 метров вокруг ДТП

            lon_acc, lat_acc = float("%.6f" % float(point[0])), float("%.6f" % float(point[1]))
            lon1, lon2 = lon_acc + 0.00159, lon_acc - 0.00159
            lat1, lat2 = lat_acc + 0.0009, lat_acc - 0.0009
            poly = shape({"coordinates": [[[lon1, lat1], [lon2, lat1], [lon2, lat2], [lon1, lat2]]], "type": "Polygon"})

            # EN: checking whether any pedestrian crossing is within a 200x200 metres frame around the accident
            # RU: проверка на попадание любого пешеходного перехода в рамку 200х200 метров вокруг ДТП

            proving_underpass = False

            for point2 in list_of_underpasses:
                if poly.contains(Point(point2)) and not proving_underpass:
                    proving_underpass = True
                    proving_both = False
                    match = 'O'

                    if 'Подземный пешеходный переход' in point[2]:
                        match = 'U'

                    for point3 in list_of_at_grades:
                        if poly.contains(Point(point3)) and not proving_both:
                            proving_both = True

                            i = point[2]
                            if 'Нерегулируемый пешеходный переход' in i or 'Регулируемый пешеходный переход' in i:
                                if match == 'U':
                                    match = 'B'
                                else:
                                    match = 'A'

                            d = both
                            d[district] = d.get(district, []) + [(point[1], point[0], match)]

                    if not proving_both:
                        d = only_underpasses
                        d[district] = d.get(district, []) + [(point[1], point[0], match)]

            if not proving_underpass:
                proving_at_grade = False
                match = 'O'

                for point3 in list_of_at_grades:
                    if poly.contains(Point(point3)) and not proving_at_grade:
                        proving_at_grade = True

                        if 'Подземный пешеходный переход' in point[2]:
                            match = 'U'

                        i = point[2]
                        if 'Нерегулируемый пешеходный переход' in i or 'Регулируемый пешеходный переход' in i:
                            if match == 'U':
                                match = 'B'
                            else:
                                match = 'A'

                        d = only_at_grades
                        d[district] = d.get(district, []) + [(point[1], point[0], match)]

    # EN: displaying numbers of accidents by district and severity
    # RU: вывод на экран количества ДТП по районам и тяжести
    print(type_of_accident)
    for district in only_underpasses:
        print(f'District: {district}:')
        # print(f'Number of accidents near underpasses: {len(only_underpasses[district])},')
        # print(f'Number of accidents near at-grade crossings: {len(only_at_grades[district])},')
        # print(f'Number of accidents near both: {len(both[district])}.')

        print()
        print(f'UNDERPASSES: {len(only_underpasses[district])}:')
        counting_matches(only_underpasses[district], 'U')
        print()
        print(f'AT-GRADES: {len(only_at_grades[district])}:')
        counting_matches(only_at_grades[district], 'A')
        print()
        print(f'BOTH: {len(both[district])}:')
        counting_matches(both[district], 'B')
        print()
        print()


def pedestrians_involved(jsonfile, la_list, sa_list, da_list):
    # EN: checking whether a pedestrian was involved in an accident and analysing the severity of it
    # RU: проверка на участие пешехода в ДТП и определение тяжести ДТП с пешеходами

    for feature in jsonfile['features']:
        for participants in feature['properties']['participants']:
            if participants:
                if 'Пешеход' in participants['role']:
                    # EN: if a pedestrian was involved | RU: если в ДТП был вовлечён пешеход
                    q = feature['properties']['datetime']

                    if '2019' in q or '2020' in q or '2021' in q or '2022' in q or '2023' in q:
                        # EN: years 2015-2018, 2024 were not researched | RU: годы 2015-2018, 2024 не исследовались
                        coords = feature['geometry']['coordinates']
                        nearby = feature['properties']['nearby']

                        if feature['properties']['severity'] == 'Легкий' and coords != [None, None]:
                            # EN: if the accident had light consequences | RU: если ДТП было с лёгкими последствиями
                            la_list.append((coords[0], coords[1], nearby))

                        elif feature['properties']['severity'] == 'Тяжёлый' and coords != [None, None]:
                            # EN: if the accident had severe consequences | RU: если ДТП было с тяжёлыми последствиями
                            sa_list.append((coords[0], coords[1], nearby))

                        elif feature['properties']['severity'] == 'С погибшими' and coords != [None, None]:
                            # EN: if the accident was lethal | RU: если ДТП было летальным
                            da_list.append((coords[0], coords[1], nearby))


with open('moskva.geojson', encoding="utf_8_sig") as file:
    js = json.load(file)

light_accidents = []  # EN: list for light accidents | RU: список ДТП с лёгкими последствиями
severe_accidents = []  # EN: list for severe accidents | RU: список ДТП с тяжёлыми последствиями
deadly_accidents = []  # EN: list for deadly accidents | RU: список летальных ДТП

pedestrians_involved(js, light_accidents, severe_accidents, deadly_accidents)

# EN: opening the file with districts of Moscow | RU: открывание файла со всеми округами Москвы
with open('moscow_districts.geojson') as f:
    js = geojson.load(f)
    light_accidents = spotting_the_district(light_accidents, js)
    severe_accidents = spotting_the_district(severe_accidents, js)
    deadly_accidents = spotting_the_district(deadly_accidents, js)

at_grades = []  # EN: the list for coordinates of at-grade crossings | RU: список координат наземных переходов
underpasses = []  # EN: the list for coordinates of underpasses | RU: список координат подземных переходов

counting_crossings(at_grades, 'at-grades.geojson')
counting_crossings(underpasses, 'underpasses.geojson')

near_accident(deadly_accidents, at_grades, underpasses, 'LETHAL ACCIDENTS')
near_accident(severe_accidents, at_grades, underpasses, 'SEVERE ACCIDENTS')
near_accident(light_accidents, at_grades, underpasses, 'LIGHT ACCIDENTS')
