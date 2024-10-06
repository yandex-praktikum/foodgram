"""Вспомогательные процедуры.

backend/recipes/utils.py
"""

import os
from io import BytesIO

from django.conf import settings
from django.http import FileResponse

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_shopping_cart_file(ingredients, username):
    path_to_fonts = os.path.join(
        settings.STATIC_ROOT, 'fonts/FreeSans.ttf'
    )
    buffer = BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdfmetrics.registerFont(
        TTFont(
            'FreeSans',
            path_to_fonts,
        )
    )
    pdf_file.setFont('FreeSans', 15)
    pdf_file.drawString(100, 750, 'Список покупок для рецептов:')

    y = 700
    counter = 0
    for ingredient in ingredients:
        counter += 1
        pdf_file.drawString(
            100,
            y,
            f'{counter}) '
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["amount_of_ingredients"]} '
            f'{ingredient["ingredient__measurement_unit"]}',
        )
        y -= 20

    pdf_file.showPage()
    pdf_file.save()
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'{username}_shopping_cart_recipe.pdf'
    )
