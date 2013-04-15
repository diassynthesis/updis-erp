(function ($) {

    $.cleditor.defaultOptions.fonts = "微软雅黑,宋体,黑体,仿宋,幼圆,楷体,Arial Black,Comic Sans MS,Courier New,Narrow,Garamond," +
        "Georgia,Impact,Sans Serif,Serif,Tahoma,Trebuchet MS,Verdana";
    // Define the fileuploader button
    // ================================== File uploader ===============================
    $.cleditor.buttons.fileuploader = {
        name: "fileuploader",
        // image: "fileuploader.gif",
        stripIndex: 28,
        title: "添加文件",
        command: "inserthtml",
        popupName: "fileuploader",
        popupClass: "cleditorPrompt",
        popupContent: "<div id='fileuploader' />",
        buttonClick: fileuploaderClick
    };
    // Add the button to the default controls before the bold button
    $.cleditor.defaultOptions.controls = $.cleditor.defaultOptions.controls
        .replace("link ", "link fileuploader ");

    // Handle the fileuploader button click event
    function fileuploaderClick(e, data) {
        // Wire up the submit button click event
        var uploader = new qq.FileUploader({
            element: $(data.popup).find("#fileuploader")[0],
            action: '/web/clupload/upload_file',
            params: {'session_id': openerp.instances.instance0.session.session_id},
            uploadButtonText: "上传文件",
            onComplete: function (id, fileName, responseJSON) {
                var html = "<a href='" + responseJSON.url + "'>" + responseJSON.filename + "</a>";
                var editor = data.editor;
                editor.execCommand(data.command, html, null, data.button);
                editor.hidePopups();
                editor.focus();
            }
        });
    };

    // ======================== Image uploader ============================
    $.cleditor.buttons.imageuploader = {
        name: "imageuploader",
        // image: "imageuploader.gif",
        stripIndex: 23,
        title: "添加图片",
        command: "inserthtml",
        popupName: "imageuploader",
        popupClass: "cleditorPrompt",
        popupContent: "<div id='imageuploader' /><div id='imagecontainer'/>",
        buttonClick: imageuploaderClick
    };
    // Add the button to the default controls before the bold button
    $.cleditor.defaultOptions.controls = $.cleditor.defaultOptions.controls
        .replace("image ", "image imageuploader ");

    // Handle the imageuploader button click event
    function imageuploaderClick(e, data) {
        // Wire up the submit button click event
        var uploader = new qq.FileUploader({
            element: $(data.popup).find("#imageuploader")[0],
            action: '/web/clupload/upload_image',
            params: {'session_id': openerp.instances.instance0.session.session_id},
            uploadButtonText: "上传图片",
            allowedExtensions: ['jpeg', 'jpg', 'png', 'gif', 'bmp'],
            sizeLimit: 3145728, //3M = 3*1024k*1024byte
            disableDefaultDropzone: true,
            onComplete: function (id, imageName, responseJSON) {
                var html = "<img id='target' src='" + responseJSON.url + "'/>";
                var editor = data.editor;
                // $(html).appendTo($(data.popup).find('#imagecontainer'));
                // $(data.popup).find('#target').Jcrop();
                editor.execCommand(data.command, html, null, data.button);
                editor.hidePopups();
                editor.focus();
            }
        });
    };

    $.cleditor.buttons.bold.title = "粗体";
    $.cleditor.buttons.italic.title = "斜体";
    $.cleditor.buttons.underline.title = "下划线";
    $.cleditor.buttons.strikethrough.title = "删除线";
    $.cleditor.buttons.removeformat.title = "删除格式";
    $.cleditor.buttons.bullets.title = "行标";
    $.cleditor.buttons.numbering.title = "行号";
    $.cleditor.buttons.outdent.title = "减小缩进";
    $.cleditor.buttons.indent.title = "增大缩进";
    $.cleditor.buttons.link.title = "添加超链接";
    $.cleditor.buttons.unlink.title = "删除超链接";
    $.cleditor.buttons.icon.title = "表情";
    $.cleditor.buttons.source.title = "查看源码";

})(jQuery);
