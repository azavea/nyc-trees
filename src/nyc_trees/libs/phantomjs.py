import subprocess


def url_to_pdf(url, zoom_factor=0.75):
    # The default zoom was chosen so that labels on map tiles
    # will be a readable size when printed.
    pdf_bytes = subprocess.check_output(
        ['phantomjs', 'js/backend/url2pdf.js', url, str(zoom_factor)])
    return pdf_bytes
