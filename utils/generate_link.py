import requests
import time

def get_epoch_plus_20min():
    current = int(time.time() * 1000)
    future = current + (20 * 60 * 1000)
    return future

def generate_link(file):
    url = "https://0x0.st"
    files = { 'file': open(file, 'rb'), 'expires': get_epoch_plus_20min() }
    response = requests.post(url, files=files)
    return response.text.strip()  
