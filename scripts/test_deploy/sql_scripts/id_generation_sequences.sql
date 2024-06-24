CREATE SEQUENCE generate_new_pid
    START 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE;

SELECT setval('generate_new_pid', (SELECT COALESCE(MAX(pid)::integer, 0) + 1 FROM patientrecord));

COMMENT ON SEQUENCE public.generate_new_pid
    IS 'Sequence to generate new pids should be initiated as the maxiumum pid';

CREATE SEQUENCE generate_new_ukrdcid
    START 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE;

SELECT setval('generate_new_ukrdcid', (SELECT COALESCE(MAX(ukrdcid)::integer, 0) + 1 FROM patientrecord));

COMMENT ON SEQUENCE public.generate_new_pid
    IS 'Sequence mints new ukrdcids';