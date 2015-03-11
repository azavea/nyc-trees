import cairo


def png_to_pdf(png_file_path, output_file_object, scale_to_dpi=96):
    # Based on http://stackoverflow.com/questions/7099630/create-pdf-with-resized-png-images-using-pycairo-rescaling-surface-issue  # NOQA

    # Paper size in points (1/72 inches)
    paper_width = 612
    paper_height = 792
    margin = 36

    pdf_surface = cairo.PDFSurface(
        output_file_object, paper_width, paper_height)
    cr = cairo.Context(pdf_surface)
    cr.translate(margin, margin)

    cr.save()
    scale = 72.0 / scale_to_dpi
    cr.scale(scale, scale)
    cr.set_source_surface(cairo.ImageSurface.create_from_png(png_file_path))
    cr.paint()
    cr.restore()

    pdf_surface.show_page()
