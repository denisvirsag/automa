import requests

jsonDefault = {"text":"Men whose spirit has grown arrogant from the great favor of fortune have this most serious fault those whom they have injured they also hate.","author":"Seneca"}

def getQuote():

    url = "https://stoic-quotes.com/api/quote"

    try:
        # Effettua la richiesta GET
        response = requests.get(url)
        
        response.raise_for_status()
        
        try:
            return response.json()
        except ValueError:
            return jsonDefault
            
    except requests.exceptions.RequestException as e:
        return jsonDefault
    