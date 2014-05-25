<html>
<head>
    <style type="text/css">
            ${css}
        td.center-head {
            text-align: center;
        }
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
                归档表1/3 ---项目纸质文件
            </td>
        </tr>

        <!------------>
        <tr>
            <td colspan="4" class="center-head">文本类成果归档目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td colspan="2">纸质文件名称</td>
            <td>份数</td>
        </tr>
            <% i = 1%>
            % for file_record in file_records['1'] :
                <tr>
                    <td  class="table-content">${i}</td>
                    <td  class="table-content" colspan="2">${file_record.name}</td>
                    <td  class="table-content">${file_record.copy_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['1']):
                <tr>
                    <td class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

        <!------------>
        <tr>
            <td colspan="4" class="center-head">图件成果（有图签、会签栏）归档目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td colspan="2">图件名称</td>
            <td>张数</td>
        </tr>
            <% i = 1%>
            % for file_record in file_records['2'] :
                <tr>
                    <td class="table-content">${i}</td>
                    <td class="table-content" colspan="2">${file_record.name}</td>
                    <td class="table-content">${file_record.page_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['2']):
                <tr>
                    <td class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

        <!------------>
        <tr>
            <td colspan="4" class="center-head">计算书归档目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td>计算书内容</td>
            <td>本数</td>
            <td>页数</td>
        </tr>
            <% i = 1%>
            % for file_record in file_records['3'] :
                <tr>
                    <td class="table-content">${i}</td>
                    <td class="table-content">${file_record.name}</td>
                    <td class="table-content">${file_record.copy_count or 0 | entity}</td>
                    <td class="table-content">${file_record.page_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['3']):
                <tr>
                    <td  class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

        <!------------>
        <tr>
            <td colspan="4" class="center-head">项目过程管理记录单目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td colspan="2">表单名称</td>
            <td>页数</td>
        </tr>
            <% i = 1%>
            % for file_record in file_records['4'] :
                <tr>
                    <td class="table-content">${i}</td>
                    <td class="table-content" colspan="2">${file_record.name}</td>
                    <td class="table-content">${file_record.page_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['4']):
                <tr>
                    <td class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

        <!------------>
        <tr>
            <td colspan="4" class="center-head">重要依据性文件归档目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td>文件名称</td>
            <td>份数</td>
            <td>页数</td>
        </tr>
            <% i = 1%>
            % for file_record in file_records['5'] :
                <tr>
                    <td class="table-content">${i}</td>
                    <td class="table-content">${file_record.name}</td>
                    <td class="table-content">${file_record.copy_count or 0 | entity}</td>
                    <td class="table-content">${file_record.page_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['5']):
                <tr>
                    <td class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

        <!------------>
        <tr>
            <td colspan="4" class="center-head">项目依据性资料目录</td>
        </tr>
        <tr>
            <td>序号</td>
            <td>资料名称</td>
            <td>份数</td>
            <td>页数</td>
        </tr>

            <% i = 1%>
            % for file_record in file_records['6'] :
                <tr>
                    <td class="table-content">${i}</td>
                    <td class="table-content">${file_record.name}</td>
                    <td class="table-content">${file_record.copy_count or 0 | entity}</td>
                    <td class="table-content">${file_record.page_count or 0 | entity}</td>
                </tr>
                <% i+=1%>
            % endfor
            % if not len(file_records['6']):
                <tr>
                    <td class="table-content" colspan="4">没有记录</td>
                </tr>
            % endif

            <% i = 1%>
            % for file_record in file_records['7'] :
                <tr>
                    <td class="table-content">电子文件</td>
                    <td class="table-content" colspan="3">${file_record.name}</td>
                </tr>
                <% i+=1%>
            % endfor
        </tbody>
    </table>
</div>
</body>
</html>