<html>
<head>
    <style type="text/css">
            ${css}
        td.center-head {
            text-align: center;
        }
        div.pdf-table > table > tbody > tr > td.table-content {
            padding: 10px 0 10px 5px !important;
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
            <td colspan="5">
                归档表2/3 ---项目纸质文件
            </td>
        </tr>
        <tr>
            <td>类型</td>
            <td>名称</td>
            <td>份数</td>
            <td>页数</td>
            <td>文件号</td>
        </tr>
        %for (type_name, attachments) in paper_attachemnts.items():
            <% head =  type_name%>
            %for attachment in attachments:
                <tr>
                    %if head:
                        <td rowspan="${len(attachments)}">${head}</td>
                        <% head = ''%>
                    %endif
                    <td class="table-content">${attachment.name}</td>
                    <td class="table-content">${attachment.copy_count or ''|entity}</td>
                    <td class="table-content">${attachment.page_count or ''|entity}</td>
                    <td class="table-content">${attachment.document_number or ''|entity}</td>
                </tr>
            %endfor
        %endfor

        </tbody>
    </table>
</div>
</body>
</html>