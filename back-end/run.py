from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import SqliteUtil as DBUtil
import json
import FileUtil
import pandas as pd
# from io import BytesIO
from DataManager import import_files_from_folder, delete_file, process_data, save_to_excel
from werkzeug.utils import secure_filename
from flask_cors import CORS


upload_root_dir = 'uploads'
import os

# 定义保存输出文件的目录
OUTPUT_DIR = 'output'


#app = Flask(__name__, static_folder="templates",static_url_path="/staff-manager")
app = Flask(__name__, template_folder='front-end', static_folder="output", static_url_path="/staff-manager")
CORS(app, origins="http://localhost:3000")

# hello
@app.route('/hello')
def hello_world():
    return "Hello Flask!"

# 默认首页
@app.route('/')
def react():
    return render_template('index.html')


# api接口前缀
apiPrefix = '/api/v1/'



##################  Job接口  ###############

@app.route(apiPrefix + 'getJobList')
def getJobList():
    return DBUtil.getJobList()

@app.route(apiPrefix + 'updateJob', methods=['POST'])
def updateJob():
    data = request.get_data(as_text=True)
    re = DBUtil.addOrUpdateJob(data)
    return re

@app.route(apiPrefix + 'deleteJob/<int:id>')
def deleteJob(id):
    re = DBUtil.deleteJob(id)
    # print(re)
    return re



##################  Company接口  ###############

@app.route(apiPrefix + 'getCompanyList', methods=['GET'])
def getCompanyList():
    return DBUtil.getCompanyList()

@app.route(apiPrefix + 'updateCompany', methods=['POST'])
def updateCompany():
    data = request.get_data(as_text=True)
    re = DBUtil.addOrUpdateCompany(data)
    return re

@app.route(apiPrefix + 'deleteCompany/<int:id>', methods=['DELETE'])
def deleteCompany(id):
    re = DBUtil.deleteCompany(id)
    # print(re)
    return re

@app.route(apiPrefix + 'getCompanyDetails/<int:id>', methods=['GET'])
def getCompanyDetails(id):
    try:
        # 调用数据库工具类的方法获取公司详情
        details = DBUtil.getCompanyDetails(id)
        if details:
            return json.dumps({'code': 0, 'data': details}), 200
        else:
            return json.dumps({'code': 1, 'message': 'Company not found'}), 404
    except Exception as e:
        return json.dumps({'code': -1, 'message': str(e)}), 500



##################  Staff接口  ###############

@app.route(apiPrefix + 'getStaffList/<int:job>')
def getStaffList(job):
    array = DBUtil.getStaffList(job)
    jsonStaffs = DBUtil.getStaffsFromData(array)
    return json.dumps(jsonStaffs)


@app.route(apiPrefix + 'updateStaff', methods=['POST'])
def updateStaff():
    data = request.get_data(as_text=True)
    re = DBUtil.addOrUpdateStaff(data)
    if re['code'] >= 0: # 数据保存成功，移动附件
        FileUtil.fileMoveDir(re['id'])
    return json.dumps(re)


@app.route(apiPrefix + 'deleteStaff/<int:id>')
def deleteStaff(id):
    FileUtil.fileDeleteDir(id)  # 文件删掉
    re = DBUtil.deleteStaff(id)
    return re


@app.route(apiPrefix + 'searchStaff')
def searchStaff():
    data = request.args.get('where')
    # print("searchStaff:", data)
    where = json.loads(data)
    array = DBUtil.searchStaff(where)
    jsonStaffs = DBUtil.getStaffsFromData(array)
    re = json.dumps(jsonStaffs)
    return re



##################  File接口  ###############

@app.route(apiPrefix + 'fileUpload', methods=['POST'])
def fileUpload():
    f = request.files["file"]
    return FileUtil.fileUpload(f)


@app.route(apiPrefix + 'fileDelete/<int:id>/<name>', methods=['GET'])
def fileDelete(id, name):
    return FileUtil.fileDelete(id, name)


@app.route(apiPrefix + 'fileDeleteDir/<int:id>', methods=['GET'])
def fileDeleteDir(id):
    return FileUtil.fileDeleteDir(id)


@app.route(apiPrefix + 'fileGetList/<int:id>', methods=['GET'])
def fileGetList(id):
    return FileUtil.fileGetList(id)


@app.route(apiPrefix + 'fileGet/<int:id>/<name>', methods=['GET'])
def fileGet(id, name):
    path = FileUtil.fileGetDir(id)
    # 参数as_attachment=True，否则对于图片格式、txt格式，会把文件内容直接显示在浏览器，对于xlsx等格式，虽然会下载，但是下载的文件名也不正确
    return send_from_directory(path, name, as_attachment=True)

@app.route(apiPrefix + 'fileBackup')
def fileBackup():
    return DBUtil.saveStaffToCVX(0)

@app.route(apiPrefix + 'fileGetBackup')
def fileGetBackup():
    path = './backup/'
    return send_from_directory(path, 'staffList.csv', as_attachment=True)


##################  DataManager接口  ###############

UPLOAD_FOLDER = 'uploads'  # 临时存储文件的目录
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}  # 允许上传的文件扩展名

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """检查文件扩展名是否有效"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(apiPrefix +'uploadFiles', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'code': -1, 'message': '未上传文件'}), 400
    
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'code': -1, 'message': '没有选择文件'}), 400
    
    # Debug输出每个文件的内容
    for file in files:
        # print(f"文件名: {file.filename}")
        # print(f"文件类型: {file.content_type}")
        # print(f"文件大小: {len(file.read())} bytes")
        
        # 将文件保存到服务器
        file.seek(0)  
        filename = secure_filename(file.filename)
        save_path = os.path.join('uploadsData', filename)
        
        # 确保上传文件夹存在
        if not os.path.exists('uploadsData'):
            os.makedirs('uploadsData')
        
        # 保存文件
        with open(save_path, 'wb') as f:
            f.write(file.read())  # 写入文件内容
        
    return jsonify({'code': 0, 'message': '上传成功'}), 200



# 删除文件接口
@app.route(apiPrefix +'deleteFiles', methods=['POST'])
def api_delete_files():
    data = request.json
    file_paths = data.get('file_paths', [])
    selected_files = data.get('selected_files', [])

    if not file_paths or not selected_files:
        return jsonify({'code': -1, 'message': '文件路径或选中文件不能为空'}), 400

    updated_paths = delete_file(file_paths, selected_files)
    return jsonify({'code': 0, 'message': '文件删除成功', 'data': updated_paths}), 200


# 处理文件接口

@app.route(apiPrefix + '/processFiles', methods=['POST'])
def process_files():
    data = request.get_json()
    file_paths = [os.path.join('uploadsData', filename) 
                  for filename in os.listdir('uploadsData') 
                  if filename.endswith(('.xlsx', '.xls'))]
    
    selected_indices = data['selected_indices']


    print(f"接收到的选中列索引: {selected_indices}")

    if not file_paths:
        return jsonify({'code': -1, 'message': '没有找到可处理的文件'}), 400

    # 处理文件
    merged_data = process_data(file_paths, selected_indices)
    if merged_data is None:
        return jsonify({'code': -1, 'message': '没有有效数据'}), 400

    # 保存合并后的数据
    # output_file_name = 'processed_data.xlsx'
    output_file_path = 'output/processed_data.xlsx'

    # if os.path.exists(output_file_path):
    #     print("文件存在:", output_file_path)
    # else:
    #     print("文件不存在:", output_file_path)

    success = save_to_excel(merged_data, output_file_path)

    if success:
        # 返回文件的下载链接
        download_url = '/static/processed_data.xlsx'
        return jsonify({
            'code': 0,
            'message': '数据处理成功',
            'data': {
                'download_link': download_url  # 直接返回下载链接
            }
        }), 200
    else:
        return jsonify({'code': -1, 'message': '保存文件失败'}), 500


@app.route('/downloadProcessedFile', methods=['GET'])
def download_processed_file():
    file_path = os.path.join('output', 'processed_data.xlsx')
    if os.path.exists(file_path):
        return send_from_directory(directory='output', path='processed_data.xlsx', as_attachment=True)
    else:
        return jsonify({'code': -1, 'message': '文件不存在'}), 404


@app.route(apiPrefix + '/clearCache', methods=['POST'])
def clear_cache():
    folder_path = 'uploadsData'
    
    # 删除 uploadsData 目录下的所有文件
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({'code': 0, 'message': '缓存已清除'}), 200
    except Exception as e:
        return jsonify({'code': -1, 'message': f'无法清除缓存: {str(e)}'}), 500


# if __name__ == '__main__': 确保服务器只会在该脚本被 Python 解释器直接执行的时候才会运行，而不是作为模块导入的时候。
if __name__ == "__main__":
    # 如果不限于本机使用：app.run(host='0.0.0.0')
    # 调试模式，修改文件之后自动更新重启。
    app.run(host='0.0.0.0', port=5000)

