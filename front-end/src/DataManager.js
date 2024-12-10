import React from 'react';
import HttpUtil from './Utils/HttpUtil'; // 需要自定义后端请求工具
import ApiUtil from './Utils/ApiUtil'; // 配置API路径
import { Collapse, Button, message, List, Checkbox, Spin, Upload } from 'antd';
// import { UploadOutlined } from '@ant-design/icons'; // 上传图标
import exampleImage from './images/文件示例.png'; // 引入图片

export default class DataManager extends React.Component {
  state = {
    fileList: [], // 上传的文件列表
    processing: false, // 数据处理状态
    showDownload: false, // 是否显示下载按钮
    downloadUrl: '', // 下载链接
    selectedColumns: ['姓名'], // 姓名列默认选中并固定
    columnButtons: ['姓名', '基本工资', '岗位工资', '工龄工资', '考核工资', '预发效益', '加班工资', '补发', '应发工资',  '医疗保险', '失业保险', '住房公积金', '工会费',  '其他扣除',  '个人所得税',  '实发工资'],
  };

  // 读取文件夹中的所有文件
  handleFolderChange = (event) => {
    const files = event.target.files;
    // console.log('Selected files:', files);  // 打印文件列表
    
    if (files.length === 0) {
      message.warning('没有选择任何文件');
      return;
    }

    const fileList = [];
    for (let i = 0; i < files.length; i++) {
      fileList.push(files[i]);
    }

    this.setState({ fileList: fileList });
  };

  // 上传文件夹中的所有文件
  handleUpload = () => {
    const { fileList } = this.state;
    if (fileList.length === 0) {
      message.warning('请先选择文件夹');
      return;
    }

    // console.log('Files to be uploaded:', fileList);

    // 选择多个文件上传
    const formData = new FormData();
    fileList.forEach(file => {
        formData.append('files[]', file);  // 使用 'files[]' 作为文件字段名
    });

    HttpUtil.postData(ApiUtil.API_DATA_FILE_UPLOAD, formData)
        .then(response => {
            // 处理成功响应
            message.info(`文件上传成功`);
        })
        .catch(error => {
            // 处理错误
        });
  };

  // 删除文件
  handleDelete = (fileName) => {
    this.setState((prevState) => ({
      fileList: prevState.fileList.filter((file) => file.name !== fileName),
    }));
    message.info(`文件 "${fileName}" 已从列表中移除`);
  };


// 清理缓存方法
handleClearCache = () => {
  HttpUtil.postData(ApiUtil.API_DATA_CLEAR_CACHE)  // 假设后端清除缓存接口路径为 `API_DATA_CLEAR_CACHE`
    .then((response) => {
      if (response.code >= 0) {
        message.success('缓存清除成功');
        
        // 清空前端文件列表
        this.setState({ fileList: [] });
      } else {
        message.error(response.message || '清除缓存失败');
      }
    })
    .catch((error) => {
      message.error(error.message || '清除缓存失败');
    });
};
  
  handleColumnChange = (selectedColumns) => {
    if (!selectedColumns.includes('姓名')) {
      selectedColumns.push('姓名');
    }
    this.setState({ selectedColumns });
  };

  // 处理数据（处理整个文件夹中的文件）
  handleProcess = (event) => {
    event.preventDefault();  // 确保阻止默认的表单提交行为

    const { selectedColumns, fileList, columnButtons } = this.state;

    if (fileList.length === 0) {
      message.warning('请先上传文件');
      return;
    }
    
    if (selectedColumns.length === 0) {
      message.warning('请选择至少一个列');
      return;
    }

    this.setState({ processing: true });
    
    const selectedIndices = selectedColumns.map((col) => columnButtons.indexOf(col));
    if (selectedIndices.includes(-1)) {
      message.warning('选中的列包含无效项');
      return;
    }

    HttpUtil.postData(ApiUtil.API_DATA_FILE_PROCESS, {
      file_paths: fileList.map((file) => file.name),
      selected_indices: selectedIndices,
    })
      .then((response) => {
        if (response.code >= 0) {
          const downloadLink = response.data.download_link;
          console.log('下载链接:', downloadLink);
  
          // 创建一个临时的 <a> 标签来触发下载
          const link = document.createElement('a');
          window.location.href = 'http://localhost:5000/downloadProcessedFile';

          document.body.appendChild(link);
          link.click();  
          document.body.removeChild(link);  
          
          message.success('数据处理成功');
        } else {
          message.error('数据处理失败');
        }
      })
      .catch((error) => {
        message.error(error.message || '处理失败');
      })
      .finally(() => {
        this.setState({ processing: false });
      });
  };
  
  
  

  render() {
    const { fileList, processing, columnButtons, selectedColumns} = this.state;

    return (
      <div style={{ marginTop: 24 }}>
        {/* 选择文件夹 */}
        <input
          type="file"
          webkitdirectory="true"
          onChange={this.handleFolderChange}
          style={{ display: 'none' }}
          ref={(input) => { this.fileInput = input; }}
        />
        <Button icon={<Upload />} onClick={() => this.fileInput.click()}>
          选择文件夹
        </Button>

        {/* 上传按钮 */}
        <Button
          type="primary"
          onClick={this.handleUpload}
          disabled={fileList.length === 0}
          style={{ marginLeft: 16 }}
        >
          上传文件
        </Button>

        {/* 选择列 */}
        <div style={{ marginTop: 16 }}>
          <Checkbox.Group
            options={columnButtons}
            value={selectedColumns}
            onChange={this.handleColumnChange}
          />
          <Checkbox value="姓名" disabled checked={selectedColumns.includes('姓名')} style={{ display: 'none' }} />
        </div>

        {/* 文件列表 */}
        <List
          bordered
          dataSource={fileList}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  danger
                  onClick={() => this.handleDelete(item.name)}
                >
                  删除
                </Button>,
              ]}
            >
              {item.name}
            </List.Item>
          )}
          style={{ margin: '16px 0' }}
        />

        {/* 处理按钮 */}
        <Button
          type="primary"
          onClick={this.handleProcess}
          disabled={fileList.length === 0 || processing}
          htmlType="button"  // 确保按钮的类型是 "button" 而不是 "submit"
        >
          {processing ? <Spin size="small" /> : '处理数据'}
        </Button>



        <Button
          type="danger"
          onClick={this.handleClearCache}
          style={{ marginLeft: 16 }}
        >
          清除缓存
        </Button>

        <Collapse style={{ marginTop: 24 }}>
          <Collapse.Panel header="查看文件示例" key="1">
            <p>以下为上传文件的正确格式示例：</p>
            <div style={{ textAlign: 'center' }}> {/* 图片居中 */}
              <img
                src={exampleImage}
                alt="excel示例"
                style={{
                  maxWidth: '100%', 
                  maxHeight: '80vh', 
                  objectFit: 'contain', 
                  cursor: 'pointer',
                }}
                onClick={() => window.open(exampleImage, "_blank")} // 点击图片打开新窗口
              />
            </div>
          </Collapse.Panel>
        </Collapse>


      </div>
    );
  }
}
