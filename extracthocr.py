# coding: utf8

import re
from bs4 import BeautifulSoup


def margining(coord, w=0, h=0, W=0, H=0):
    coord[0] -= w
    coord[1] -= h
    coord[2] += W
    coord[3] += H
    return coord

def getTitleAttribute(hocr_element, attribute):
    title = hocr_element["title"]
    if attribute is 'bbox' or attribute is 'x_bboxes':
        result = re.findall(r"(bbox|x_bboxes)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", title)[0]
        return [int(r) for r in result[1:]]

    elif attribute is 'image':
        return re.findall(r"image\s+\"([^\"]+)", attribute)  # be careful with the image path syntax in hocr file!

    elif attribute is None:
        return title


def zoning(imgPage, node, margin):
    # get glyph's coords (and parse from xml)
    coordCrop = getTitleAttribute(node, "bbox")

    # margining
    coordCrop = margining(coordCrop, margin, margin, margin, margin)

    # crop the image of in the glyph in the image of the page
    area = imgPage.crop(coordCrop)
    # outputName = char+pageNum+"-"+idNode+".png";
    # area.save(folderOutputPath+char+pageNum+"-"idGlyph+".png")
    return area

def pixels2mm(val,ppp):
    ppmm = float(ppp)/25.4
    mm = float(val)/ppmm
    return mm