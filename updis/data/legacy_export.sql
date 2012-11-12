--Non active employee
SELECT dbo.LZ_MISUser.SU_UserID AS legacyID, 
      dbo.LZ_MISUser.SU_UserID AS 'External Id', 
      dbo.LZ_MISUser.SU_UserName AS name, dbo.LZ_MISUser.SU_LoginName AS login, 
      0 AS active, dbo.LZ_MisUserAddressBook.SU_EmpAddr AS work_location, 
      dbo.LZ_MisUserAddressBook.SU_EmpHmTel AS home_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpMobile AS home_mobile, 
      dbo.LZ_MisUserAddressBook.SU_EmpComTel AS mobile_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpEAddr AS work_email, 
      dbo.LZ_MISUserInfo.SU_Sex AS gender, CONVERT(DATETIME, 
      dbo.LZ_MISUserInfo.SU_Birthday, 112) AS birthday, 
      dbo.LZ_MISUserInfo.SU_Folk AS folk, dbo.LZ_MISUserInfo.SU_Bio AS notes, 
      dbo.LZ_MISUserInfo.SU_Diploma AS diploma, 
      dbo.LZ_MISUserInfo.SU_Degree AS degree, 
      dbo.LZ_MISUserInfo.SU_Academy AS academy, 
      dbo.LZ_MISUserInfo.SU_Speciality AS major
FROM dbo.LZ_MISUser INNER JOIN
      dbo.LZ_MisUserAddressBook ON 
      dbo.LZ_MISUser.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISUserInfo ON 
      dbo.LZ_MISUserInfo.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID
WHERE (dbo.LZ_MISUser.SU_IsDel = 1) AND 
      (dbo.LZ_MISUser.SU_LoginName <> 'admin')

--active employee
SELECT dbo.LZ_MISUser.SU_UserID AS legacyID, 
      dbo.LZ_MISUser.SU_UserID AS 'External Id', 
      dbo.LZ_MISUser.SU_UserName AS name, dbo.LZ_MISUser.SU_LoginName AS login, 
      1 AS active, dbo.LZ_MisUserAddressBook.SU_EmpAddr AS work_location, 
      dbo.LZ_MisUserAddressBook.SU_EmpHmTel AS home_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpMobile AS home_mobile, 
      dbo.LZ_MisUserAddressBook.SU_EmpComTel AS mobile_phone, 
      dbo.LZ_MisUserAddressBook.SU_EmpEAddr AS work_email, 
      dbo.LZ_MISUserInfo.SU_Sex AS gender, CONVERT(DATETIME, 
      dbo.LZ_MISUserInfo.SU_Birthday, 112) AS birthday, 
      dbo.LZ_MISUserInfo.SU_Folk AS folk, dbo.LZ_MISUserInfo.SU_Bio AS notes, 
      dbo.LZ_MISUserInfo.SU_Diploma AS diploma, 
      dbo.LZ_MISUserInfo.SU_Degree AS degree, 
      dbo.LZ_MISUserInfo.SU_Academy AS academy, 
      dbo.LZ_MISUserInfo.SU_Speciality AS major
FROM dbo.LZ_MISUser INNER JOIN
      dbo.LZ_MisUserAddressBook ON 
      dbo.LZ_MISUser.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID INNER JOIN
      dbo.LZ_MISUserInfo ON 
      dbo.LZ_MISUserInfo.SU_UserID = dbo.LZ_MisUserAddressBook.SU_UserID
WHERE (dbo.LZ_MISUser.SU_IsDel = 0) AND 
      (dbo.LZ_MISUser.SU_LoginName <> 'admin')

--department
SELECT UG_UserGrpID AS [external id], UG_UserGrpName AS name, 
      UG_IsDel AS deleted
FROM dbo.LZ_MISDepartment

--position
SELECT PI_PosId AS [external id], PI_PosName AS name, Remark AS description
FROM dbo.LZ_MISPosInfo

--user position and department
SELECT dbo.LZ_MISDepPosUser.SU_UserID AS [external id], 
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
SELECT TOP 1000 dbo.Hp_Information.HI_ID AS [external id], dbo.Hp_Information.HI_Title AS name, 
      dbo.Hp_Information.HI_Content AS content, 
      dbo.Hp_Information.HI_ReadTimes AS [read times], 
      dbo.Hp_Information.HU_UserID AS [Author / external id], 
      dbo.Hp_Information.HI_DisName AS [Display name?], 
      dbo.HP_Module.HM_Name AS Category
FROM dbo.Hp_Information INNER JOIN
      dbo.HP_Module ON dbo.Hp_Information.HM_ID = dbo.HP_Module.HM_ID
ORDER BY Category

--Message catgories
SELECT 'category' as Type, HM_ID AS [external id], HM_Name AS name, 
      HM_Disname AS display_name
FROM dbo.HP_Module
