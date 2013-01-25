--active employee with dep and pos. make sure to import pos and dep first!
SELECT 'USR_'+dbo.LZ_MISUser.SU_UserID AS 'User External Id', 
      'EMP_'+dbo.LZ_MisUser.SU_UserID as 'Emp External Id',
	dbo.LZ_MISUser.SU_UserName AS [user], 
      dbo.LZ_MISUser.SU_UserName AS name, dbo.LZ_MISUser.SU_LoginName AS login, 
      ~dbo.LZ_MISUser.SU_IsDel AS active, dbo.LZ_MisUserAddressBook.SU_EmpAddr AS work_location, 
      dbo.LZ_MisUserAddressBook.SU_EmpHmTel AS home_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpMobile AS mobile_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpComTel AS work_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpEAddr AS work_email, 
      	dbo.LZ_MISUserInfo.SU_Sex AS gender, 
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_Birthday, 111),'/','-') AS birthday, 
      dbo.LZ_MISUserInfo.SU_Folk AS folk,  
      dbo.LZ_MISUserInfo.SU_NativePlace AS [native place], 
	dbo.LZ_MISUserInfo.SU_Bio AS notes, 
      dbo.LZ_MISUserInfo.SU_Diploma AS diploma, 
      dbo.LZ_MISUserInfo.SU_Degree AS degree, 
      dbo.LZ_MISUserInfo.SU_Academy AS academy,
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_BeginWorkDate, 111),'/','-') AS begin_work_date, 
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_EnterDate, 111),'/','-') AS enter_date, 
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_ContractDate, 111),'/','-') AS contract_date, 
      dbo.LZ_MISUserInfo.SU_Aptitude AS [aptitude],
      dbo.LZ_MISUserInfo.SU_Speciality AS major,
      dbo.LZ_MISUserInfo.SU_YearVacDays AS year_vac_days,
      dbo.LZ_MISUserInfo.SU_HaveVacDays AS have_vac_days,
      dbo.LZ_MISUserInfo.SU_Insurance AS insurance,
      dbo.LZ_MISUserInfo.SU_BearPalm AS awards,
      dbo.LZ_MISUserInfo.SU_StudyList AS study_list,
      dbo.LZ_MISUserInfo.SU_Interest AS interest,
      dbo.LZ_MISUserInfo.SU_Practice AS practice,
      dbo.LZ_MISUserInfo.SU_GoAbroadList AS go_abroad_list,
      dbo.LZ_MISUserInfo.SU_JoinPloy AS join_ploy,
      dbo.LZ_MISUserInfo.SU_StrongPoint AS strong_point,
      dbo.LZ_MISUserInfo.SU_Business AS business,
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_BusinessDate, 111),'/','-') AS business_date, 
      dbo.LZ_MISUserInfo.SU_Duty AS duty,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_DutyDate, 111),'/','-') AS duty_date, 
      dbo.LZ_MISUserInfo.SU_Title AS title,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_TitleDate, 111),'/','-') AS title_date, 
      dbo.LZ_MISUserInfo.SU_RegTax AS reg_tax,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_RegTaxDate, 111),'/','-') AS reg_tax_date, 
      dbo.LZ_MISUserInfo.SU_RegTaxNo AS reg_tax_no,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_GraDate, 111),'/','-') AS gra_date, 
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_OutDate, 111),'/','-') AS out_date, 
      dbo.LZ_MISPosInfo.PI_PosID as [job/external id],
      dbo.LZ_MISDepartment.UG_UserGrpID AS [department/external id]
FROM dbo.LZ_MISUser INNER JOIN
      dbo.LZ_MisUserAddressBook ON 
      dbo.LZ_MISUser.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISUserInfo ON 
      dbo.LZ_MISUserInfo.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISDepPosUser ON 
      dbo.LZ_MISDepPosUser.SU_UserID = dbo.LZ_MISUserInfo.SU_UserID INNER JOIN
      dbo.LZ_MISDepPos ON 
      dbo.LZ_MISDepPosUser.DP_ID = dbo.LZ_MISDepPos.DP_ID INNER JOIN
      dbo.LZ_MISPosInfo ON 
      dbo.LZ_MISDepPos.PI_PosID = dbo.LZ_MISPosInfo.PI_PosId INNER JOIN
      dbo.LZ_MISDepartment ON
      dbo.LZ_MISDepartment.UG_UserGrpID = dbo.LZ_MISDepPos.UG_UserGrpID
WHERE (dbo.LZ_MISUser.SU_IsDel=0) AND 
	(dbo.LZ_MISUser.SU_LoginName <> 'admin') AND
	      (dbo.LZ_MISDepPos.UG_UserGrpID <> 'UG050721000001')
-- non active employees with dep and pos.
SELECT 'USR_'+dbo.LZ_MISUser.SU_UserID AS 'User External Id', 
      'EMP_'+dbo.LZ_MisUser.SU_UserID as 'Emp External Id',
	dbo.LZ_MISUser.SU_UserName AS [user], 
      dbo.LZ_MISUser.SU_UserName AS name, dbo.LZ_MISUser.SU_LoginName AS login, 
      ~dbo.LZ_MISUser.SU_IsDel AS active, dbo.LZ_MisUserAddressBook.SU_EmpAddr AS work_location, 
      dbo.LZ_MisUserAddressBook.SU_EmpHmTel AS home_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpMobile AS mobile_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpComTel AS work_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpEAddr AS work_email, 
      	dbo.LZ_MISUserInfo.SU_Sex AS gender, 
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_Birthday, 111),'/','-') AS birthday, 
      dbo.LZ_MISUserInfo.SU_Folk AS folk,  
      dbo.LZ_MISUserInfo.SU_NativePlace AS [native place], 
	dbo.LZ_MISUserInfo.SU_Bio AS notes, 
      dbo.LZ_MISUserInfo.SU_Diploma AS diploma, 
      dbo.LZ_MISUserInfo.SU_Degree AS degree, 
      dbo.LZ_MISUserInfo.SU_Academy AS academy,
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_BeginWorkDate, 111),'/','-') AS begin_work_date, 
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_EnterDate, 111),'/','-') AS enter_date, 
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_ContractDate, 111),'/','-') AS contract_date, 
      dbo.LZ_MISUserInfo.SU_Aptitude AS [aptitude],
      dbo.LZ_MISUserInfo.SU_Speciality AS major,
      dbo.LZ_MISUserInfo.SU_YearVacDays AS year_vac_days,
      dbo.LZ_MISUserInfo.SU_HaveVacDays AS have_vac_days,
      dbo.LZ_MISUserInfo.SU_Insurance AS insurance,
      dbo.LZ_MISUserInfo.SU_BearPalm AS awards,
      dbo.LZ_MISUserInfo.SU_StudyList AS study_list,
      dbo.LZ_MISUserInfo.SU_Interest AS interest,
      dbo.LZ_MISUserInfo.SU_Practice AS practice,
      dbo.LZ_MISUserInfo.SU_GoAbroadList AS go_abroad_list,
      dbo.LZ_MISUserInfo.SU_JoinPloy AS join_ploy,
      dbo.LZ_MISUserInfo.SU_StrongPoint AS strong_point,
      dbo.LZ_MISUserInfo.SU_Business AS business,
      replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_BusinessDate, 111),'/','-') AS business_date, 
      dbo.LZ_MISUserInfo.SU_Duty AS duty,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_DutyDate, 111),'/','-') AS duty_date, 
      dbo.LZ_MISUserInfo.SU_Title AS title,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_TitleDate, 111),'/','-') AS title_date, 
      dbo.LZ_MISUserInfo.SU_RegTax AS reg_tax,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_RegTaxDate, 111),'/','-') AS reg_tax_date, 
      dbo.LZ_MISUserInfo.SU_RegTaxNo AS reg_tax_no,
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_GraDate, 111),'/','-') AS gra_date, 
	replace(CONVERT(varchar, 
		      dbo.LZ_MISUserInfo.SU_OutDate, 111),'/','-') AS out_date, 
      dbo.LZ_MISPosInfo.PI_PosID as [job/external id],
      dbo.LZ_MISDepartment.UG_UserGrpID AS [department/external id]
FROM dbo.LZ_MISUser INNER JOIN
      dbo.LZ_MisUserAddressBook ON 
      dbo.LZ_MISUser.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISUserInfo ON 
      dbo.LZ_MISUserInfo.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISDepPosUser ON 
      dbo.LZ_MISDepPosUser.SU_UserID = dbo.LZ_MISUserInfo.SU_UserID INNER JOIN
      dbo.LZ_MISDepPos ON 
      dbo.LZ_MISDepPosUser.DP_ID = dbo.LZ_MISDepPos.DP_ID INNER JOIN
      dbo.LZ_MISPosInfo ON 
      dbo.LZ_MISDepPos.PI_PosID = dbo.LZ_MISPosInfo.PI_PosId INNER JOIN
      dbo.LZ_MISDepartment ON
      dbo.LZ_MISDepartment.UG_UserGrpID = dbo.LZ_MISDepPos.UG_UserGrpID
WHERE (dbo.LZ_MISUser.SU_IsDel=1) AND 
	(dbo.LZ_MISUser.SU_LoginName <> 'admin') AND
	      (dbo.LZ_MISDepPos.UG_UserGrpID <> 'UG050721000001')
--department
SELECT UG_UserGrpID AS [external id], UG_UserGrpName AS name, 
      UG_IsDel AS deleted,
      UG_InUse AS is_in_use,
      ug_usergrpforshort AS short_name
FROM dbo.LZ_MISDepartment

--position
SELECT PI_PosId AS [external id], PI_PosName AS name, Remark AS description
FROM dbo.LZ_MISPosInfo

--user position and department
SELECT 'EMP_'+dbo.LZ_MISDepPosUser.SU_UserID AS [external id], 
      dbo.LZ_MISDepPos.PI_PosID AS [job/external id], 
      dbo.LZ_MISDepPos.UG_UserGrpID AS [department/external id], 
      dbo.LZ_MISUser.SU_UserName AS name
FROM dbo.LZ_MISDepPosUser INNER JOIN
      dbo.LZ_MISDepPos ON 
      dbo.LZ_MISDepPosUser.DP_ID = dbo.LZ_MISDepPos.DP_ID INNER JOIN
      dbo.LZ_MISPosInfo ON 
      dbo.LZ_MISDepPos.PI_PosID = dbo.LZ_MISPosInfo.PI_PosId INNER JOIN
      dbo.LZ_MISUser ON 
      dbo.LZ_MISDepPosUser.SU_UserID = dbo.LZ_MISUser.SU_UserID
WHERE (dbo.LZ_MISDepPos.UG_UserGrpID <> 'UG050721000001')

--Messages
SELECT * FROM 
(SELECT TOP 10000 * FROM 
	(SELECT TOP 10000 dbo.Hp_Information.HI_ID AS [external id], 
		dbo.Hp_Information.HI_Title AS name, dbo.Hp_Information.HI_Content AS content, 
		dbo.Hp_Information.HI_ReadTimes AS [read times], 
		replace(CONVERT(varchar, 
				dbo.Hp_Information.HI_SetTime, 120),'/','-') AS create_date, 	
		replace(CONVERT(varchar, 
				dbo.Hp_Information.HI_SetTime, 120),'/','-') AS write_date, 
		replace(CONVERT(varchar, 
				dbo.Hp_Information.HI_OverTime, 111),'/','-') AS expire_date, 
		'USR_'+dbo.Hp_Information.HU_UserID AS [Author / external id], 
		'USR_'+dbo.Hp_Information.HU_UserID AS [Last Contributor / external id], 
		dbo.Hp_Information.HI_DisName AS [Display name?], 
		dbo.HP_Module.HM_id AS [Category/external id], 
		SZGH_OA_20050823.dbo.p_systemuser.UserGrpID AS [department/external id], 
		dbo.Hp_Information.HI_FBBM AS Publisher 
		FROM dbo.Hp_Information INNER JOIN
		dbo.HP_Module ON dbo.Hp_Information.HM_ID = dbo.HP_Module.HM_ID INNER JOIN
		SZGH_OA_20050823.dbo.p_systemuser ON 
		dbo.Hp_Information.HU_UserID = SZGH_OA_20050823.dbo.p_systemuser.SU_UserID ORDER BY dbo.Hp_Information.HI_SetTime ASC
) AS aSysTable ORDER BY aSysTable.[create_date] DESC) as bSysTable ORDER BY bSysTable.[create_date] ASC;

--Message comments
SELECT 
'comment' as type,
'message.message' as model,
HC_ID as external_id,
HI_ID as legacy_message_id,
HC_Comment as body,
HC_CreateTime as [Date],
RU_UserId as [Author/external_id],
~DisName as is_anonymous
FROM HP_InfoComment
WHERE HI_ID in 
(SELECT TOP 10000 dbo.Hp_Information.HI_ID  
	FROM dbo.Hp_Information INNER JOIN
	dbo.HP_Module ON dbo.Hp_Information.HM_ID = dbo.HP_Module.HM_ID INNER JOIN
	SZGH_OA_20050823.dbo.p_systemuser ON 
	dbo.Hp_Information.HU_UserID = SZGH_OA_20050823.dbo.p_systemuser.SU_UserID ORDER BY dbo.Hp_Information.HI_SetTime DESC
);

--Message catgories
SELECT HM_ID AS [external id], HM_Name AS name, 
      case when HM_Disname=1 then 0 else 1 end AS is_anonymous_allowed
FROM dbo.HP_Module
