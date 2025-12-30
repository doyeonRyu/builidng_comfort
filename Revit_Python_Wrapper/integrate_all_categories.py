'''
Category별 element list를 담은 list를 JSON 파일로 저장
'''

import os
import json

file_path = IN[0] # C:\Temp\params.json
elements_lists = IN[1] # 각 category별 element list들의 list

# 폴더가 없으면 생성
folder = os.path.dirname(file_path)
if folder and not os.path.exists(folder):
    os.makedirs(folder)

# JSON으로 저장
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(elements_lists, f, ensure_ascii=False, indent=2)

# 저장 완료 메시지 반환
OUT = "saved: {}".format(file_path)
