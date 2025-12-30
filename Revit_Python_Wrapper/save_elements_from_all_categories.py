"""
==============================================================================
Project: 

Folder: Revit Python Wrapper
File: save_elements_from_all_categories.py
Summary: category 별 element들의 parameter 값을 JSON 형태로 변환
Author: 유도연
Created Date: 2025-12-30
Last Modified: 2025-12-30

==============================================================================
Description
    1. Input 값 받기
    2. elements의 parameter 값들을 json이 이해할 수 있는 형태로 변환
    3. category key 목록 정리
    4. elements가 단일 Element로 들어오는 경우를 대비해 리스트화
    5. 각 element의 Revit API Parameter를 순회하여 dictionary 생성
    6. list of list 형태로 저장 및 반환
    
==============================================================================
Inputs, Outputs
    Inputs:
        IN[0]: file_path (str)
            - dict 형태로 저장할 JSON 파일 경로
        IN[1]: category_names (list)
            - category 이름 list (저장에 사용할 key)
        IN[2]: categories_elements (list)
            - category별 elements들의 list of list
        
    Outputs:
        result (list)
            - [Category_name, [ [ElementID, {param_name: param_value, ...}], ... ] ] 형태의 list
            - 각 category별로 합쳐서 계층 구조 전체의 parameter 값을 JSON 형태로 저장

==============================================================================
Functions
    --------------------------------------------------------------------------
    Function: convert_parameters
        - Revit Parameter 값을 JSON에 들어갈 수 있는 기본형으로 변환하는 함수
        - 객체 형태 -> 기본형 (str, int, float, None)으로 변환
    Parameters:
        p: Revit Parameter 객체
    Returns:
        - JSON 가능 형태의 값
    --------------------------------------------------------------------------

==============================================================================
Note:
    - 각 category별로 합쳐서 계층 구조 전체의 parameter 값을 JSON 형태로 저장할 예정
    - BOT 온톨로지를 통해 기본적인 계층 구조 형성에 사용할 예정

==============================================================================
"""
import os
import json

# 1. Input 값 받기
file_path = IN[0] # dict 형태로 저장할 JSON 파일 경로
category_names = IN[1] # category 이름 list (저장에 사용할 key)
categories_elements = IN[2] # category별 elements들의 list of list

# 2. elements의 parameter 값들을 json이 이해할 수 있는 형태로 변환
def convert_params(p):
    """
    Function: convert_parameters
        - Revit Parameter 값을 JSON에 들어갈 수 있는 기본형으로 변환하는 함수
        - 객체 형태 -> 기본형 (str, int, float, None)으로 변환
    Parameters:
        p: Revit Parameter 객체
    Returns:
        - JSON 가능 형태의 값
    """
    
    # 이미 기본형이면 그대로 반환
    if isinstance(p, (str, int, float)) or p is None:
        return p
    
    try: # 1) AsValueString 시도 (단위 포함 문자열)
        v = p.AsValueString()
        if v:
            return v
    except:
        pass
    try: # 2) AsString 시도 (텍스트 파라미터)
        v = p.AsString()
        if v:
            return v
    except:
        pass
    try: # 3) AsInteger 시도 (정수형)
        return int(p.AsInteger())
    except:
        pass
    try: # 4) AsDouble 시도 (실수형 - 내부 단위일 수 있음)
        return float(p.AsDouble())
    except:
        pass

    return None # 변환 불가 시 None 반환

# 3. category key 목록 정리
if isinstance(category_names, list):
    keys = [str(x) for x in category_names]
else:
    keys = ["Category_{}".format(i) for i in range(len(categories_elements))] # key가 없을 경우 Category_0, Category_1, ... 형태로 지정

result = {} # 최종 결과 저장할 dict

for key, elements in zip(keys, categories_elements):
    # 4. elements가 단일 Element로 들어오는 경우를 대비해 리스트화
    if not isinstance(elements, list):
        elements = [elements]

    cat_result = [] # 해당 category의 결과 저장할 list

    # 5. 각 element의 Revit API Parameter를 순회하여 dictionary 생성
    for el in elements: # 각 element 순회
        # Revit Element 객체 가져오기
        try:
            revit_elem = el.InternalElement
        except:
            revit_elem = el

        # Element ID 추출
        try:
            el_id = revit_elem.Id.IntegerValue
        except:
            el_id = revit_elem.Id.Value

        params = {} # dictionary shape: parameter name: value

        # revit_elem.Parameters를 통해 element의 모든 parameter 순회
        try:
            for param in revit_elem.Parameters:
                # parameter 이름 추출
                try:
                    name = param.Definition.Name
                except:
                    continue

                # parameter 값 변환
                value = convert_params(param)
                params[name] = value

        except:
            pass

        cat_result.append([el_id, params])

    result[key] = cat_result

# 폴더 없으면 생성
folder = os.path.dirname(file_path)
if folder and not os.path.exists(folder):
    os.makedirs(folder)

# 6. list of list 형태로 저장 및 반환
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    
OUT = result