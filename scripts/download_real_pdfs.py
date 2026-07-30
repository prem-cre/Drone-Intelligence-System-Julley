import os
import urllib.request
import ssl

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_PDF_DIR = os.path.join(DATA_DIR, "data", "real_pdfs")
os.makedirs(REAL_PDF_DIR, exist_ok=True)

# List of official real government / public drone PDF sources
PDF_SOURCES = [
    {
        "filename": "India_Drone_Rules_2021_Gazette.pdf",
        "urls": [
            "https://egazette.gov.in/WriteReadData/2021/229221.pdf",
            "https://raw.githubusercontent.com/drone-intelligence/assets/main/India_Drone_Rules_2021_Gazette.pdf",
            "https://www.dgca.gov.in/digigov-portal/jsp/dgca/homePage/viewPDF.jsp?path=drone_rules_2021.pdf"
        ]
    },
    {
        "filename": "Ministry_Civil_Aviation_Drone_Rules_Summary.pdf",
        "urls": [
            "https://static.pib.gov.in/WriteReadData/specificdocs/documents/2021/aug/doc202182501.pdf",
            "https://pib.gov.in/PressReleasePage.aspx?PRID=1748804"
        ]
    },
    {
        "filename": "ICAR_Agricultural_Drone_Spraying_SOP.pdf",
        "urls": [
            "https://icar.org.in/sites/default/files/SOP-Drone-Spraying.pdf",
            "https://agricoop.gov.in/sites/default/files/SOP_Drone_Agriculture.pdf"
        ]
    },
    {
        "filename": "Namo_Drone_Didi_Scheme_Guidelines_2024.pdf",
        "urls": [
            "https://agricoop.nic.in/sites/default/files/Drone_Guidelines_2022.pdf"
        ]
    }
]

def download_file(urls, dest_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for url in urls:
        try:
            print(f"Attempting download from: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=12) as response, open(dest_path, 'wb') as out_file:
                content = response.read()
                if len(content) > 1000:  # Check valid PDF size
                    out_file.write(content)
                    print(f"SUCCESS: Saved {len(content)} bytes -> {dest_path}")
                    return True
        except Exception as e:
            print(f"Notice: Failed to fetch from {url} ({e})")
    return False

def main():
    print("Starting download of official real Indian drone PDFs from web sources...")
    downloaded_count = 0
    for item in PDF_SOURCES:
        dest = os.path.join(REAL_PDF_DIR, item["filename"])
        success = download_file(item["urls"], dest)
        if success:
            downloaded_count += 1
            
    print(f"\nDownload summary: {downloaded_count}/{len(PDF_SOURCES)} real PDFs saved in '{REAL_PDF_DIR}'.")

if __name__ == "__main__":
    main()
