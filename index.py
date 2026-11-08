import socket
import ssl
from concurrent.futures import ThreadPoolExecutor

# সচরাচর ব্যবহৃত HTTP/HTTPS ওয়েব পোর্টসমূহ
COMMON_PORTS = [80, 443, 8080, 8443, 8888, 8000, 8081]
OUTPUT_FILE = "active_web_ips.txt"

def test_target(target):
    ip, port = target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.35)
    
    try:
        s.connect((ip, port))
        
        # প্রোটোকল যাচাই (HTTPS নাকি HTTP)
        protocol = "http"
        if port in [443, 8443]:
            protocol = "https"
        else:
            # SSL হ্যান্ডশেক টেস্ট
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with context.wrap_socket(s, server_hostname=ip) as ss:
                    protocol = "https"
            except Exception:
                protocol = "http"
        
        url = f"{protocol}://{ip}:{port}"
        print(f"[+] FOUND: {url}")
        
        with open(OUTPUT_FILE, "a") as f:
            f.write(url + "\n")
            
    except Exception:
        pass
    finally:
        s.close()

def target_generator():
    for sub in range(0, 256):
        for host in range(1, 255):
            ip = f"10.120.{sub}.{host}"
            for port in COMMON_PORTS:
                yield (ip, port)

print("Scanning 10.120.x.x across common HTTP/HTTPS ports...")
print(f"Results will be saved in: {OUTPUT_FILE}")

# থ্রেড সংখ্যা ১৮০ দেওয়া হয়েছে দ্রুত স্ক্যানের সুবিধার্থে
with ThreadPoolExecutor(max_workers=10000) as executor:
    executor.map(test_target, target_generator())

print("\nScan completed! Check active_web_ips.txt")
