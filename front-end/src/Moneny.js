import React from 'react';
import HttpUtil from './Utils/HttpUtil';
import ApiUtil from './Utils/ApiUtil';
import { connect } from "react-redux";
import { getcompanies, updatecompany } from "./redux/actions";
import { Table, Icon, Button, message, Input, Modal } from 'antd';

class CompanyList extends React.Component {
  columns = [
    {
      title: '序号',
      render: (text, record, index) => index + 1,  // 使用数组索引生成序号
      width: 80,
      align: 'center',
    },
    {
      title: '公司',
      dataIndex: 'name',
      width: 300,
      align: 'center',
    },
    {
      title: '资料',
      dataIndex: 'detail',
      align: 'center',
    },
    {
      title: '编辑',
      align: 'center',
      width: 160,
      render: (company) => (
        <span>
          <Icon type="edit" title="编辑" onClick={() => this.showUpdateDialog(company)} />
          <Icon type="close" title="删除" style={{ color: '#ee6633', marginLeft: 12 }} onClick={() => this.deleteConfirm(company)} />
        </span>
      ),
    },
  ];

  state = {
    mcompanies: [],
    showAddDialog: false,
    company: {
      id: 0,
      name: '',
      detail: '', // 新增字段
    }
  };

  // 获取公司列表
  componentDidMount() {
    this.props.getcompanies();
  }

  removeData(id) {
    HttpUtil.delete(ApiUtil.API_COMPANY_DELETE + id)
        .then(re => {
            message.info(re.message); // 成功提示
            this.props.getcompanies(); // 刷新公司列表
        })
        .catch(error => {
            message.error(error.message || '删除失败'); // 错误提示
        });
  }

  render() {
    const { companyList, error } = this.props;
    const { company, showAddDialog } = this.state;

    // 显示错误信息
    if (error) {
      message.error(error.message);
    }

    return (
      <div>
        <div style={{ textAlign: 'right' }} >
          <Button type="primary" icon="plus" onClick={() => this.showUpdateDialog()}>添加</Button>
        </div>
        <Table
          style={{ marginTop: 10 }}
          dataSource={companyList}
          rowKey={item => item.id}
          columns={this.columns}
          pagination={false} 
        />
        
        <Modal
          title={company.id ? "修改公司" : "添加公司"}
          okText="保存"
          cancelText="取消"
          visible={showAddDialog}
          onOk={this.handleAdd}
          onCancel={() => this.setState({ showAddDialog: false })}>
  
          {/* 公司名输入框 */}
          <Input 
            type="text"
            onChange={this.handleTextChanged}
            value={company.name}
            placeholder="请输入公司名"
            style={{ marginBottom: 10 }}
          />

          {/* 公司详情输入框 */}
          <Input 
            type="text"
            onChange={this.handleDetailChanged}  // 新增：处理公司详情输入
            value={company.detail}  // 绑定详情字段
            placeholder="请输入公司详情"
          />
        </Modal>

      </div>
    );
  }

  // 显示添加/编辑对话框
  showUpdateDialog = (company = { id: 0, name: '', detail: '' }) => {
    this.setState({
      showAddDialog: true,
      company: { ...company }
    });
  };

  // 处理表单提交
  handleAdd = () => {
    const { company } = this.state;
    if (company.name && company.detail) {  // 确保公司名称和公司详情都不为空
      HttpUtil.post(ApiUtil.API_COMPANY_UPDATE, company)
        .then(re => {
          message.info(re.message);
          this.setState({ showAddDialog: false });
          this.props.getcompanies();
        })
        .catch(error => {
          message.error(error.message);
        });
    } else {
      message.error('请输入公司名和公司详情');
    }
  };

  // 更新公司名称
  handleTextChanged = (e) => {
    const name = e.target.value;
    this.setState(prevState => ({
        company: { ...prevState.company, name }
    }));
  };

  // 更新公司详情
  handleDetailChanged = (e) => {
    const detail = e.target.value;
    this.setState(prevState => ({
        company: { ...prevState.company, detail }
    }));
  };

  // 删除公司确认
  deleteConfirm = (company) => {
    const modal = Modal.confirm({
      title: '确认',
      content: '确定要删除该公司信息吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        this.removeData(company.id);
        modal.destroy();
      },
      onCancel() { },
    });
  };
}

const mapStateToProps = (state) => {
  return {
    companyList: state.companies.list, 
    error: state.companies.message   
  };
};

export default connect(mapStateToProps, { getcompanies, updatecompany })(CompanyList);
