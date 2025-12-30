"""
==============================================================================
Project: Revit Python Wrapper

File: extract_parameters_from_elements.py
Summary: category 내 element들의 parameter 값을 JSON 형태로 변환
Author: 유도연
Created Date: 2025-12-30
Last Modified: 2025-12-30

==============================================================================
Description
    1. 특정 category의 element list를 입력값으로 받음
    2. elements의 parameter 값들을 json이 이해할 수 있는 형태로 변환
    3. elements가 단일 element로 들어오는 경우를 대비해 list화
    4. 각 elements의 Revit API Parameter를 순회하여 dict 생성
    5. list of list 형태로 반환
    
==============================================================================
Inputs, Outputs
    Inputs:
        IN[0]: elements (list)
            - category 내 element들의 list
    Outputs:
        OUT: result (list)
            - [element ID, parameter 값들]의 list 형태로 변환된 값들의 list

==============================================================================
Functions
    
==============================================================================
Note:
    - 각 category별로 합쳐서 계층 구조 전체의 parameter 값을 JSON 형태로 저장할 예정
    - BOT 온톨로지를 통해 기본적인 계층 구조 형성에 사용할 예정

==============================================================================
"""
import os
import json

# 1. 특정 category의 element list를 입력값으로 받음
file_path = IN[0] # 저장할 JSON 파일 경로
categories = IN[1] # category 내 elements들의 list

result = [] # list shape: [elements ID, parameter dictionary]

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

for category in categories:
    elements = category

    # 3. elements가 단일 Element로 들어오는 경우를 대비해 리스트화
    if not isinstance(elements, list):
        elements = [elements]
        
    # 4. 각 element의 Revit API Parameter를 순회하여 dictionary 생성
    for el in elements: # 각 element 순회
        # Revit Element 객체 가져오기 
        try:
            revit_elem = el.InternalElement
        except:
            revit_elem = el
        
        # element ID 추출하기
        try:
            el_id = revit_elem.Id.IntegerValue
        except:
            el_id = revit_elem.Id.Value
            
        params = {} # dictionary shape: parameter name: value

        # revit_elem.Parameters를 통해 element의 모든 parameter 순회
        for param in revit_elem.Parameters:
            # parameter 이름 추출
            try:
                name = param.Definition.Name
            except:
                continue # 스킵
            
            # parameter 값 변환
            value = convert_params(param)
            
            params[name] = value
            
        result.append([el_id, params])

# 폴더가 없으면 생성
folder = os.path.dirname(file_path)
if folder and not os.path.exists(folder):
    os.makedirs(folder)

# JSON으로 저장
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 5. list of list 형태로 반환
OUT = result