# -*- coding: utf-8 -*-
import sys, os, shutil

# html fetching
from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# pdf generation
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER

import threading

def section_downloader(num,section,text_body,sema,textBodySema):
    print(num)
    (url,titleStr) = section
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")

    # download the novel subsection text body
    sections = []
    textBodySema.acquire(True)
    text_body[num] = soup.find("div",id="novel_honbun",class_="novel_view").text
    text_body[num] = text_body[num].replace('\n','<br/>')
    text_body[num] = text_body[num].replace("　","")
    
    sema.release()
    textBodySema.release()
    exit()

if __name__ == "__main__":
    max_thread = 5
    sema = threading.Semaphore(max_thread)
    textBodySema = threading.Semaphore(1)
    
    url = "http://ncode.syosetu.com/n6332bx/"
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")

    # download the novel section names & urls
    title = soup.find("p",class_="novel_title").text
    
    sections = []
    for subtitle in soup.findAll("dd"):
        sub_tag = subtitle.find("a")
        sub_url = urljoin(url,sub_tag.get("href"))
        sections.append((sub_url,sub_tag.string))

    # download the section text body
    thread_list = []
    text_body = [None]*len(sections)
    for i in range(len(sections)):
        sema.acquire(True)
        th = threading.Thread(target=section_downloader,
                              args=(i,sections[i],text_body,sema,textBodySema))
        thread_list.append(th)
        th.start()
    
    print("waiting")
    for th in thread_list:
        th.join()

    print("PDF generation")

    pdfFile = SimpleDocTemplate(title+".pdf",pagesize=A4,
                        rightMargin=32,leftMargin=32,
                        topMargin=72,bottomMargin=24)

    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    style_sheet = getSampleStyleSheet()
    style_sheet.add(ParagraphStyle(name='MainText',fontName='HeiseiKakuGo-W5',
                               fontSize=12,leading=18))
    style_sheet.add(ParagraphStyle(name='SubTitle',fontName='HeiseiKakuGo-W5',
                               fontSize=24,leading=50,alignment=TA_CENTER))
    style_sheet.add(ParagraphStyle(name='NovelTitle',fontName='HeiseiKakuGo-W5',
                               fontSize=40,leading=-100,alignment=TA_CENTER))
    style_sheet.add(ParagraphStyle(name='IndexText',fontName='HeiseiKakuGo-W5',
                               fontSize=16,leading=24))
    

    Story=[]
    Story.append(Paragraph(title,style_sheet["NovelTitle"]))
    Story.append(PageBreak())

    refTag = []
    Story.append(Paragraph("目次", style_sheet["SubTitle"]))
    for i in range(len(sections)):
        subtitle = str(i+1)+'. '+sections[i][1]
        refTag.append('<a href = page' + str(i) + '.html#0>' + subtitle+ '</a>')
        Story.append(Paragraph(refTag[i], style_sheet["IndexText"]))

    Story.append(PageBreak())

    for i in range(len(sections)):
        subtitle = str(i+1)+'. '+sections[i][1]
        text = text_body[i]
        Story.append(Paragraph('<a name = page' + str(i) + '.html#0></a>'+subtitle
                               , style_sheet["SubTitle"]))
        Story.append(Paragraph(text,style_sheet["MainText"]))
        Story.append(PageBreak())

    pdfFile.build(Story)

    print("done")
