# -*- coding:utf-8 -*-


import sqlite3
import json
import csv

db_name = 'staff_manager'

conn = sqlite3.connect(db_name + '.db', check_same_thread=False)
cursor = conn.cursor()


def createTables():
    try:
        sql_create_t_job = 'create table IF NOT EXISTS t_job(id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(40) NOT NULL)'
        sql_create_t_staff = '''create table IF NOT EXISTS t_staff(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(40) NOT NULL,
        job INTEGER,
        company VARCHAR(100),
        education SMALLINT,
        gender CHAR(2),
        birth_year SMALLINT,
        hometown VARCHAR(40),
        address VARCHAR(100),
        marriage SMALLINT DEFAULT 0,
        phone VARCHAR(20),
        email VARCHAR(100),
        qq VARCHAR(20),
        wechat VARCHAR(20),
        experience TEXT,
        contact_logs TEXT,
        create_time TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
        modify_time TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime'))
        )'''

        # cursor.execute("drop trigger trigger_auto_timestamp")

        sql_create_trigger_timestamp = '''CREATE TRIGGER IF NOT EXISTS trigger_auto_timestamp
        AFTER UPDATE ON t_staff
        FOR EACH ROW
        BEGIN
            update t_staff set modify_time=datetime('now','localtime') WHERE id = old.id;
        END;
        '''

        #sql_add_address = "alter table t_staff add column address varchar(100) default '';"

        cursor.execute(sql_create_t_job)
        cursor.execute(sql_create_t_staff)
        cursor.execute(sql_create_trigger_timestamp)
        # cursor.execute(sql_add_address)
    except Exception as e:
        print(repr(e))


createTables()


def getJobList():
    tableName = 't_job'

    sql = "select id, name from %s" % (tableName)
    print(sql)

    cursor.execute(sql)

    listAll = cursor.fetchall()     # fetchall() 获取所有记录
    jobs = []
    for item in listAll:
        job = {
            'id': item[0],
            'name': item[1]
        }
        jobs.append(job)

    json_str = json.dumps(jobs)
    print(json_str)

    return json_str


def addOrUpdateJob(json_str):
    try:
        job = json.loads(json_str)
        id = job.get('id', 0)
        name = job.get('name', '')
        result = ''

        if id == 0:  # 新增
            sql = "insert into t_job (name) VALUES ('%s')" % (name)
            # values = (name)
            print(sql)
            cursor.execute(sql)
            result = '添加成功'
            print(cursor.rowcount, result)
        else:   # 修改
            sql = "update t_job set name='%s' where id=%d" % (name, id)
            print(sql)
            cursor.execute(sql)
            result = '更新成功'
            print(cursor.rowcount, result)

        conn.commit()
        re = {
            'code': 0,
            'message': result
        }
        return json.dumps(re)
    except Exception as e:
        re = {
            'code': -1,
            'message': repr(e)
        }
        print(repr(e))
        return json.dumps(re)


def deleteJob(id):
    try:
        sql = "delete from t_job where id=%d" % (id)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        re = {
            'code': 0,
            'message': '删除成功'
        }
        return json.dumps(re)
    except Exception as e:
        re = {
            'code': -1,
            'message': repr(e)
        }
        return json.dumps(re)


def addOrUpdateStaff(json_str):
    try:
        print(json_str)
        staff = json.loads(json_str)
        id = staff.get('id', 0)
        result = ''
        newId = id

        if id == 0:  # 新增
            keys = ''
            values = ''
            isFirst = True
            for key, value in staff.items():
                if isFirst:
                    isFirst = False
                else:
                    keys += ','
                    values += ','
                keys += key
                if isinstance(value, str):
                    values += ("'%s'" % value)
                else:
                    values += str(value)

            sql = "INSERT INTO t_staff (%s) values (%s)" % (keys, values)

            print(sql)
            cursor.execute(sql)
            result = '添加成功'
            newId = cursor.lastrowid
            print(result, "newId:", newId)
        else:   # 修改
            update = ''
            isFirst = True
            for key, value in staff.items():
                if key == 'id':
                    continue
                if isFirst:
                    isFirst = False
                else:
                    update += ","
                if isinstance(value, str):
                    update += (key + "='" + value + "'")
                else:
                    update += (key + "=" + str(value))

            where = "where id=" + str(id)
            sql = "update t_staff set %s %s" % (update, where)
            print(sql)
            cursor.execute(sql)
            result = '更新成功'
            print(cursor.rowcount, result)

        conn.commit()
        re = {
            'code': 0,
            'id': newId,
            'message': result
        }
        return re
    except Exception as e:
        print(repr(e))
        re = {
            'code': -1,
            'message': repr(e)
        }
        return re


def deleteStaff(id):
    try:
        sql = "delete from t_staff where id=%d" % (id)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        re = {
            'code': 0,
            'message': '删除成功'
        }
        return json.dumps(re)
    except Exception as e:
        re = {
            'code': -1,
            'message': repr(e)
        }
        return json.dumps(re)


staffColumns = ('id', 'name', 'job', 'company', 'education', 'gender', 'birth_year',
                'hometown', 'address', 'marriage', 'phone', 'email', 'qq', 'wechat', 'experience', 'contact_logs')

# 将数据库返回结果包装成staff对象（字典）


def getStaffsFromData(dataList):
    staffs = []
    for itemArray in dataList:   # dataList 是数据库返回的数据集，是一个二维数组
        staff = {}

        for columnIndex, columnName in enumerate(staffColumns):
            columnValue = itemArray[columnIndex]

            # # 打印每个员工的公司值，用于调试
            # if columnName == 'company':
            #     print(f"Employee company ID: {columnValue}")

            # 对每一列的空值进行适当的处理
            if columnValue is None:
                if columnName in ('job', 'education', 'birth_year'):  # 针对数字字段使用 0 作为默认值
                    columnValue = 0
                else:
                    columnValue = ''  # 其他字段使用空字符串作为默认值

            # 根据列名处理公司（company）字段，查询公司名称
            if columnName == 'company' and columnValue:
                # 获取公司名称，假设 `columnValue` 是公司 ID
                company_name = getCompanyNameById(columnValue)
                columnValue = company_name if company_name else '未选择'

            staff[columnName] = columnValue

        staffs.append(staff)

    return staffs



def getCompanyNameById(company_id):
    try:
        # print(f"Fetching company name for ID: {company_id}")  # 增加调试日志
        sql = "SELECT name FROM t_company WHERE id = ?"
        cursor.execute(sql, (company_id,))
        company = cursor.fetchone()
        if company:
            # print(f"Found company: {company[0]}")  # 打印找到的公司名
            return company[0]  # 返回公司名称
        else:
            print(f"No company found for ID: {company_id}")  # 未找到公司时的日志
            return None  # 如果没有找到对应的公司，返回 None
    except Exception as e:
        print(f"Error fetching company name: {str(e)}")
        return None



def getStaffList(job):
    tableName = 't_staff'
    where = ''

    if job > 0:
        where = ' where job=%d' % (job)

    columns = ','.join(staffColumns)
    order = ' order by id desc'
    sql = "select %s from %s%s%s" % (columns, tableName, where, order)
    print(sql)

    cursor.execute(sql)

    dateList = cursor.fetchall()     # fetchall() 获取所有记录
    return dateList



def searchStaff(where):
    try:
        sql_where = ''
        sql_like = ''
        
        # 处理 company 筛选条件
        if where.get('company', 0) > 0:
            sql_where = "where company = %d" % where['company']

        # 处理 job 筛选条件
        if where.get('job', 0) > 0:
            if sql_where:
                sql_where += " and job = %d" % where['job']
            else:
                sql_where = "where job = %d" % where['job']
        
        # 处理模糊搜索条件
        where_like_items = []
        for key, value in where.items():
            if isinstance(value, str) and len(value.strip()) > 0:
                where_item = (key + " like '%" + value + "%'")
                where_like_items.append(where_item)
        
        if len(where_like_items) > 0:
            sql_like = "(%s)" % ' or '.join(where_like_items)
        
        if sql_like:
            if sql_where:
                sql_where += " and " + sql_like
            else:
                sql_where = "where " + sql_like

        # 构造最终的 SQL 查询
        columns = ','.join(staffColumns)
        order = ' order by id desc'
        sql = "select %s from t_staff %s%s" % (columns, sql_where, order)

        print(sql)  # 打印 SQL 查询，检查是否正确

        cursor.execute(sql)
        dateList = cursor.fetchall()  # 获取查询结果
        return dateList
    except Exception as e:
        print(repr(e))
        return []



def saveStaffToCVX(jobId):
    try:
        # 这儿编码用utf-8不知道为啥乱码，网上有说utf-8-sig的，也不行，最后改成gb18030好了
        csvfile = open('./backup/staffList.csv', 'w', newline='', encoding='gb18030')
        writer = csv.writer(csvfile)
        writer.writerow(staffColumns)
        staffList = getStaffList(jobId)
        for item in staffList:
            writer.writerow(item)

        csvfile.close()
        return json.dumps({'code': 0})
    except Exception as e:
        print(repr(e))
        return json.dumps({'code': -1, 'message': repr(e)})


def staffTestData():
    insertStaff = {"name": "中文中文", "experience": "中文测试\n\n中文测试",
                   "birth_year": 87, "wechat": "445566"}
    #insertStaff = {"education": 3, "experience": "中文测试\n\n中文测试", "phone": "13760798503", "qq": "969853979", "name": "\u5f20\u4e09\u4e30", "job": 1, "marriage": 0, "gender": "\u7537", "email": "testemail@163.com", "hometown": "\u6e56\u5317", "company": "\u6b66\u5f53\u6d3e", "contact_logs": "中文测试\n中文测试", "birth_year": 87, "wechat": ""}
    updateStaff = {"id": 1, "experience": "中文测试\n\n中文测试",
                   "birth_year": 87, "wechat": "445566"}
    jsonStr = json.dumps(insertStaff)
    print(jsonStr)
    addOrUpdateStaff(jsonStr)



# addOrUpdateJob('{"name": "test23", "index": 8}')
# addOrUpdateJob('{"name": "test23", "id": 8, "index": 8}')
# getJobList()

# staffTestData()
#staffList = getStaffsFromData(getStaffList(0))
# print(str(staffList))
#saveStaffToCVX(0)

#searchStaff({'job':4,'detail':'123'})
#searchStaff({'job':0,'detail':''})



# 获取公司列表
def getCompanyList():
    try:
        # conn = sqlite3.connect('staff_manager.db')
        # cursor = conn.cursor()
        
        # 直接使用静态表名，避免拼接
        sql = "select id, name, detail from t_company"
        # print(sql)  # 打印查询语句用于调试
        cursor.execute(sql)
        companies = cursor.fetchall()
        # 检查是否获取到数据
        if not companies:
            return json.dumps({'code': -1, 'message': 'No data found'})

        result = []
        for company in companies:
            result.append({
                'id': company[0],
                'name': company[1],
                'detail': company[2],
            })
        # print(result)
        return json.dumps(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({'code': -1, 'message': f"Error: {str(e)}"})



# 添加或更新公司
def addOrUpdateCompany(json_str):
    try:
        # 解析 JSON 字符串
        company = json.loads(json_str)
        id = company.get('id', 0)
        name = company.get('name', '')
        detail = company.get('detail', '')
        message = ''
        
        # 连接到数据库
        conn = sqlite3.connect('staff_manager.db')
        cursor = conn.cursor()

        if id == 0:  # 新增公司
            sql = "INSERT INTO t_company (name, detail) VALUES (?, ?)"  # 修正 INSERT 语句
            values = (name, detail)
            # print(sql, values)
            cursor.execute(sql, values)
            conn.commit()
            message = '公司添加成功'
            print(cursor.rowcount, message)
        else:  # 更新公司
            sql = "UPDATE t_company SET name=?, detail=? WHERE id=?"  # 修正 UPDATE 语句
            values = (name, detail, id)
            # print(sql, values)
            cursor.execute(sql, values)
            conn.commit()
            message = '公司更新成功'
            # print(cursor.rowcount,message)

        conn.close()  # 关闭连接
        re = {
            'code': 0,
            'message': message
        }
        return json.dumps(re)
    except Exception as e:
        re = {
            'code': -1,
            'message': repr(e)
        }
        print(repr(e))
        return json.dumps(re)

# 删除公司
def deleteCompany(id):
    try:
        sql = "delete from t_company where id=%d" % (id)
        # print(sql)
        cursor.execute(sql)
        conn.commit()
        re = {
            'code': 0,
            'message': '删除成功'
        }
        return json.dumps(re)
    except Exception as e:
        re = {
            'code': -1,
            'message': repr(e)
        }
        return json.dumps(re)


# 获取公司详情
def getCompanyDetails(id):
    try:
        sql = "SELECT id, name, detail FROM t_company WHERE id = %s"
        # print(sql % id)
        cursor.execute(sql, (id,))
        company = cursor.fetchone()

        if company:
            result = {
                'id': company[0],
                'name': company[1],
                'detail': company[2],
            }
            return json.dumps(result)
        else:
            return json.dumps({'code': -1, 'message': '公司未找到'})
    except Exception as e:
        # print(str(e))
        return json.dumps({'code': -1, 'message': str(e)})