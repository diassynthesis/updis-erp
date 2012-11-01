(function($) {
      
  $.cleditor.defaultOptions.fonts = "微软雅黑,宋体,黑体,仿宋,幼圆,楷体,Arial Black,Comic Sans MS,Courier New,Narrow,Garamond," +
                    "Georgia,Impact,Sans Serif,Serif,Tahoma,Trebuchet MS,Verdana";
  // Define the fileuploader button
  // ================================== File uploader ===============================
  $.cleditor.buttons.fileuploader = {
    name: "fileuploader",
    // image: "fileuploader.gif",
    title: "Add File",
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
      action:'/web/clupload/upload_file',
      params:{'session_id':openerp.instances.instance0.session.session_id},
      uploadButtonText: "上传文件",
      onComplete: function(id, fileName, responseJSON) {
        var html = "<a href='" + responseJSON.url + "'>"+responseJSON.filename+"</a>";
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
    title: "Add Image",
    command: "inserthtml",
    popupName: "imageuploader",
    popupClass: "cleditorPrompt",
    popupContent: "<div id='imageuploader' />",
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
      action:'/web/clupload/upload_image',
      params:{'session_id':openerp.instances.instance0.session.session_id},
      uploadButtonText: "上传图片",
      allowedExtensions: ['jpeg', 'jpg', 'png', 'gif','bmp'],
      sizeLimit: 3145728, //3M = 3*1024k*1024byte
      onComplete: function(id, imageName, responseJSON) {
        var html = "<img src='" + responseJSON.url + "'/>";
        var editor = data.editor;
        editor.execCommand(data.command, html, null, data.button);
        editor.hidePopups();
        editor.focus();
      }
    });
  };      
 
})(jQuery);
