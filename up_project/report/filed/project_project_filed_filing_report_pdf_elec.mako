<html>
<head>
    <style type="text/css">
            ${css}
        td.center-head {
            text-align: center;
        }

        div.pdf-table > table > tbody > tr > td.table-content {
            padding: 20px 0 10px 5px !important;
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
                归档表3/3 ---项目电子文件
            </td>
        </tr>
        <tr>
            <td>路径</td>
            <td>文件名</td>
            <td>归档批次</td>
            <td>创建时间</td>
            <td>文件大小(字节)</td>
        </tr>
            %for (dir_name, attachments) in elec_attachments.items():
                <% head =  dir_name%>
                %for attachment in attachments:
                    <tr>
                        %if head:
                            <td rowspan="${len(attachments)}">/${head}</td>
                        <% head = ''%>
                        %endif
                        <td class="table-content">${attachment.attachment_id.name}</td>
                        <td class="table-content">${attachment.version}</td>
                        <td class="table-content">${attachment.create_date}</td>
                        <td class="table-content">${attachment.attachment_id.file_size}</td>
                    </tr>
                %endfor
            %endfor
        <tr>
            <td>签署人：</td>
            <td>
                %if object.elec_file_approver_id and object.elec_file_approver_id.sign_image:
                    ${helper.embed_image('jpg',object.elec_file_approver_id.sign_image,150)}
                %elif object.elec_file_approver_id and not object.elec_file_approver_id.sign_image:
                    ${object.elec_file_approver_id.name}
                %endif
            </td>
            <td>签署日期：</td>
            <td colspan="2">${object.elec_file_approver_date or ''|entity}</td>
        </tr>
        </tbody>
    </table>
</div>
</body>
</html>