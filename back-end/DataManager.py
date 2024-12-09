import pandas as pd
import os
import openpyxl  
import xlrd  


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
    required_columns = ['姓名', '基本工资', '岗位工资', '工龄工资', '考核工资', '预发效益', '加班工资', '补发', '应发工资']

    all_data = []
    for file_path in file_paths:
        try:
            # 确保文件路径正确，拼接上传目录
            full_file_path = os.path.join(file_path)
            
            # 检查文件是否存在，避免路径问题
            if not os.path.exists(full_file_path):
                print(f"文件不存在: {full_file_path}")
                continue
            
            # 读取 Excel 文件
            xls = pd.ExcelFile(full_file_path)
            
            # 查找包含“工资发放”关键词的工作表
            selected_sheets = [sheet for sheet in xls.sheet_names if "工资发放" in sheet]
            if not selected_sheets:
                continue  # 如果没有找到符合的工作表，跳过

            # 获取第一个符合条件的工作表
            sheet_name = selected_sheets[0]
            df = pd.read_excel(xls, sheet_name=sheet_name, header=3)

            # 确保所需列在 DataFrame 中
            available_columns = [col for col in df.columns if col in required_columns]
            df = df[available_columns]  # 只保留需要的列

            # 删除姓名为空的行，并过滤掉非中文字符的姓名
            df = df.dropna(subset=['姓名'])
            df = df[df['姓名'].apply(lambda x: isinstance(x, str) and all(u'\u4e00' <= c <= u'\u9fff' for c in x))]

            # 添加空行作为填充
            empty_rows = pd.DataFrame([[''] * len(df.columns)] * 2, columns=df.columns)
            df = pd.concat([df, empty_rows], ignore_index=True, sort=False)

            all_data.append(df)  # 将每个文件的处理结果添加到列表中

        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {e}")
            continue  # 如果处理出错，跳过此文件并继续

    if all_data:
        merged_data = pd.concat(all_data, ignore_index=True)
        return merged_data
    else:
        return None  # 如果没有有效的数据，返回 None

def save_to_excel(dataframe, output_path):
    try:
        dataframe.to_excel(output_path, index=False)
        return True
    except Exception as e:
        print(f"保存文件时发生错误: {e}")
        return False
