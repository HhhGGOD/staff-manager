
/**
 * 对fetch方法进行基础封装，统一请求参数，使直接返回Json格式。
 */
export default class HttpUtil {

    /**
     * http get请求
     */
    static get(url) {
        return new Promise((resolve, reject) => {
            fetch(url)
                .then(response => {
                    if (response.ok) {
                        return response.json(); // 将文本结果转成json对象
                    } else {
                        throw new Error(response.status + " : " + response.statusText)
                    }
                })
                .then(result => resolve(result))
                .catch(error => {
                    reject(error);
                })
        });
    }


    /**
     * http post请求
     */
    static post(url, data) {
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: 'POST',
                header: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)  // 将json对象转成文本
            })
                .then(response => response.json())
                .then(result => resolve(result))
                .catch(error => {
                    reject(error);
                })
        });
    }

    static delete(url) {
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: 'DELETE', // 确认使用 DELETE 方法
            })
                .then(response => {
                    if (response.ok) {
                        return response.json(); // 解析返回的 JSON
                    } else {
                        throw new Error(response.status + " : " + response.statusText);
                    }
                })
                .then(result => resolve(result))
                .catch(error => reject(error));
        });
    }
    

    static postData(url, data) {
        return new Promise((resolve, reject) => {
            // 判断是否是 FormData 对象（用于文件上传）
            const headers = data instanceof FormData ? {} : {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            };
    
            fetch(url, {
                method: 'POST',
                headers: headers,  // 如果是 FormData，不需要设置 Content-Type，浏览器会自动处理
                body: data,  // 如果是 FormData，直接将其传递给 body
            })
                .then(response => response.json())
                .then(result => resolve(result))
                .catch(error => {
                    reject(error);
                })
        });
    }
    
}

