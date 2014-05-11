<html>
<head>
    <style type="text/css">
        body {
            font-family: "Microsoft YaHei", "SimSun", "Lucida Grande", Helvetica, Verdana, Arial, sans-serif;
            font-size: 14px;
        }

        .pdf-title {
            text-align: center;
        }

        div.pdf-small-title {
            display: inline;
        }

        div.pdf-small-title div {
            display: inline-block;
        }

        .pdf-small-title-right {
            float: right;
        }

        .pdf-small-title-center {
            margin-left: 200px;
        }

        div.pdf-table table {
            border: solid #000000 2px;
            border-collapse: collapse;
            width: 100%;
        }

        div.pdf-table table td {
            border: solid #000000 1px;
        }

    </style>
</head>
<body>
<div>
    <br/>

    <div class="pdf-title">
        <h1>项目文件归档表</h1>
    </div>
    <div class="pdf-small-title">
        <div class="pdf-small-title-left">
            QRT4.2.3-3
        </div>
        <div class="pdf-small-title-center">
            版别/修改码:E/1112
        </div>
        <div class="pdf-small-title-right">
            项目编号: ${object.project_id.xiangmubianhao}
        </div>
    </div>
    <div class="pdf-table">
        <table>
            <tbody>
            <tr>
                <td colspan="2">归档表2/2 ---项目简介</td>
            </tr>
            <tr>
                <td>项目名称</td>
                <td>${object.project_id.name}</td>
            </tr>
            <tr>
                <td>所在地区</td>
                <td>${object.project_id.country_id.name}  ${object.project_id.state_id.name |trim} ${object.project_id.city}</td>
            </tr>
            </tbody>
        </table>
    </div>

</div>
</body>
</html>