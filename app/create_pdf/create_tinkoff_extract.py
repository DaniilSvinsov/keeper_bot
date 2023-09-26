from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from add_cyrillic_font import faceName
from io import BytesIO
from time import time
from create_number_agreement import random_number_agreement
from user_transactions_data import dict_transaction_data, result_sums_money


def create_page(p: BytesIO, pdf_file: str, output_pdf_file: str) -> None:
    p.seek(0)

    new_pdf = PdfReader(p)
    existing_pdf = PdfReader(open(pdf_file, "rb"))
    output = PdfWriter()

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    output.write(output_pdf_file)


def create_last_page():
    packet1 = BytesIO()
    can_last = canvas.Canvas(packet1, pagesize=letter)
    can_last.setFont("Helvetica", 9)
    can_last.drawString(110.5, 773.5, f'{result_sums_money[0]} RUB')
    can_last.drawString(93, 752.5, f'{result_sums_money[1]} RUB')
    can_last.save()
    create_page(packet1, "tinkoff_last_template.pdf", "tinkoff_last_page.pdf")


def create_tinkoff_add_template():
    packet_add = BytesIO()
    can_add = canvas.Canvas(packet_add, pagesize=letter)
    can_add.setFont("Helvetica", 9)
    return can_add, packet_add


def create_transactions_in_page(cnt: int):
    step_between_payments, step_to_add = 25, 0
    range_len = 27
    first_step = 0
    if not cnt:
        page_template = can_first
        range_len = 16
    else:  # если страница не первая
        page_template, add_packet_1 = create_tinkoff_add_template()
        step_to_add = 280.5
        first_step = 3

    indx = 16 + 27 * (cnt - 1) if cnt > 0 else 0
    transactions = dict_transaction_data['lst_data_money']
    for i in range(indx, range_len + indx):
        step_low = i - indx
        page_template.setFont(faceName + '1251', 9)
        if transactions[i][0][0] == '0':
            page_template.drawString(56, 505 - step_between_payments * step_low + step_to_add, transactions[i][0])
            page_template.drawString(56, 492.5 - step_between_payments * step_low + step_to_add, transactions[i][0])
        else:
            page_template.drawString(55, 505 - step_between_payments * step_low + step_to_add, transactions[i][0])
            page_template.drawString(55, 492.5 - step_between_payments * step_low + step_to_add, transactions[i][0])
        page_template.drawString(165, 500 - step_between_payments * step_low + step_to_add, transactions[i][1])
        page_template.drawString(260, 500 - step_between_payments * step_low + step_to_add, transactions[i][1])
        if len(transactions[i][2]) >= 43:
            page_template.drawString(355, 504 - step_between_payments * step_low + step_to_add, transactions[i][2][:21])
            page_template.drawString(355, 494 - step_between_payments * step_low + step_to_add,
                                     transactions[i][2][21:43] + '...')
        elif len(transactions[i][2]) >= 21:
            page_template.drawString(355, 504 - step_between_payments * step_low + step_to_add, transactions[i][2][:21])
            page_template.drawString(355, 494 - step_between_payments * step_low + step_to_add, transactions[i][2][21:])
        else:
            page_template.drawString(355, 500 - step_between_payments * step_low + step_to_add, transactions[i][2])
        page_template.drawString(500, 500 - step_between_payments * step_low + step_to_add, transactions[i][3])
        if i != indx:  # исправление косяка (первая линия)
            page_template.line(56.5, 489.5 - step_between_payments * step_low + step_to_add + first_step, 539.5,
                               489.5 - step_between_payments * step_low + step_to_add + first_step)

        first_step = 0

        if i == len(transactions) - 1:
            break

    if step_to_add == 280.5:
        page_template.save()
        create_page(add_packet_1, "tinkoff_add_template.pdf", f"tinkoff_{dict_transaction_data['name']}_{cnt}.pdf")


s = time()
packet = BytesIO()

can_first = canvas.Canvas(packet, pagesize=letter)

can_first.setFont(faceName + '1251', 10)
can_first.drawString(55, 690, dict_transaction_data['name'])

can_first.setFont('Helvetica-Bold', 11)
can_first.drawString(245, 554, dict_transaction_data['first_part_period'])
can_first.drawString(325, 554, dict_transaction_data['second_part_period'])

can_first.setFont("Helvetica", 8)  # заменить на OlegSans 9
can_first.drawString(161.5, 619, dict_transaction_data['first_date_registration'])
can_first.drawString(122, 601, dict_transaction_data['number_agreement'])
can_first.drawString(144, 583, dict_transaction_data['personal_account_number'])

can_first.setFont(faceName + '1251', 9)
can_first.drawString(66, 716, random_number_agreement)
can_first.drawString(494.5, 717, dict_transaction_data['first_part_period'])
cnt_pages = (len(dict_transaction_data['lst_data_money']) + 10) // 27 + 1  # 10 получается из (-16 + 27 - 1)
# Проход по транзакциям взятым из бд
for count in range(cnt_pages):
    create_transactions_in_page(
        count)  # и теперь сюда передается количество страниц и они будут создаваться в add_payment

can_first.save()

create_page(packet, "first_tinkoff_template.pdf", "first_tinkoff_page.pdf")

create_last_page()

merger = PdfWriter()
merger.append("first_tinkoff_page.pdf")
for page_number in range(1, cnt_pages):
    merger.append(f"tinkoff_{dict_transaction_data['name']}_{page_number}.pdf")
merger.append("tinkoff_last_page.pdf")
merger.write("result_tinkoff.pdf")
merger.close()

print(time() - s)
