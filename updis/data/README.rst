Introduction
============

bin\mongoimport.exe --journal -d updis -c message_categories -f _id,name,is_anonymous_allowed --type csv --drop --headerline --upsert --file "c:\Users\Zhou Guangwen\PycharmProjects\oeaddon\updis\data\message_categories.csv"
bin\mongoimport.exe --journal -d updis -c departments -f _id,name,deleted --type csv --drop --headerline --upsert --file "c:\Users\Zhou Guangwen\PycharmProjects\oeaddon\updis\data\department.csv"
bin\mongoimport.exe --journal -d updis -c employees -f _id,External_Id,name,active,work_location,home_phone,mobile_phone,work_phone,work_email,gender,birthday,folk,native_place,notes,diploma,degree,academy,begin_work_date,enter_date,contract_date,aptitude,major,year_vac_days,have_vac_days,insurance,awards,study_list,interest,practice,go_abroad_list,join_ploy,strong_point,business,business_date,duty,duty_date,title,title_date,reg_tax,reg_tax_date,reg_tax_no,gra_date,out_date,job_id,department_id --type csv --drop --headerline --upsert --file "c:\Users\Zhou Guangwen\PycharmProjects\oeaddon\updis\data\employees.csv"
