import React from 'react';
import HttpUtil from './Utils/HttpUtil';
import ApiUtil from './Utils/ApiUtil';

import { connect } from "react-redux";
import { getJobs, updateJob } from "./redux/actions";

import {
    Table, Icon, Button, message, Input, Modal
} from 'antd';

class JobList extends React.Component {
    columns = [{
        title: '序号',
        dataIndex: 'index',  // 显示的是index
        width: 80,
        align: 'center'
    }, {
        title: '职位',
        dataIndex: 'name',
    }, {
        title: '编辑',
        align: 'center',
        width: 160,
        render: (job) => (
            <span>
                <Icon type="edit" title="编辑" onClick={() => this.showUpdateDialog(job)} />
                <Icon type="close" title="删除" style={{ color: '#ee6633', marginLeft: 12 }} onClick={() => this.deleteConfirm(job)} />
            </span>
        ),
    }];

    state = {
        mJobs: [],
        showAddDialog: false,
        job: {}
    };

    removeData(id) {
        HttpUtil.get(ApiUtil.API_JOB_DELETE + id)
            .then(
                re => {
                    message.info(re.message);
                    this.props.getJobs();  // 获取最新的职位列表，触发重新渲染
                }
            ).catch(error => {
                message.error(error.message);
            });
    }

    componentDidMount() {
        this.props.getJobs();  // 获取职位列表
    }

    render() {
        if (this.props.message) {
            message.error(this.props.message.message);
        }

        return (
            <div>
                <div style={{ textAlign: 'right' }} >
                    <Button type="primary" icon="plus"
                        onClick={() => this.showUpdateDialog()}>添加</Button>
                </div>
                <Table
                    style={{ marginTop: 10 }}
                    dataSource={this.props.jobList}  // 使用从 Redux 获取的数据
                    rowKey={item => item.id}
                    columns={this.columns}
                    pagination={false} />
                
                <Modal
                    title={this.state.job.id ? "修改职位" : "添加职位"}
                    okText="保存"
                    cancelText="取消"
                    visible={this.state.showAddDialog}
                    onOk={this.handleAdd}
                    onCancel={() => this.setState({ showAddDialog: false })}>
                    <Input type='text'
                        onChange={this.handleTextChanged}
                        value={this.state.job.name}
                        placeholder="请输入职位名" />
                </Modal>
            </div>
        )
    }

    showUpdateDialog = (job) => {
        if (job === undefined) {
            job = {
                id: 0,
                name: ''
            };
        }
        let currentJob = Object.assign({}, this.state.job, job);     // 对象赋值，同时注意不要给state直接赋值，先追加到空对象{}
        this.setState({
            showAddDialog: true,
            job: currentJob
        });
    }

    handleAdd = () => {
        let job = this.state.job;
        if (job.name) {
            HttpUtil.post(ApiUtil.API_JOB_UPDATE, job)
                .then(
                    re => {
                        message.info(re.message);
                        this.setState({
                            showAddDialog: false
                        });
                        this.props.getJobs();  // 获取最新职位列表
                    }
                ).catch(error => {
                    message.error(error.message);
                });
        } else {
            message.error('请输入职位名');
        }
    }

    handleTextChanged = (e) => {
        let currentJob = Object.assign({}, this.state.job, { 'name': e.target.value });
        this.setState({
            job: currentJob
        });
    }
    
    deleteConfirm = (company) => {
        Modal.confirm({
          title: '确认',
          content: '确定要删除该公司信息吗？',
          okText: '确认',
          cancelText: '取消',
          onOk: () => {
            this.removeData(company.id); // 执行删除操作
          },
          onCancel() { },
        });
      };
      
}

const mapStateToProps = (state) => {
    // 为每个职位重新分配序号
    const jobListWithIndex = state.jobs.jobs.map((job, index) => ({
        ...job, 
        index: index + 1  // 重新分配序号
    }));
    return {
        jobList: jobListWithIndex,  // 返回带有序号的职位列表
        error: state.jobs.message
    }
}

export default connect(
    mapStateToProps,      
    { getJobs, updateJob }
)(JobList);
