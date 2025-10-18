

def insert_https_protocol(link: str):

    if link.startswith('https'):
        return link
    
    return 'https://' + link.split('://', 1)[1]