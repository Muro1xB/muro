import socket
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_actual_website_port(url):
    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.netloc
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5900, 8080, 8443]
    
    results = {
        "hostname": hostname,
        "open_ports": [],
        "default_http_port": 80,
        "default_https_port": 443,
        "specified_port": parsed_url.port
    }
    
    def check_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((hostname, port))
                if result == 0:
                    results["open_ports"].append(port)
                    if port == 443:
                        try:
                            context = ssl.create_default_context()
                            with socket.create_connection((hostname, port), timeout=1) as sock:
                                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                                    results["https_verified"] = True
                        except:
                            results["https_verified"] = False
        except:
            pass
    
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_port, port) for port in common_ports]
        for future in as_completed(futures):
            future.result()
    
    if parsed_url.port:
        results["primary_port"] = parsed_url.port
    elif parsed_url.scheme == 'https' and 443 in results["open_ports"]:
        results["primary_port"] = 443
    elif 80 in results["open_ports"]:
        results["primary_port"] = 80
    else:
        if results["open_ports"]:
            results["primary_port"] = results["open_ports"][0]
        else:
            results["primary_port"] = None
    
    return results

if __name__ == "__main__":
    try:
        url = input("link - - > ")
        print(f"Checking  {url}...")
        result = get_actual_website_port(url)
        
        print("\nTest results :")
        print(f"Host Name : {result['hostname']}")
        print(f"The port specified in the link : {result['specified_port'] if result['specified_port'] else 'غير محدد'}")
        print(f"The port specified in the link : {result['primary_port'] if result['primary_port'] else 'غير معروف'}")
        print(f"Open ports : {', '.join(map(str, result['open_ports'])) if result['open_ports'] else 'لم يتم العثور على منافذ مفتوحة'}")
        
        if 443 in result["open_ports"] and "https_verified" in result:
            print(f"sure  HTTPS: {'(y) ' if result['https_verified'] else '(n) '}")
    
    except Exception as e:
        print(f"error: {str(e)}")
