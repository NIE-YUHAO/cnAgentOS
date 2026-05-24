from app.models.api_interface import ApiInterfaceModel

apis = ApiInterfaceModel.get_all()
print(f'Total APIs: {len(apis)}')
for i, api in enumerate(apis):
    print(f'{i+1}. {api["name"]} - {api["api_url"]}')