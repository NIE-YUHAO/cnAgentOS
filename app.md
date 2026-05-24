|app.md(本文件，说明整个项目的目录结构及文件归属，是指导A完成开发的重要框架性帮助文件)

|app.py(整个程序的主入口，采用tornado框架构建实现，MVC三层经典架构)

|test.py(程序单元测试用脚本文件，主要用于模块/包/方法的测试，可以写入一些临时性的测试用例)

|  
+---app
|   |   **init**.py
|   |  
|   +---controllers(MVC中的控制层模块)
|   |   |   auth.py(鉴权有关的控制层方法，涉及登录、注册、退出)
|   |   |   base.py(控制层公共基类，提供纺一的登录态获取逻辑，供其他Handler继承使用)

|   |   |   home.py(后台首页控制)
|   |   |   **init**.py
|   |   |  
|   |   ---**pycache**
|   |           auth.cpython-312.pyc
|   |           base.cpython-312.pyc
|   |           home.cpython-312.pyc
|   |           **init**.cpython-312.pyc
|   |  
|   +---models(业务与数据模型层）
|   |   |   db.py(sqlite【数据库访问层】，后续可在此拓展兼容mysql/pgsq等数据库访问逻辑)
|   |   |   user.py(对应用户相关的model)
|   |   |   **init**.py
|   |   |  
|   |   ---**pycache**
|   |           db.cpython-312.pyc
|   |           user.cpython-312.pyc
|   |           **init**.cpython-312.pyc
|   |  
|   +---static(view中的静态资源)
|   |   +---css

|			base.css
|   |   ---js

|			base.js
|   +---templates(view-视图）
|   |       base.html(基础模板)
|   |       index.html(后台首页模板)
|   |       login.html(登录页模板)
|   |       register.html(注册页模板)
|   |  
|   ---**pycache**
|           **init**.cpython-312.pyc
|  
---database(sqlite数据库目录，用于存放sqlite文件或sql脚本文件)
app.db

