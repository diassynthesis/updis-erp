update ir_attachment set name='招标公告1.doc' where id=35;
update ir_attachment set name='招标公告1.docx' where id=74;
update ir_attachment set name='Image_10001.jpg' where id=148;
update ir_attachment set name='Image_20001.jpg' where id=181;
update ir_attachment set name='拓展中心-大鹏小城规划研究和大鹏办事处较场尾片区规划及城市设计研究1.doc' where id=192;
update ir_attachment set name='任务书1.doc' where id=197;
update ir_attachment set name='马鞍山郑蒲港新区关于综合保税区控制性详细规划编制工作的邀请招标书1.pdf' where id=221;
update ir_attachment set name='招标文件1.doc' where id=230;
update ir_attachment set name='滨河区规划及设计招标文件_上网_1.pdf' where id=252;
select * from ir_attachment where name='滨河区规划及设计招标文件_上网_.pdf';
--update toubiao wenjian
update ir_attachment as ir
set
  res_model='project.project',
  res_id=(select project_id from project_attachments where attachment_id=ir.id),
  parent_id=(select res_id from ir_model_data where name='dir_up_project_active')
where id in (select attachment_id from project_attachments);

--update huiyi wenjian
update ir_attachment as ir
set
	res_model='project.project' ,
	res_id = (
	  select project_id from project_project_active_tasking
	  where id = (select tasking_id from project_tasking_attachments where attachment_id=ir.id)
	),
	parent_id=(select res_id from ir_model_data where name='dir_up_project_active')
where id in (select attachment_id from project_tasking_attachments);

--update huiyi contract
update ir_attachment as ir
set
  res_id=(select contract_id from contract_attatchment_many where attachment_id=ir.id),
  parent_id=(select res_id from ir_model_data where name='dir_contract_root')
where res_model='project.contract.contract'