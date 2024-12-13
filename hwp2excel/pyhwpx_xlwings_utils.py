from pyhwpx import Hwp
import xlwings as xw
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import numpy as np
import re


def extract_table_as_xml(_hwp: Hwp):
    
    n = ""
    if _hwp.SelectionMode != 19:
        start_pos = _hwp.hwp.GetPos()
        ctrl = _hwp.hwp.HeadCtrl
        if isinstance(n, type(ctrl)):
            # 정수인덱스 대신 ctrl 객체를 넣은 경우
            _hwp.set_pos_by_set(n.GetAnchorPos(0))
            _hwp.find_ctrl()
        elif n == "" and _hwp.is_cell():
            _hwp.TableCellBlock()
            _hwp.TableColBegin()
            _hwp.TableColPageUp()
        elif n == "" or isinstance(n, int):
            if n == "":
                n = 0
            if n >= 0:
                idx = 0
            else:
                idx = -1
                ctrl = _hwp.hwp.LastCtrl

            while ctrl:
                if ctrl.UserDesc == "표":
                    if n in (0, -1):
                        _hwp.set_pos_by_set(ctrl.GetAnchorPos(0))
                        _hwp.hwp.FindCtrl()
                        break
                    else:
                        if idx == n:
                            _hwp.set_pos_by_set(ctrl.GetAnchorPos(0))
                            _hwp.hwp.FindCtrl()
                            break
                        if n >= 0:
                            idx += 1
                        else:
                            idx -= 1
                if n >= 0:
                    ctrl = ctrl.Next
                else:
                    ctrl = ctrl.Prev

            try:
                _hwp.hwp.SetPosBySet(ctrl.GetAnchorPos(0))
            except AttributeError:
                raise IndexError(f"해당 인덱스의 표가 존재하지 않습니다."
                                    f"현재 문서에는 표가 {abs(int(idx + 0.1))}개 존재합니다.")
            _hwp.hwp.FindCtrl()
    else:
        selected_range = _hwp.get_selected_range()
    
    xml_data = _hwp.GetTextFile("HWPML2X", option="saveblock")
    
    return xml_data

def extract_table_contents(_xml_string: str): 
    table_xml_str = ""
    
    table_start = re.search('''<TABLE''', _xml_string).span()[0]
    table_end = re.search('''</TABLE>''', _xml_string).span()[1]
    
    return _xml_string[table_start:table_end], (table_start, table_end)

def extract_cell_attributes(_xml_string):
    root = ET.fromstring(_xml_string)
    
    borderfill = root.findall('.//BORDERFILLLIST/BORDERFILL')
    charshape = root.findall('.//CHARSHAPELIST/CHARSHAPE')
    
    return borderfill, charshape

def colorstr_to_rgb(color_str: str):
    val_color = int(color_str)
    
    r = val_color & 0xff
    g = (val_color >> 8) & 0xff
    b = (val_color >> 16) & 0xff   
    
    return r, g, b

def get_table_spec(_xml_string:str):
    soup = BeautifulSoup(_xml_string, 'xml')
    
    cells = soup.find_all('CELL')

    cell_rows = np.array([int(cell.attrs['RowAddr']) for cell in cells], dtype=int).max() + 1
    cell_cols = np.array([int(cell.attrs['ColAddr']) for cell in cells], dtype=int).max() + 1

    table_id = np.zeros((cell_rows, cell_cols))
    table_type = np.char.chararray((cell_rows, cell_cols))
    
    return table_id, table_type


# table_id, table_type, cell, data columns를 반환함
# table_id: 전체 테이블 범위 내에서 실제로 값이 있는 셀은 1 나머지는 0
# table_type: 해당 셀에 있는 값이 문자열이면 b's', 정수면 b'i', 소수면 b'f'
# data_columns: 전체 테이블 범위 내에서 인덱스가 아닌 값이 있어야 하는 열의 인덱스
def get_table_contents(_xml_string:str):
    table_id, table_type = get_table_spec(_xml_string)
    cell_rows, _ = table_id.shape
    
    table_root = ET.fromstring(_xml_string)

    cell_dict = {}

    for row in table_root.findall('.//ROW'):
        for cell in row.findall('.//CELL'):
            
            cell_row_addr = int(cell.get('RowAddr'))
            cell_col_addr = int(cell.get('ColAddr'))
            
            dict_key = make_key(cell_row_addr, cell_col_addr)
            
            table_id[cell_row_addr, cell_col_addr] = 1
            table_type[cell_row_addr, cell_col_addr] = check_string_type(get_cell_text(cell))
            cell_dict[dict_key] = cell

    table_cols = np.sum(table_id, axis=0)
    data_cols = np.where(table_cols >= cell_rows-1)[0]
    
    return table_id, table_type, cell_dict, data_cols


def get_cell_text(_cell, remove_blank=False):
    cell_text = ''
    
    for text in _cell.findall('.//TEXT'):
        for char in text.findall('.//CHAR'):
            if char.text is not None:
                cell_text += char.text
        cell_text += "\r\n"
    if cell_text.endswith("\r\n"):
        cell_text = cell_text[:-2]
    
    if remove_blank:
        cell_text = re.sub(' +', ' ', cell_text)
    return cell_text

def check_string_type(s):
    # 공백을 제거한 후 확인
    s = s.strip()
    s = s.replace(',', '')

    # 자연수인지 확인 (0보다 큰 양의 정수)
    if s.isdigit():
        return 'i'

    # 정수인지 확인 (음수 포함)
    try:
        float(s)  # 정수로 변환 시도
        return 'f'
    except ValueError:
        return 's'
    
def make_key(row_id, col_id):
    return f'''{row_id}, {col_id}'''


def write_to_excel(file_name:str, xml_data):
    table_id, table_type, cell_dict, data_cols = get_table_contents(xml_data)
    borderfill, charshape = extract_cell_attributes(xml_data)
    
    try:
        wb = xw.Book(file_name)
    except:
        wb = xw.Book()
        
    sht1 = wb.sheets[0]
    
    cell_rows, cell_cols = table_id.shape
    
    for ii in range(cell_rows):
        for jj in range(cell_cols):
            sht1.range((ii+1, jj+1)).api.Borders.Weight = 2
            
            if table_id[ii,jj] == 1:    
                
                dict_key = make_key(ii, jj)
                
                cell = cell_dict[dict_key]
                
                value_str = get_cell_text(cell)

                if table_type[ii, jj] == b'i':
                    value = int(value_str.replace(',', ''))
                    sht1.range((ii+1, jj+1)).number_format = "#,##0"
                    sht1.range((ii+1, jj+1)).options(numbers=int).value = value
                    
                elif table_type[ii, jj] == b'f':            
                    value = float(value_str.replace(',', ''))
                    sht1.range((ii+1, jj+1)).number_format = '0.000'
                    sht1.range((ii+1, jj+1)).options(numbers=float).value = value
                else:
                    value = value_str
                    sht1.range((ii+1, jj+1)).value = value
                
                font_color = charshape[int(cell.find('.//TEXT').get('CharShape'))]
                sht1.range((ii+1, jj+1)).font.color = colorstr_to_rgb(font_color.get('TextColor'))

                border_color = borderfill[int(cell.get('BorderFill')) - 1]
                face_color = border_color.find('./FILLBRUSH/WINDOWBRUSH')
                
                if face_color is not None:
                    sht1.range((ii+1, jj+1)).color = colorstr_to_rgb(face_color.get('FaceColor'))
                else:
                    sht1.range((ii+1, jj+1)).color = (255, 255, 255)
            else:
                if face_color is not None:
                    sht1.range((ii+1, jj+1)).color = colorstr_to_rgb(face_color.get('FaceColor'))
                else:
                    sht1.range((ii+1, jj+1)).color = (255, 255, 255)
    
    wb.save(file_name)
    
    
    
def update_excel_to_xml_string(file_name, xml_data):
    wb = xw.Book(file_name)
    sht1 = wb.sheets[0]
    
    table_xml_data, (table_start, table_end) = extract_table_contents(xml_data)
    table_id, table_type, cell_dict, data_cols = get_table_contents(xml_data)
    
    table_root = ET.fromstring(table_xml_data)
    for row in table_root.findall('.//ROW'):
        for cell in row.findall('.//CELL'):
        
            cell_row_addr = int(cell.get('RowAddr'))
            cell_col_addr = int(cell.get('ColAddr'))
            
            cell_text = ''
            for text in cell.findall('.//TEXT'):
                for ii, char in enumerate(text.findall('.//CHAR')):
                    if table_id[cell_row_addr, cell_col_addr] == 1 and cell_col_addr in data_cols:
                    
                        value = sht1.range(cell_row_addr+1, cell_col_addr+1).value
                        
                        if table_type[cell_row_addr, cell_col_addr] == b'i':
                            value_str = f'''{int(value):,}'''
                            
                        elif table_type[cell_row_addr, cell_col_addr] == b'f':     
                            value_str =f'''{value:.3f}'''
                            
                        else:
                            value_str = str(value)
                        
                        
                        if ii == 0:
                            char.text = value_str
                        else:
                            char.text = ""
    
    new_xml_data = xml_data[:table_start] + str(ET.tostring(table_root), encoding='utf8')+ xml_data[table_end:]
                            
    return new_xml_data