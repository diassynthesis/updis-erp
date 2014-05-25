<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang('zh_CN') %>
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
        项目编号: ${object.project_serial_number or ''|entity}
    </div>
</div>
<div class="pdf-table">
    <table>
        <tbody>
        <tr>
            <td colspan="4">
                归档表1/3 ---项目简介
            </td>
        </tr>
        <tr>
            <td style="width: 20%">项目名称</td>
            <td colspan="3" class="table-content">${object.project_id.name or ''|entity}</td>
        </tr>
        <tr>
            <td>项目类别</td>
            <td class="table-content">一级分类：${object.project_category_id.name or ''|entity}<br/>二级分类：${object.project_second_category or ''|entity}
            </td>
            <td>项目负责人</td>
            <td class="table-content">${','.join([u.name for u in object.project_user]) or ''|entity}</td>
        </tr>
        <tr>
            <td>所在地区</td>
            <td class="table-content">
                %if object.project_country_id.name == 'China':
                    中国
                %else:
                    ${object.project_country_id.name or '' | entity}
                %endif
                ${object.project_state_id.name or ''|entity} ${object.project_id.city or ''|entity}
            </td>
            <td>中止项目填写归档阶段</td>
            <td class="table-content">
                %if object.end_stage:
                    ${dict(object._columns['end_stage'].selection)[object.end_stage]}
                %endif
            </td>
        </tr>
        <tr>
            <td>项目规模</td>
            <td colspan="3" class="table-content">${object.project_scale or ''|entity}</td>
        </tr>
        <tr>
            <td>项目起止日期</td>
            <td colspan="3" class="table-content">${object.project_begin_date} ~ ${object.project_end_date}</td>
        </tr>
        <tr>
            <td>项目关键字</td>
            <td colspan="3" class="table-content">
                %if tags:
                    % for tag in tags.items():
                        <div>${tag[0]}: ${','.join(tag[1])}</div>
                    % endfor
                %endif
            </td>
        </tr>
        <tr>
            <td>项目概况</td>
            <td colspan="3" class="table-content">${object.description or ''|n}</td>
        </tr>
        <tr>
            <td>借鉴的主要案例</td>
            <td colspan="3" class="table-content">${object.note or ''|n}</td>
        </tr>
        <tr>
            <td>推荐主要表达图纸名称</td>
            <td colspan="3">
                %for show_image in object.show_images:
                        ${helper.embed_image('jpg',setHtmlImage(show_image.id),150)}
                %endfor
            </td>
        </tr>
        </tbody>
    </table>
</div>
</body>
</html>