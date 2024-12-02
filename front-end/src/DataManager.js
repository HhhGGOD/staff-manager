import React from 'react';
import HttpUtil from './Utils/HttpUtil'; // 需要自定义后端请求工具
import ApiUtil from './Utils/ApiUtil'; // 配置API路径
import { Button, Upload, message, List, Spin } from 'antd';
// import { UploadOutlined } from '@ant-design/icons';

export default class DataManager extends React.Component {
  state = {
    fileList: [], // 上传的文件列表
    processing: false, // 数据处理状态
    showDownload: false, // 是否显示下载按钮
    downloadUrl: '', // 下载链接
  };

  // 上传文件
  handleUpload = (file) => {
    const formData = new FormData();
    formData.append('file', file);

    HttpUtil.post(ApiUtil.API_FILE_UPLOAD, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
      .then((response) => {
        if (response.code >= 0) {
          this.setState((prevState) => ({
            fileList: [...prevState.fileList, file.name],
          }));
          message.success('文件上传成功');
        } else {
          message.error('文件上传失败');
        }
      })
      .catch((error) => {
        message.error(error.message || '上传错误');
      });

    return false; // 阻止默认的上传行为
  };

  // 删除文件
  handleDelete = (fileName) => {
    this.setState((prevState) => ({
      fileList: prevState.fileList.filter((name) => name !== fileName),
    }));
    message.info(`文件 "${fileName}" 已从列表中移除`);
  };

  // 处理数据（处理整个文件）
  handleProcess = () => {
    if (this.state.fileList.length === 0) {
      message.warning('请先上传文件');
      return;
    }

    this.setState({ processing: true });

    // 假设处理文件的API路径为 /processFile
    HttpUtil.post(ApiUtil.API_FILE_PROCESS)
      .then((response) => {
        if (response.code >= 0) {
          this.setState({
            showDownload: true,
            downloadUrl: response.data.download_url,
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
        {/* 上传文件 */}
        <Upload
          customRequest={({ file }) => this.handleUpload(file)}
          showUploadList={false}
        >
          <Button icon={<Upload />}>上传文件</Button>
        </Upload>

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
                  onClick={() => this.handleDelete(item)}
                >
                  删除
                </Button>,
              ]}
            >
              {item}
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
          >
            下载数据
          </Button>
        )}
      </div>
    );
  }
}
