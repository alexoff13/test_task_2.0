from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


def to_date(input_str: str):
    return [datetime.strptime(i, '%Y-%m-%d').date() for i in input_str]


def autolabel(rects, height_factor=1.01):
    for i, rect in enumerate(rects):
        height = rect.get_height()
        label = f'{int(height):d}'
        ax.text(rect.get_x() + rect.get_width() / 2., height_factor * height,
                f'{label}',
                ha='center', va='bottom')


data = pd.read_csv('files/data.csv')
guide = pd.read_csv('files/Справочник.csv')

data.rename(columns={'Идентификатор филиалы документа': 'Идентификатор филиала'}, inplace=True)
data = data.merge(guide[['Идентификатор филиала', 'Наименование региона филиала']])

del (guide)

receiving_product = data[data['Вид операции документа'] == 'Прием товара'][['Идентификатор товара', 'Дата документа']]
receiving_product.rename(columns={'Дата документа': 'Прием товара'}, inplace=True)
extradition_product = data[data['Вид операции документа'] == 'Выдача товара'][
    ['Идентификатор товара', 'Дата документа']]

extradition_product.rename(columns={'Дата документа': 'Выдача товара'}, inplace=True)
group_by_products = receiving_product.merge(extradition_product)
group_by_products = group_by_products.merge(data[['Идентификатор товара', 'Наименование региона филиала']])

del (data)

group_by_products[['Прием товара', 'Выдача товара']] = group_by_products[['Прием товара', 'Выдача товара']].apply(
    to_date)
group_by_products['Месяц'] = group_by_products['Прием товара'].apply(lambda x: x.month)
group_by_products['Неделя'] = group_by_products['Прием товара'].apply(lambda x: x.isocalendar()[1])
group_by_products['Количество дней'] = (group_by_products['Выдача товара'] - group_by_products['Прием товара']).apply(
    lambda x: x.days)

groups_ = group_by_products[['Месяц', 'Количество дней']].groupby('Месяц')['Количество дней'].mean()

print(groups_)
standard_time_limit = group_by_products["Количество дней"].mean()
print(f'Нормативный срок по всей компании = {standard_time_limit}')
groups_.to_csv('files/months.csv')

group_by_month = group_by_products[['Неделя', 'Наименование региона филиала', 'Количество дней']].groupby(
    ['Неделя', 'Наименование региона филиала'])['Количество дней'].mean().to_csv('files/regions.csv')

del (group_by_month)

# считаем среднее по каждому региону
group_by_week = \
    group_by_products[['Наименование региона филиала', 'Количество дней']].groupby('Наименование региона филиала')[
        'Количество дней'].mean()
# график
index = list(group_by_week.index)

values = group_by_week.to_list()
plt.bar(index, values)
plt.axhline(y=standard_time_limit, color='r', linestyle='-')
ax = plt.gca()
autolabel(ax.patches, height_factor=1.01)
plt.show()
