import pandas as pd
import os

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
 


def process_data(file_paths, selected_columns):
    column_buttons = ['姓名', '基本工资', '岗位工资', '工龄工资', '考核工资', '预发效益', '加班工资', '补发', '应发工资',  '医疗保险', '失业保险', '住房公积金', '工会费',  '其他扣除',  '个人所得税',  '实发工资']
    
    # 使用 selected_columns 来获取列名
    required_columns = [column_buttons[i] for i in selected_columns]

    all_data = []
    for file_path in file_paths:
        try:
            # 确保文件路径正确，拼接上传目录
            full_file_path = os.path.join(file_path)
            
            if not os.path.exists(full_file_path):
                print(f"文件不存在: {full_file_path}")
                continue

            with pd.ExcelFile(full_file_path) as xls:
                selected_sheets = [sheet for sheet in xls.sheet_names if "工资发放" in sheet]
                if not selected_sheets:
                    continue  

                sheet_name = selected_sheets[0]
                df = pd.read_excel(xls, sheet_name=sheet_name, header=3)

                available_columns = [col for col in df.columns if col in required_columns]
                df = df[available_columns]  

                df = df.dropna(subset=['姓名'])
                df = df[df['姓名'].apply(lambda x: isinstance(x, str) and all(u'\u4e00' <= c <= u'\u9fff' for c in x))]

                empty_rows = pd.DataFrame([[''] * len(df.columns)] * 2, columns=df.columns)
                df = pd.concat([df, empty_rows], ignore_index=True, sort=False)

                all_data.append(df)  

        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {e}")
            continue  

    if all_data:
        merged_data = pd.concat(all_data, ignore_index=True)
        return merged_data
    else:
        return None  # 如果没有有效的数据，返回 None


def save_to_excel(data, output_path):
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='ProcessedData')
            worksheet = writer.sheets['ProcessedData']
            worksheet.freeze_panes = 'A2'  # 冻结第一行
        return True
    except Exception as e:
        print(f"保存文件时发生错误: {e}")
        return False
