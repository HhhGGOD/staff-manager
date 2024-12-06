import pandas as pd
import os

# 需要的列名
required_columns = ['姓名', '基本工资', '岗位工资', '工龄工资', '考核工资', '预发效益', '加班工资', '补发', '应发工资']

def import_files_from_folder(folder_path):
    file_paths = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.xlsx', '.xls')):
            file_path = os.path.join(folder_path, file_name)
            if file_path not in file_paths:
                file_paths.append(file_path)
    return file_paths


def delete_file(file_paths, selected_files):
    for file in selected_files:
        file_paths.remove(file)
    return file_paths


def process_data(file_paths):
    all_data = []
    for file_path in file_paths:
        try:
            xls = pd.ExcelFile(file_path)
            selected_sheets = [sheet for sheet in xls.sheet_names if "工资发放" in sheet]
            if not selected_sheets:
                continue

            sheet_name = selected_sheets[0]
            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)

            # 选择需要的列
            available_columns = [col for col in df.columns if col in required_columns]
            df = df[available_columns]

            # 删除姓名为空的行，并过滤掉非中文字符的姓名
            df = df.dropna(subset=['姓名'])
            df = df[df['姓名'].apply(lambda x: isinstance(x, str) and all(u'\u4e00' <= c <= u'\u9fff' for c in x))]

            # 添加空行作为填充
            empty_rows = pd.DataFrame([[''] * len(df.columns)] * 2, columns=df.columns)
            df = pd.concat([df, empty_rows], ignore_index=True, sort=False)

            all_data.append(df)

        except Exception as e:
            continue

    if all_data:
        merged_data = pd.concat(all_data, ignore_index=True)
        return merged_data
    else:
        return None


def save_to_excel(data, output_file_path):
    if data is not None:
        data.to_excel(output_file_path, index=False)
        return True
    else:
        return False
