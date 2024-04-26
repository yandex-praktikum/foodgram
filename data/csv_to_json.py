import csv
import json


def csv_to_json(csv_file, json_file):
    with open(csv_file, encoding='utf-8') as csvf:
        column_names = ['name', 'measurement_unit']
        csvReader = csv.DictReader(csvf, fieldnames=column_names)

        with open(json_file, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(list(csvReader), ensure_ascii=False))


if __name__ == '__main__':
    csv_to_json('data/ingredients.csv', 'data/ingredients.json')
