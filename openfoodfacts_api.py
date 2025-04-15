import requests

def search_open_food_facts(ingredient):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'search_terms': ingredient,
        'search_simple': 1,
        'action': 'process',
        'json': 1
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('products', [])
    else:
        print(f"Error fetching data for '{ingredient}': {response.status_code}")
        return []
    
if __name__ == "__main__":
    test_results = search_open_food_facts("brown sugar")
    for product in test_results[:5]:
        print(product.get("product_name"), "-", product.get("brands"))
