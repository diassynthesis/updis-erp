openerp.workflow_china = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.AudittingForm = instance.web.Dialog.extend({
        template: 'auditting_form',
        dialog_title:'Auditting Form',
        events:{
         'change .oe_form_field_select': 'on_change_step',
        },

        on_change_step:function(){
            self =this;
            var context  = new instance.web.CompoundContext(this.data_set.get_context(), this._action_data.context || {});
            //context = [new instance.web.CompoundContext(context)];
            //delete(context.__ref);

            var lang ='en_US';
            try{lang= context.__contexts[0].__contexts[0].lang;}catch(err){}

            instance.session.rpc('web/workflow_china/get_auditters',{
										            model: this.data_set.model,
										            state_cn: this.$el.find(".oe_form_field_select").find("option:selected").text(),
                                                    lang:lang,
                                                    id:this._record_id,
                }).then(
                function(record){
                  var str = QWeb.render('auditting_form.approvers', record);
                  //$(str).appendTo(this.$(".approver_wrapper"));
                  self.$el.find(".auditting_form_approver_div").html(str);
                },

                function(){}
                );
        },

        init:function(parent, options, content, data_set, action__data, record_id) {
            this._super(parent, options, content);
            this.data_set = data_set;
            this._action_data = action__data;
            this._record_id = record_id;
        },

    });

    instance.web.View.include({        
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
	    	//alert("action_data :"+action_data + "  dataset:"+dataset+ "  record_id: "+record_id+"  on_closed: "+on_closed )
	    	var self = this;
            is_reject=false;
	    	if(action_data.type == "workflow_ok" || action_data.type == "workflow_no"
	    		|| action_data.type == "workflow_stop" || action_data.type == "workflow_cancel"){
	    		sta = "" ;
	    		_title= "" ;
	    		if( action_data.type == "workflow_no"){
	    			sta = "no" ;
	    			_title = "驳回" ;
                    is_reject=true;
	    		} else if(action_data.type=="workflow_ok"){
	    			sta = "ok";
	    			_title = "提交(意见可不填)：";
	    		} else if( action_data.type=="workflow_stop"){
	    			sta = "stop";
	    			_title = "中止：";
	    		}else if( action_data.type=="workflow_cancel"){
	    			sta = "cancel";
	    			_title = "撤销：";
	    		}

                instance.session.rpc('web/workflow_china/getRejected2StepList',{
										            model: dataset.model,
										            id: record_id, // wkf_instance id
										            signal: action_data.name,
										            status: sta
                }).then(
                    function(record){
                        context ={rejected:true,
                        steps:record.steps,
                        approvers:record.approvers,
                        default_option:action_data.name,
                        type:action_data.type,
                        }

                        var dialog = new instance.web.AudittingForm(this,{
                            title: _title,
                            dialogClass: 'oe_act_window',
                            width:500,
                            _context:context,
                        },	QWeb.render("auditting_form",context), dataset, action_data, record_id);
                        buttons=[{text: _t("确定"), click: function() {
                            return instance.session.rpc('/web/workflow_china/info', {
                                                            model: dataset.model,
                                                            id: record_id, // wkf_instance id
                                                            signal:action_data.type=="workflow_no"?dialog.$(".oe_form_field_select").val(): action_data.name,// action_data.name,
                                                            note:dialog.$el.find(".oe_textbox_pft_wkl").val(),
                                                            status: sta
                                                        }).then(function(){
                                                            dialog.destroy();
                                                        }).then(function () {
                                                            self.reload();
                                                        });
                                                }
                            }
                            ,{text:_t("取消"),click:function(){dialog.destroy();}}
                        ];
                        dialog._add_buttons(buttons);
                        dialog.open();
                    },
                    function(){
                        alert("failed to load the steps that will be rejected to");
                    }
                );
	    	} else if (action_data.type == "workflow_submit"){
	    		return instance.session.rpc('/web/workflow_china/info', {
										            model: dataset.model,
										            id: record_id, // wkf_instance id
										            signal: action_data.name,
										            note:'提交',
										            status: 'submit'
										        }).then(function () {
										        	self.reload();
									            });
	    	}else if(action_data.type == "workflow_diagram"){
	    	    var context  = new instance.web.CompoundContext(dataset.get_context(), action_data.context || {});
	    	    var ncontext = new instance.web.CompoundContext(context);
	    	    if (record_id){
                    ncontext.add({
                        active_id: record_id,
                        active_ids: [record_id],
                        active_model: dataset.model
                    });
                }
                args=[ncontext];
                var model = new instance.web.Model('workflow.logs');
                model.call(action_data.type, args).then(function(r){self.do_action(r);});
	    	}
	    	else {
	    		return this._super(action_data, dataset, record_id, on_closed) ;
    	    }
    }
    });
    
};

// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
