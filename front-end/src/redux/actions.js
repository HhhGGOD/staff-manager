// import companyList from '../companyList';
import ApiUtil from '../Utils/ApiUtil'
import HttpUtil from '../Utils/HttpUtil'
/**
 * 将action抽取出来
 * action名字 => funciton调用
 */


export const getJobs = () => (dispatch, getState) => {
    dispatch({
        type: 'get_jobs_start',
    });
    //先去请求数据
    HttpUtil.get(ApiUtil.API_JOB_LIST)
        .then(
            jobList => {
                //请求数据完成后再dispatch
                dispatch({
                    type: 'get_jobs_success',
                    payload: jobList
                })
            }
        )
        .catch(e => {
            console.log(e)
            dispatch({
                type: 'get_jobs_fail',
                payload: e
            })
        })
};



export const updateJob = (job) => (dispatch, getState) => {
    HttpUtil.post(ApiUtil.API_JOB_UPDATE, job)
        .then(
            re => {
                dispatch({
                    type: 'update_jobs_success',
                    payload: job
                })
            }
        )
        .catch(e => {
            console.log(e)
            dispatch({
                type: 'action_jobs_fail',
                payload: e
            })
        })
};


export const getcompanies = () => async (dispatch) => {
    try {
      dispatch({ type: "get_companies_start" });
      const response = await fetch("/api/v1/getCompanyList");
      const data = await response.json();
      dispatch({ type: "get_companies_success", payload: data });
    } catch (error) {
      dispatch({ type: "get_companies_fail", payload: error.message });
    }
};
  
  


export const updatecompany = (company) => (dispatch, getState) => {
    HttpUtil.post(ApiUtil.API_COMPANY_UPDATE, company)
        .then(
            re => {
                dispatch({
                    type: 'update_compgetcompanies_success',
                    payload: company
                })
            }
        )
        .catch(e => {
            console.log(e)
            dispatch({
                type: 'action_compgetcompanies_fail',
                payload: e
            })
        })
};


export const addJob = () => ({ type: 'addJob' });
export const addcompany = () => ({ type: 'addcompany' });
