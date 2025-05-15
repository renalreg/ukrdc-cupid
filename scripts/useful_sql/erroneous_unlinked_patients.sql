-- The new paradigm where the ukrdc is the single source of truth begs the question 
-- are there patients with different ukrdcid and the same nhs number
-- this query returns such people 
with multiple_nhs as (
	select A.id as id_1, A.pid as pid_1,B.id as id_2, B.pid as pid_2, A.patientid
	from patientnumber A 
	inner join patientnumber B
	on A.patientid = B.patientid
	where A.organization in ('NHS', 'CHI', 'HSC') 
	and B.organization in ('NHS', 'CHI', 'HSC')
	and A.numbertype = 'NI'
	and B.numbertype = 'NI'
	and A.pid <> B.pid
	order by A.patientid
)
--select * from multiple_nhs limit(100);
select A.id_1, A.id_2, A.pid_1, A.pid_2, B.ukrdcid as ukrdcid_1, C.ukrdcid as ukrdcid_2, A.patientid from multiple_nhs A 
inner join patientrecord B 
on A.pid_1 = B.pid
inner join patientrecord C 
on A.pid_2 = C.pid
where B.ukrdcid <> C.ukrdcid
and B.sendingextract = 'UKRDC' 
and C.sendingextract = 'UKRDC'
limit(100)

-- pretty much same as above
with multiple_nhs as (
	select A.id as id_1, A.pid as pid_1,B.id as id_2, B.pid as pid_2, A.patientid
	from patientnumber A 
	inner join patientnumber B
	on A.patientid = B.patientid
	where A.organization in ('NHS', 'CHI', 'HSC') 
	and B.organization in ('NHS', 'CHI', 'HSC')
	and A.numbertype = 'NI'
	and B.numbertype = 'NI'
	and A.pid <> B.pid
	order by A.patientid
)
select patientid from multiple_nhs A
inner join patientrecord B 
on A.pid_1 = B.pid
inner join patientrecord C 
on A.pid_2 = C.pid
where B.ukrdcid <> C.ukrdcid
and B.sendingextract = 'UKRDC' 
and C.sendingextract = 'UKRDC'
group by patientid 

-- these records have the same nhs number and different names and ukrdcids
with nhs_names as (
	select A.pid as pid_1, B.pid as pid_2, E.ukrdcid as ukrdcid_1, F.ukrdcid as ukrdcid_2, lower(C.family) as family_1,lower(D.family) as family_2, lower(C.given) as given_1, lower(D.given) as given_2, B.patientid as nhs_no  from  patientnumber A
	inner join patientnumber B 
	on A.patientid = B.patientid
	inner join name C on A.pid = C.pid
	inner join name D on B.pid = D.pid 
	inner join patientrecord E on E.pid = A.pid
	inner join patientrecord F on F.pid = B.pid 
	where E.ukrdcid <> F.ukrdcid
	and lower(C.family) <> lower(D.family)
	order by nhs_no
)

select distinct * from nhs_names order by nhs_no




with combined_demog as (
select 
    A.pid, 
    A.ukrdcid, 
    A.sendingextract, 
    A.sendingfacility,
    B.given, 
    B.family,
    C.birthtime, 
    C.deathtime,
    C.gender
from patientrecord A
inner join name B on B.pid = A.pid
inner join patient C on C.pid = A.pid
)
select 
    A.ukrdcid, 
    A.given as given_A,
    B.given as given_B,
    A.family as family_A,
    B.family as family_B,
    A.birthtime as birthtime_A, 
    B.birthtime as birthtime_B,
	A.sendingextract,
	B.sendingextract, 
	A.sendingfacility,
	B.sendingfacility
from combined_demog A 
inner join combined_demog B
on A.ukrdcid = B.ukrdcid 
and A.pid <> B.pid -- Ensure not comparing the same record--
where (UPPER(A.given) <> UPPER(B.given) or UPPER(A.family) <> UPPER(B.family))
and (UPPER(A.given) <> UPPER(B.family) or UPPER(A.family) <> UPPER(B.given))
and ABS(EXTRACT(EPOCH FROM A.birthtime - B.birthtime)) > 86400;