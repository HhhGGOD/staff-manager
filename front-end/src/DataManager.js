import React from 'react';
import HttpUtil from './Utils/HttpUtil'; // 需要自定义后端请求工具
import ApiUtil from './Utils/ApiUtil'; // 配置API路径
import { Collapse, Button, message, List, Spin, Upload } from 'antd';
// import { UploadOutlined } from '@ant-design/icons'; // 上传图标
import exampleImage from './images/文件示例.png'; // 引入图片

export default class DataManager extends React.Component {
  state = {
    fileList: [], // 上传的文件列表
    processing: false, // 数据处理状态
    showDownload: false, // 是否显示下载按钮
    downloadUrl: '', // 下载链接
  };

  // 读取文件夹中的所有文件
  handleFolderChange = (event) => {
    const files = event.target.files;
    console.log('Selected files:', files);  // 打印文件列表
    
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

    console.log('Files to be uploaded:', fileList);

    // 选择多个文件上传
    const formData = new FormData();
    fileList.forEach(file => {
        formData.append('files[]', file);  // 使用 'files[]' 作为文件字段名
    });

    HttpUtil.postData(ApiUtil.API_DATA_FILE_UPLOAD, formData)
        .then(response => {
            // 处理成功响应
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

  // 处理数据（处理整个文件夹中的文件）
  handleProcess = () => {
    if (this.state.fileList.length === 0) {
      message.warning('请先上传文件');
      return;
    }

    this.setState({ processing: true });

    HttpUtil.postData(ApiUtil.API_DATA_FILE_PROCESS, {
      file_paths: this.state.fileList.map((file) => file.name),
    })
      .then((response) => {
        if (response.code >= 0) {
          this.setState({
            showDownload: true,
            downloadUrl: response.data.output_file_path, // 假设返回的是下载文件的 URL
          });
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

  // 下载文件
  handleDownload = () => {
    if (this.state.downloadUrl) {
      window.location.href = this.state.downloadUrl;
    } else {
      message.warning('下载链接不存在');
    }
  };

  render() {
    const { fileList, processing, showDownload } = this.state;

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
        >
          {processing ? <Spin size="small" /> : '处理数据'}
        </Button>

        {/* 下载按钮 */}
        {showDownload && (
          <Button
            type="primary"
            icon="download"
            href={this.state.downloadUrl}
            style={{ marginLeft: 24 }}
            onClick={this.handleDownload}
          >
            下载数据
          </Button>
        )}

        <Collapse style={{ marginTop: 24 }}>
          <Collapse.Panel header="查看文件示例" key="1">
            <p>以下为上传文件的正确格式示例：</p>
            <div style={{ textAlign: 'center' }}> {/* 图片居中 */}
              <img
                src={exampleImage}
                alt="excel示例"
                style={{
                  maxWidth: '100%', // 限制宽度为容器的100%
                  maxHeight: '80vh', // 限制高度为视口的80%
                  objectFit: 'contain', // 确保图片内容不被裁剪
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
