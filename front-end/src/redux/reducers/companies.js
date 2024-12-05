const initialState = {
    loading: false,
    list: [],        // 公司列表
    message: null    // 错误信息
};

export default function(state = initialState, action) {
    switch (action.type) {
        case 'get_companies_start': {
            return {
                ...state,
                loading: true,
                message: '' // 清空消息
            };
        }
        case 'get_companies_success': {
            // 获取公司列表成功，添加索引
            const data = action.payload.map((item, index) => ({
                ...item,
                index: index + 1 // 添加索引
            }));
            return {
                ...state,
                loading: false,
                list: data, 
                message: '' 
            };
        }
        case 'get_companies_fail': {
            // 获取公司列表失败，记录错误消息
            return {
                ...state,
                loading: false,
                message: action.payload
            };
        }
        case 'update_compgetcompanies_success': {
            // 更新公司信息成功，替换指定项并保持索引顺序
            const updatedList = state.list.map(item =>
                item.id === action.payload.id ? { ...action.payload } : item
            );
            return {
                ...state,
                loading: false,
                list: updatedList, 
                message: '公司信息更新成功' 
            };
        }
        default:
            return state;
    }
}
