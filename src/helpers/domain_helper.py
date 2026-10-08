from urllib.parse import urlparse

def find_domain(url):
    domain = urlparse(url).netloc.split('.')
    if len(domain) == 2:
        return domain[0]
    elif len(domain) == 3:
        if 'iqvia' in domain:
            return 'CedarGate'
        return domain[1]
    elif 'oraclecloud' in domain:
        return 'Verisk'