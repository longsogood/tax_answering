from bs4 import BeautifulSoup, Tag
from urllib import request
import json
from pathlib import Path
import os
import requests
import numpy as np
import bs4

def get_content_url(url):
    page = request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser", from_encoding="utf-8")
    return soup

def get_content_panes(soup):
    panes = soup.find_all("div", class_="panes")
    return panes

def get_file(soup):
    """
    get file và tạo metadata cho file khi request url
    """
    prefix_url = "https://www.gdt.gov.vn"
    
    post_path = soup.find("a", class_="linkDown").get_attribute_list(key="href")[0]
    name = post_path.split("?MOD=")[0].split("/")[-1]
    response = requests.get(prefix_url+post_path)

    if response.status_code == 200:
        with open(f"thue_ttcn/{name}", "wb") as f:
            f.write(response.content)
            f.close()
        print("File downloaded successfully")
    else:
        print("Failed to download file")

def get_metadata(soup):
    post_path = soup.find("a", class_="linkDown").get_attribute_list(key="href")[0]
    name = post_path.split("?MOD=")[0].split("/")[-1]
    metadata_keys = ["documentName", "numberSymbol", "issueDate", "effectiveDate", "expirationDate", "signedBy", "replacedDocument", "issuingAuthority",
                     "documentStatus", "attachedFile"]
    table = soup.find("table", id="detail_legal")
    elements = table.find_all("td")
    metadata = {element1: element2.text.strip() for element1, element2 in zip(metadata_keys, elements[1::2])}
    
    with open(f"thue_ttcn/{name}.metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
        f.close()

def check_table(table_tag):
    table_content = " ".join(table_tag.get_text().replace("\n", " ").split())
    return "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" not in table_content or "TỔNG CỤC TRƯỞNG" not in table_content

def get_descendant_texts(tag: bs4.element.Tag):
    """
    Get text and preprocessing đối với những url không có linkDown, hiển thị trực tiếp văn bản
    """
    # print(tag)
    content = ""
    
    # h5_tag = tag.find("h5")
    # contentBody = tag.find("div", id="contentBody")

    # if h5_tag:
    #     content += h5_tag.get_text()
    
    for child in tag.children:
        if isinstance(child, str):
            if len(child.split()) > 0:
                content += (child.string.strip() + "\n")
        elif isinstance(child, Tag):
            if child.name == "table" and check_table(child):
                table_data = get_data_from_table_tag(child)
                formatted_table = convert_table_data_to_markdown_format(table_data)
                content += formatted_table
            if child.name == "p" and child.children:
                for sub_child in child.children:
                    if len(sub_child.text.split()) == 0:
                        continue
                        # print("Check: ", sub_child.text, "end")
                    content += (" ".join(sub_child.text.strip().split()) + "\n")
            elif child.name == "style":
                continue
            else:
                content += (get_descendant_texts(child) + "\n")

    return content

def get_data_from_table_tag(table_tag):
    """
    Lấy dữ liệu từng cell trong table tag
    """
    table_data = []
    for row_id, row in enumerate(table_tag.find_all("tr")):
        row_data = []
        for col_id, data in enumerate(row.find_all("td")):
            if "colspan" in data.attrs.keys():
                merged_cell_num = data.attrs['colspan']
                # if int(merged_cell_num) > max_merged_cell:
                #     max_merged_cell = merged_cell_num
                #     location["row_index"] = row_id
                #     location["column_index"] = col_id
                for i in range(int(merged_cell_num)):
                    row_data.append(" ".join(data.text.replace("\n", "").split()))
            else:
                row_data.append(" ".join(data.text.replace("\n", "").split()))
        table_data.append(row_data)
    return np.array(table_data)

def convert_table_data_to_markdown_format(table_data):
    len_table_data = np.char.str_len(table_data)

    # max len cho từng column
    max_len_table_data = len_table_data.max(axis=0)

    # length lớn nhất của element đã được thêm khoảng trắng cho từng column
    max_spaces = max_len_table_data + 4
    
    content = ""
    count = 1
    
    for row, len in zip(table_data, len_table_data):    
        content += "|"
        for element, len_element, max_len in zip(row, len, max_len_table_data):
            # Khoảng trắng cần thêm vào
            align_space = (max_len-len_element)/2

            if np.round(align_space) == align_space:
                left_space, right_space = int(align_space), int(align_space)
            else:
                left_space, right_space = int(align_space+1), int(align_space)
            
            content += " " * left_space + element + " " * right_space + "|"
        content += "\n"
        
        if count == 1:
            content += "|"
            for max_len in max_len_table_data:
                content += ("-" * max_len) + "|"
            content += "\n"
        
        count += 1
    return content


