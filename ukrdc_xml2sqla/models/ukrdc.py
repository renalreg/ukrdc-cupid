"""
WIP: VERY WORK IN PROGRESS

THE PLAN:

-   For each xsdata class, create a class which accepts 
    a single instance of that xsdata class as an argument.
-   Each of these will include a to_orm() method which returns an
    instance of the corresponding ORM class.
-   These ORM objects will not include any keys like pid or id.
-   The top-level PatientRecord class will cascade the to_orm() method
    to all of its child objects.
-   We then have a separate method, equivalent to the Java store() method
    which will take a PatientRecord object, generate/cascade all keys, merge
    with any existing data, and save it to the database.
"""

from typing import Optional

import ukrdc_sqla.ukrdc as orm
import ukrdc_xsdata.ukrdc.types as xsd_types
import ukrdc_xsdata.ukrdc as xsd_ukrdc
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders
import ukrdc_xsdata.ukrdc.social_histories as xsd_social_history
import ukrdc_xsdata.ukrdc.family_histories as xsd_family_history
import ukrdc_xsdata.ukrdc.allergies as xsd_allergy
import ukrdc_xsdata.ukrdc.diagnoses as xsd_diagnosis
import ukrdc_xsdata.ukrdc.medications as xsd_medication
import ukrdc_xsdata.ukrdc.procedures as xsd_procedure
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_session
import ukrdc_xsdata.ukrdc.transplants as xsd_transplants
import ukrdc_xsdata.ukrdc.vascular_accesses as xsd_vascular_accesses
import ukrdc_xsdata.ukrdc.encounters as xsd_encounters
import ukrdc_xsdata.ukrdc.program_memberships as xsd_program_memberships
import ukrdc_xsdata.ukrdc.opt_outs as xsd_opt_outs
import ukrdc_xsdata.ukrdc.clinical_relationships as xsd_clinical_relationships
import ukrdc_xsdata.ukrdc.surveys as xsd_surveys
import ukrdc_xsdata.ukrdc.documents as xsd_documents
import ukrdc_xsdata.pv.pv_2_0 as xsd_pvdata

# import ukrdc_xsdata.pv.pv_2_0


class DialysisSession:
    def __init__(self, dialysis_session: xsd_dialysis_session.DialysisSession) -> None:
        self.dialysis_session = dialysis_session

    def to_orm(self) -> orm.DialysisSession:
        dialysis_session = orm.DialysisSession()

        # Basic columns

        dialysis_session.externalid = self.dialysis_session.external_id

        if self.dialysis_session.procedure_time:
            dialysis_session.proceduretime = self.dialysis_session.procedure_time.to_datetime()

        if self.dialysis_session.updated_on:
            dialysis_session.updatedon = self.dialysis_session.updated_on.to_datetime()

        if self.dialysis_session.procedure_type:
            dialysis_session.proceduretypecode = self.dialysis_session.procedure_type.code
            dialysis_session.proceduretypecodestd = self.dialysis_session.procedure_type.coding_standard
            dialysis_session.proceduretypedesc = self.dialysis_session.procedure_type.description

        if self.dialysis_session.clinician:
            dialysis_session.cliniciancode = self.dialysis_session.clinician.code
            dialysis_session.cliniciancodestd = self.dialysis_session.clinician.coding_standard
            dialysis_session.cliniciandesc = self.dialysis_session.clinician.description

        if self.dialysis_session.entered_by:
            dialysis_session.enteredbycode = self.dialysis_session.entered_by.code
            dialysis_session.enteredbycodestd = self.dialysis_session.entered_by.coding_standard
            dialysis_session.enteredbydesc = self.dialysis_session.entered_by.description

        if self.dialysis_session.entered_at:
            dialysis_session.enteredatcode = self.dialysis_session.entered_at.code
            dialysis_session.enteredatcodestd = self.dialysis_session.entered_at.coding_standard
            dialysis_session.enteredatdesc = self.dialysis_session.entered_at.description

        if self.dialysis_session.attributes:
            dialysis_session.qhd19 = self.dialysis_session.attributes.qhd19
            dialysis_session.qhd20 = self.dialysis_session.attributes.qhd20
            dialysis_session.qhd21 = self.dialysis_session.attributes.qhd21
            dialysis_session.qhd22 = self.dialysis_session.attributes.qhd22
            dialysis_session.qhd30 = self.dialysis_session.attributes.qhd30
            dialysis_session.qhd31 = self.dialysis_session.attributes.qhd31
            dialysis_session.qhd32 = self.dialysis_session.attributes.qhd32
            dialysis_session.qhd33 = self.dialysis_session.attributes.qhd33

        return dialysis_session


class Procedure:
    def __init__(self, procedure: xsd_procedure.Procedure) -> None:
        self.procedure = procedure

    def to_orm(self) -> orm.Procedure:
        procedure = orm.Procedure()

        # Basic columns

        procedure.externalid = self.procedure.external_id

        if self.procedure.procedure_time:
            procedure.proceduretime = self.procedure.procedure_time.to_datetime()

        if self.procedure.updated_on:
            procedure.updatedon = self.procedure.updated_on.to_datetime()

        if self.procedure.procedure_type:
            procedure.proceduretypecode = self.procedure.procedure_type.code
            procedure.proceduretypecodestd = self.procedure.procedure_type.coding_standard
            procedure.proceduretypedesc = self.procedure.procedure_type.description

        if self.procedure.clinician:
            procedure.cliniciancode = self.procedure.clinician.code
            procedure.cliniciancodestd = self.procedure.clinician.coding_standard
            procedure.cliniciandesc = self.procedure.clinician.description

        if self.procedure.entered_by:
            procedure.enteredbycode = self.procedure.entered_by.code
            procedure.enteredbycodestd = self.procedure.entered_by.coding_standard
            procedure.enteredbydesc = self.procedure.entered_by.description

        if self.procedure.entered_at:
            procedure.enteredatcode = self.procedure.entered_at.code
            procedure.enteredatcodestd = self.procedure.entered_at.coding_standard
            procedure.enteredatdesc = self.procedure.entered_at.description

        return procedure


class Medication:
    def __init__(self, medication: xsd_medication.Medication) -> None:
        self.medication = medication

    def to_orm(self) -> orm.Medication:
        medication = orm.Medication()

        # Basic columns

        medication.prescriptionnumber = self.medication.prescription_number
        medication.frequency = self.medication.frequency
        medication.commenttext = self.medication.comments
        medication.dosequantity = self.medication.dose_quantity
        medication.indication = self.medication.indication
        medication.encounternumber = self.medication.encounter_number
        medication.externalid = self.medication.external_id

        if self.medication.updated_on:
            medication.updatedon = self.medication.updated_on.to_datetime()
        if self.medication.from_time:
            medication.fromtime = self.medication.from_time.to_datetime()
        if self.medication.to_time:
            medication.totime = self.medication.to_time.to_datetime()

        if self.medication.ordered_by:
            medication.orderedbycode = self.medication.ordered_by.code
            medication.orderedbycodestd = self.medication.ordered_by.coding_standard
            medication.orderedbydesc = self.medication.ordered_by.description

        if self.medication.entering_organization:
            medication.enteringorganizationcode = self.medication.entering_organization.code
            medication.enteringorganizationcodestd = self.medication.entering_organization.coding_standard
            medication.enteringorganizationdesc = self.medication.entering_organization.description

        if self.medication.route:
            medication.routecode = self.medication.route.code
            medication.routecodestd = self.medication.route.coding_standard
            medication.routedesc = self.medication.route.description

        if self.medication.drug_product:
            if self.medication.drug_product.id:
                medication.drugproductidcode = self.medication.drug_product.id.code
                medication.drugproductidcodestd = self.medication.drug_product.id.coding_standard
                medication.drugproductiddesc = self.medication.drug_product.id.description
            if self.medication.drug_product.generic:
                medication.drugproductgeneric = self.medication.drug_product.generic
            if self.medication.drug_product.label_name:
                medication.drugproductlabelname = self.medication.drug_product.label_name
            if self.medication.drug_product.form:
                medication.drugproductformcode = self.medication.drug_product.form.code
                medication.drugproductformcodestd = self.medication.drug_product.form.coding_standard
                medication.drugproductformdesc = self.medication.drug_product.form.description
            if self.medication.drug_product.strength_units:
                medication.drugproductstrengthunitscode = self.medication.drug_product.strength_units.code
                medication.drugproductstrengthunitscodestd = self.medication.drug_product.strength_units.coding_standard
                medication.drugproductstrengthunitsdesc = self.medication.drug_product.strength_units.description

        if self.medication.dose_uo_m:
            medication.doseuomcode = self.medication.dose_uo_m.code
            medication.doseuomcodestd = self.medication.dose_uo_m.coding_standard
            medication.doseuomdesc = self.medication.dose_uo_m.description

        return medication


class RenalDiagnosis:
    def __init__(self, renal_diagnosis: xsd_diagnosis.RenalDiagnosis) -> None:
        self.renal_diagnosis = renal_diagnosis

    def to_orm(self) -> orm.RenalDiagnosis:
        renal_diagnosis = orm.RenalDiagnosis()

        # Basic columns

        renal_diagnosis.diagnosistype = self.renal_diagnosis.diagnosis_type
        renal_diagnosis.comments = self.renal_diagnosis.comments
        renal_diagnosis.externalid = self.renal_diagnosis.external_id

        if self.renal_diagnosis.identification_time:
            renal_diagnosis.identificationtime = self.renal_diagnosis.identification_time.to_datetime()
        if self.renal_diagnosis.onset_time:
            renal_diagnosis.onsettime = self.renal_diagnosis.onset_time.to_datetime()
        if self.renal_diagnosis.entered_on:
            renal_diagnosis.enteredon = self.renal_diagnosis.entered_on.to_datetime()
        if self.renal_diagnosis.updated_on:
            renal_diagnosis.updatedon = self.renal_diagnosis.updated_on.to_datetime()

        if self.renal_diagnosis.diagnosing_clinician:
            renal_diagnosis.diagnosingcliniciancode = self.renal_diagnosis.diagnosing_clinician.code
            renal_diagnosis.diagnosingcliniciancodestd = self.renal_diagnosis.diagnosing_clinician.coding_standard
            renal_diagnosis.diagnosingcliniciandesc = self.renal_diagnosis.diagnosing_clinician.description

        if self.renal_diagnosis.diagnosis:
            renal_diagnosis.diagnosiscode = self.renal_diagnosis.diagnosis.code
            renal_diagnosis.diagnosiscodestd = self.renal_diagnosis.diagnosis.coding_standard
            renal_diagnosis.diagnosisdesc = self.renal_diagnosis.diagnosis.description

        return renal_diagnosis


class CauseOfDeath:
    def __init__(self, cause_of_death: xsd_diagnosis.CauseOfDeath) -> None:
        self.cause_of_death = cause_of_death

    def to_orm(self) -> orm.CauseOfDeath:
        cause_of_death = orm.CauseOfDeath()

        # Basic columns

        cause_of_death.diagnosistype = self.cause_of_death.diagnosis_type
        cause_of_death.comments = self.cause_of_death.comments
        cause_of_death.externalid = self.cause_of_death.external_id

        if self.cause_of_death.entered_on:
            cause_of_death.enteredon = self.cause_of_death.entered_on.to_datetime()
        if self.cause_of_death.updated_on:
            cause_of_death.updatedon = self.cause_of_death.updated_on.to_datetime()

        if self.cause_of_death.diagnosing_clinician:
            cause_of_death.diagnosingcliniciancode = self.cause_of_death.diagnosing_clinician.code
            cause_of_death.diagnosingcliniciancodestd = self.cause_of_death.diagnosing_clinician.coding_standard
            cause_of_death.diagnosingcliniciandesc = self.cause_of_death.diagnosing_clinician.description

        if self.cause_of_death.diagnosis:
            cause_of_death.diagnosiscode = self.cause_of_death.diagnosis.code
            cause_of_death.diagnosiscodestd = self.cause_of_death.diagnosis.coding_standard
            cause_of_death.diagnosisdesc = self.cause_of_death.diagnosis.description

        return cause_of_death


class Diagnosis:
    def __init__(self, diagnosis: xsd_diagnosis.Diagnosis) -> None:
        self.diagnosis = diagnosis

    def to_orm(self) -> orm.Diagnosis:
        diagnosis = orm.Diagnosis()

        # Basic columns

        diagnosis.diagnosistype = self.diagnosis.diagnosis_type
        diagnosis.comments = self.diagnosis.comments
        diagnosis.encounternumber = self.diagnosis.encounter_number
        diagnosis.externalid = self.diagnosis.external_id

        if self.diagnosis.identification_time:
            diagnosis.identificationtime = self.diagnosis.identification_time.to_datetime()
        if self.diagnosis.onset_time:
            diagnosis.onsettime = self.diagnosis.onset_time.to_datetime()
        if self.diagnosis.entered_on:
            diagnosis.enteredon = self.diagnosis.entered_on.to_datetime()
        if self.diagnosis.updated_on:
            diagnosis.updatedon = self.diagnosis.updated_on.to_datetime()

        if self.diagnosis.verification_status:
            diagnosis.verificationstatus = self.diagnosis.verification_status.value

        if self.diagnosis.diagnosing_clinician:
            diagnosis.diagnosingcliniciancode = self.diagnosis.diagnosing_clinician.code
            diagnosis.diagnosingcliniciancodestd = self.diagnosis.diagnosing_clinician.coding_standard
            diagnosis.diagnosingcliniciandesc = self.diagnosis.diagnosing_clinician.description

        if self.diagnosis.diagnosis:
            diagnosis.diagnosiscode = self.diagnosis.diagnosis.code
            diagnosis.diagnosiscodestd = self.diagnosis.diagnosis.coding_standard
            diagnosis.diagnosisdesc = self.diagnosis.diagnosis.description

        if self.diagnosis.entered_at:
            diagnosis.enteredatcode = self.diagnosis.entered_at.code
            diagnosis.enteredatcodestd = self.diagnosis.entered_at.coding_standard
            diagnosis.enteredatdesc = self.diagnosis.entered_at.description

        return diagnosis


class Allergy:
    def __init__(self, allergy: xsd_allergy.Allergy) -> None:
        self.allergy = allergy

    def to_orm(self) -> orm.Allergy:
        allergy = orm.Allergy()

        # Basic columns

        if self.allergy.discovery_time:
            allergy.discoverytime = self.allergy.discovery_time.to_datetime()
        if self.allergy.confirmed_time:
            allergy.confirmedtime = self.allergy.confirmed_time.to_datetime()
        if self.allergy.inactive_time:
            allergy.inactivetime = self.allergy.inactive_time.to_datetime()

        allergy.commenttext = self.allergy.comments
        allergy.freetextallergy = self.allergy.free_text_allergy
        allergy.qualifyingdetails = self.allergy.qualifying_details
        allergy.updatedon = self.allergy.updated_on
        allergy.externalid = self.allergy.external_id

        if self.allergy.allergy:
            allergy.allergycode = self.allergy.allergy.code
            allergy.allergycodestd = self.allergy.allergy.coding_standard
            allergy.allergydesc = self.allergy.allergy.description

        if self.allergy.allergy_category:
            allergy.allergycategorycode = self.allergy.allergy_category.code
            allergy.allergycategorycodestd = self.allergy.allergy_category.coding_standard
            allergy.allergycategorydesc = self.allergy.allergy_category.description

        if self.allergy.severity:
            allergy.severitycode = self.allergy.severity.code
            allergy.severitycodestd = self.allergy.severity.coding_standard
            allergy.severitydesc = self.allergy.severity.description

        if self.allergy.clinician:
            allergy.cliniciancode = self.allergy.clinician.code
            allergy.cliniciancodestd = self.allergy.clinician.coding_standard
            allergy.cliniciandesc = self.allergy.clinician.description

        return allergy


class FamilyHistory:
    def __init__(self, family_history: xsd_family_history.FamilyHistory):
        self.family_history = family_history

    def to_orm(self) -> orm.FamilyHistory:
        history = orm.FamilyHistory()

        # Basic columns

        history.notetext = self.family_history.note_text
        history.fromtime = self.family_history.from_time
        history.totime = self.family_history.to_time
        history.updatedon = self.family_history.updated_on
        history.externalid = self.family_history.external_id

        if self.family_history.family_member:
            history.familymembercode = self.family_history.family_member.code
            history.familymembercodestd = self.family_history.family_member.coding_standard
            history.familymemberdesc = self.family_history.family_member.description

        if self.family_history.diagnosis:
            history.diagnosiscode = self.family_history.diagnosis.code
            history.diagnosiscodestd = self.family_history.diagnosis.coding_standard
            history.diagnosisdesc = self.family_history.diagnosis.description

        if self.family_history.entered_at:
            history.enteredatcode = self.family_history.entered_at.code
            history.enteredatcodestd = self.family_history.entered_at.coding_standard
            history.enteredatdesc = self.family_history.entered_at.description

        return history


class SocialHistory:
    def __init__(self, social_history: xsd_social_history.SocialHistory):
        self.social_history = social_history

    def to_orm(self) -> orm.SocialHistory:
        history = orm.SocialHistory()

        # Basic columns
        history.updatedon = self.social_history.updated_on
        history.externalid = self.social_history.external_id

        if self.social_history.social_habit:
            history.socialhabitcode = self.social_history.social_habit.code
            history.socialhabitcodestd = self.social_history.social_habit.coding_standard
            history.socialhabitdesc = self.social_history.social_habit.description

        return history


class ResultItem:
    def __init__(self, result_item: xsd_lab_orders.ResultItem):
        self.result_item = result_item

    def to_orm(self) -> orm.ResultItem:
        result = orm.ResultItem()

        # Basic columns

        if self.result_item.pre_post:
            result.prepost = self.result_item.pre_post.value
        if self.result_item.interpretation_codes:
            result.interpretationcodes = self.result_item.interpretation_codes.value
        if self.result_item.status:
            result.status = self.result_item.status.value if self.result_item.status else None

        result.resulttype = self.result_item.result_type
        result.enteredon = self.result_item.entered_on
        result.subid = self.result_item.sub_id
        result.resultvalue = self.result_item.result_value
        result.resultvalueunits = self.result_item.result_value_units
        result.referencerange = self.result_item.reference_range
        result.observationtime = self.result_item.observation_time
        result.commenttext = self.result_item.comments
        result.referencecomment = self.result_item.reference_comment

        if self.result_item.service_id:
            result.serviceidcode = self.result_item.service_id.code
            result.serviceidcodestd = self.result_item.service_id.coding_standard
            result.serviceiddesc = self.result_item.service_id.description

        return result


class LabOrder:
    def __init__(self, laborder: xsd_lab_orders.LabOrder):
        self.laborder = laborder

    def to_orm(self) -> orm.LabOrder:
        order = orm.LabOrder()

        # Basic columns

        order.placerid = self.laborder.placer_id
        order.fillerid = self.laborder.filler_id
        order.specimencollectedtime = self.laborder.specimen_collected_time
        order.specimenreceivedtime = self.laborder.specimen_received_time
        order.status = self.laborder.status
        order.specimensource = self.laborder.specimen_source
        order.duration = self.laborder.duration
        order.enteredon = self.laborder.entered_on
        order.updatedon = self.laborder.updated_on
        order.externalid = self.laborder.external_id

        if self.laborder.receiving_location:
            order.receivinglocationcode = self.laborder.receiving_location.code
            order.receivinglocationdesc = self.laborder.receiving_location.description
            order.receivinglocationcodestd = self.laborder.receiving_location.coding_standard

        if self.laborder.ordered_by:
            order.orderedbycode = self.laborder.ordered_by.code
            order.orderedbydesc = self.laborder.ordered_by.description
            order.orderedbycodestd = self.laborder.ordered_by.coding_standard

        if self.laborder.order_item:
            order.orderitemcode = self.laborder.order_item.code
            order.orderitemdesc = self.laborder.order_item.description
            order.orderitemcodestd = self.laborder.order_item.coding_standard

        if self.laborder.order_category:
            order.ordercategorycode = self.laborder.order_category.code
            order.ordercategorydesc = self.laborder.order_category.description
            order.ordercategorycodestd = self.laborder.order_category.coding_standard

        if self.laborder.priority:
            order.prioritycode = self.laborder.priority.code
            order.prioritydesc = self.laborder.priority.description
            order.prioritycodestd = self.laborder.priority.coding_standard

        if self.laborder.patient_class:
            order.patientclasscode = self.laborder.patient_class.code
            order.patientclassdesc = self.laborder.patient_class.description
            order.patientclasscodestd = self.laborder.patient_class.coding_standard

        if self.laborder.entered_at:
            order.enteredatcode = self.laborder.entered_at.code
            order.enteredatdesc = self.laborder.entered_at.description
            order.enteredatcodestd = self.laborder.entered_at.coding_standard

        if self.laborder.entering_organization:
            order.enteringorganizationcode = self.laborder.entering_organization.code
            order.enteringorganizationdesc = self.laborder.entering_organization.description
            order.enteringorganizationcodestd = self.laborder.entering_organization.coding_standard

        # Relationships

        if self.laborder.result_items:
            order.result_items = [ResultItem(item).to_orm() for item in self.laborder.result_items.result_item]

        return order


class FamilyDoctor:
    def __init__(self, family_doctor: xsd_types.FamilyDoctor):
        self.family_doctor = family_doctor

    def to_orm(self) -> orm.FamilyDoctor:
        doctor = orm.FamilyDoctor()

        doctor.gpname = self.family_doctor.gpname
        doctor.gpid = self.family_doctor.gpid
        doctor.gppracticeid = self.family_doctor.gppractice_id

        doctor.email = self.family_doctor.email

        if self.family_doctor.address:
            doctor.addressuse = self.family_doctor.address.use
            doctor.fromtime = self.family_doctor.address.from_time
            doctor.totime = self.family_doctor.address.to_time
            doctor.street = self.family_doctor.address.street
            doctor.town = self.family_doctor.address.town
            doctor.county = self.family_doctor.address.county
            doctor.postcode = self.family_doctor.address.postcode

            if self.family_doctor.address.country:
                doctor.countrycode = self.family_doctor.address.country.code
                doctor.countrycodestd = self.family_doctor.address.country.coding_standard
                doctor.countrydesc = self.family_doctor.address.country.description

        if self.family_doctor.contact_detail:
            doctor.contactuse = self.family_doctor.contact_detail.use
            doctor.contactvalue = self.family_doctor.contact_detail.value
            doctor.commenttext = self.family_doctor.contact_detail.comments

        return doctor


class Address:
    def __init__(self, address: xsd_types.Address):
        self.address = address

    def to_orm(self) -> orm.Address:
        address = orm.Address()

        address.addressuse = self.address.use
        address.fromtime = self.address.from_time
        address.totime = self.address.to_time
        address.street = self.address.street
        address.town = self.address.town
        address.county = self.address.county
        address.postcode = self.address.postcode

        if self.address.country:
            address.countrycode = self.address.country.code
            address.countrycodestd = self.address.country.coding_standard
            address.countrydesc = self.address.country.description

        return address


class ContactDetail:
    def __init__(self, xsd_contact: xsd_types.ContactDetail):
        self.xsd_contact = xsd_contact

    def to_orm(self) -> orm.ContactDetail:
        detail = orm.ContactDetail()

        detail.contactuse = self.xsd_contact.use
        detail.contactvalue = self.xsd_contact.value
        detail.commenttext = self.xsd_contact.comments

        return detail


class Name:
    def __init__(self, xml: xsd_types.Name):
        self.xml = xml

    def to_orm(self):
        name = orm.Name()

        name.nameuse = self.xml.use
        name.prefix = self.xml.prefix
        name.family = self.xml.family
        name.given = self.xml.given
        name.othergivennames = self.xml.other_given_names
        name.suffix = self.xml.suffix

        return name


class PatientNumber:
    def __init__(self, xml: xsd_types.PatientNumber):
        self.xml = xml

    def to_orm(self):
        number = orm.PatientNumber()

        number.patientid = self.xml.number
        number.organization = self.xml.organization
        number.numbertype = self.xml.number_type

        return number


class Patient:
    def __init__(self, xml: xsd_ukrdc.Patient):
        self.xml = xml

    @property
    def _first_person_to_contact(self) -> Optional[xsd_types.ContactDetail]:
        if self.xml.person_to_contact and self.xml.person_to_contact.contact_details:
            return self.xml.person_to_contact.contact_details[0]
        return None

    def to_orm(self):
        patient = orm.Patient()

        # Basic columns

        patient.birthtime = self.xml.birth_time.to_datetime() if self.xml.birth_time else None
        patient.deathtime = self.xml.death_time.to_datetime() if self.xml.death_time else None

        patient.gender = self.xml.gender
        patient.countryofbirth = self.xml.country_of_birth

        if self.xml.ethnic_group:
            patient.ethnicgroupcode = self.xml.ethnic_group.code
            patient.ethnicgroupcodestd = self.xml.ethnic_group.coding_standard
            patient.ethnicgroupdesc = self.xml.ethnic_group.description

        if self.xml.person_to_contact:
            patient.persontocontactname = self.xml.person_to_contact.name
            patient.persontocontact_relationship = self.xml.person_to_contact.relationship

            if self.xml.person_to_contact.contact_details:
                patient.persontocontact_contactnumber = self.xml.person_to_contact.contact_details[0].value
                patient.persontocontact_contactnumbercomments = self.xml.person_to_contact.contact_details[0].comments
                patient.persontocontact_contactnumbertype = self.xml.person_to_contact.contact_details[0].use

        if self.xml.occupation:
            patient.occupationcode = self.xml.occupation.code
            patient.occupationcodestd = self.xml.occupation.coding_standard
            patient.occupationdesc = self.xml.occupation.description

        if self.xml.primary_language:
            patient.primarylanguagecode = self.xml.primary_language.code
            patient.primarylanguagecodestd = self.xml.primary_language.coding_standard
            patient.primarylanguagedesc = self.xml.primary_language.description

        patient.death = self.xml.death

        patient.updatedon = self.xml.updated_on.to_datetime() if self.xml.updated_on else None

        patient.bloodgroup = self.xml.blood_group
        patient.bloodrhesus = self.xml.blood_rhesus

        # Relationships

        if self.xml.patient_numbers:
            patient.numbers = [PatientNumber(number).to_orm() for number in self.xml.patient_numbers.patient_number]

        if self.xml.names:
            patient.names = [Name(name).to_orm() for name in self.xml.names.name]

        if self.xml.contact_details:
            patient.contact_details = [ContactDetail(contact).to_orm() for contact in self.xml.contact_details.contact_detail]

        if self.xml.addresses:
            patient.addresses = [Address(address).to_orm() for address in self.xml.addresses.address]

        if self.xml.family_doctor:
            patient.familydoctor = FamilyDoctor(self.xml.family_doctor).to_orm()

        return patient


class Transplant:
    def __init__(self, xml: xsd_transplants.TransplantProcedure):
        self.xml = xml

    def to_orm(self):
        transplant = orm.Transplant()
        if self.xml.procedure_type:
            transplant.proceduretypecode = self.xml.procedure_type.code
            transplant.proceduretypecodestd = self.xml.procedure_type.coding_standard
            transplant.proceduretypedesc = self.xml.procedure_type.description

        if self.xml.clinician:
            transplant.cliniciancode = self.xml.clinician.code
            transplant.cliniciancodestd = self.xml.clinician.coding_standard
            transplant.cliniciandesc = self.xml.clinician.description

        if self.xml.procedure_time:
            transplant.procedure_time = self.xml.procedure_time

        if self.xml.entered_by:
            transplant.enteredbycode = self.xml.entered_by.code
            transplant.enteredbycodestd = self.xml.entered_by.coding_standard
            transplant.enteredbydesc = self.xml.entered_by.description

        if self.xml.entered_at:
            transplant.enteredatcode = self.xml.entered_at.code
            transplant.enteredatcodestd = self.xml.entered_at.coding_standard
            transplant.enteredatdesc = self.xml.entered_at.description

        if self.xml.updated_on:
            transplant.updatedon = self.xml.updated_on

        # where is action code?

        if self.xml.external_id:
            transplant.externalid = self.xml.external_id

        if self.xml.Attributes:
            if self.xml.Attributes.tra64:
                transplant.tra64 = self.xml.Attributes.tra64

            if self.xml.Attributes.tra65:
                transplant.tra65 = self.xml.Attributes.tra65

            if self.xml.Attributes.tra66:
                transplant.tra66 = self.xml.Attributes.tra66

            if self.xml.Attributes.tra69:
                transplant.tra69 = self.xml.Attributes.tra69

            if self.xml.Attributes.tra76:
                transplant.tra76 = self.xml.Attributes.tra76

            if self.xml.Attributes.tra77:
                transplant.tra77 = self.xml.Attributes.tra77

            if self.xml.Attributes.tra78:
                transplant.tra78 = self.xml.Attributes.tra78

            if self.xml.Attributes.tra79:
                transplant.tra79 = self.xml.Attributes.tra79

            if self.xml.Attributes.tra80:
                transplant.tra80 = self.xml.Attributes.tra80

            if self.xml.Attributes.tra8_a:
                transplant.tra8a = self.xml.Attributes.tra8_a

            if self.xml.Attributes.tra81:
                transplant.tra81 = self.xml.Attributes.tra81

            if self.xml.Attributes.tra82:
                transplant.tra82 = self.xml.Attributes.tra82

            if self.xml.Attributes.tra83:
                transplant.tra83 = self.xml.Attributes.tra83

            if self.xml.Attributes.tra84:
                transplant.tra84 = self.xml.Attributes.tra84

            if self.xml.Attributes.tra85:
                transplant.tra85 = self.xml.Attributes.tra85

            if self.xml.Attributes.tra86:
                transplant.tra86 = self.xml.Attributes.tra86

            if self.xml.Attributes.tra87:
                transplant.tra87 = self.xml.Attributes.tra87

            if self.xml.Attributes.tra88:
                transplant.tra88 = self.xml.Attributes.tra88

            if self.xml.Attributes.tra89:
                transplant.tra89 = self.xml.Attributes.tra89

            if self.xml.Attributes.tra90:
                transplant.tra90 = self.xml.Attributes.tra90

            if self.xml.Attributes.tra91:
                transplant.tra91 = self.xml.Attributes.tra91

            if self.xml.Attributes.tra92:
                transplant.tra92 = self.xml.Attributes.tra92

            if self.xml.Attributes.tra93:
                transplant.tra93 = self.xml.Attributes.tra93

            if self.xml.Attributes.tra94:
                transplant.tra94 = self.xml.Attributes.tra94

            if self.xml.Attributes.tra95:
                transplant.tra95 = self.xml.Attributes.tra95

            if self.xml.Attributes.tra96:
                transplant.tra96 = self.xml.Attributes.tra96

            if self.xml.Attributes.tra97:
                transplant.tra97 = self.xml.Attributes.tra97

            if self.xml.Attributes.tra98:
                transplant.tra98 = self.xml.Attributes.tra98

        return transplant


class VascularAccess:
    def __init__(self, xml: xsd_vascular_accesses.VascularAccess):
        self.xml = xml

    def to_orm(self):
        vascular_access = orm.VascularAccess()

        if self.xml.procedure_type:
            vascular_access.proceduretypecode = self.xml.procedure_type.code
            vascular_access.proceduretypecodestd = self.xml.procedure_type.coding_standard
            vascular_access.proceduretypedesc = self.xml.procedure_type.description

        if self.xml.clinician:
            vascular_access.cliniciancode = self.xml.clinician.code
            vascular_access.cliniciancodestd = self.xml.clinician.coding_standard
            vascular_access.cliniciandesc = self.xml.clinician.description

        if self.xml.procedure_time:
            vascular_access.proceduretime = self.xml.procedure_time

        if self.xml.entered_by:
            vascular_access.enteredbycode = self.xml.entered_by.code
            vascular_access.enteredbycodestd = self.xml.entered_by.coding_standard
            vascular_access.enteredbydesc = self.xml.entered_by.description

        if self.xml.entered_at:
            vascular_access.enteredatcode = self.xml.entered_at.code
            vascular_access.enteredatcodestd = self.xml.entered_at.coding_standard
            vascular_access.enteredatdesc = self.xml.entered_at.description

        if self.xml.updated_on:
            vascular_access.updatedon = self.xml.updated_on

        if self.xml.external_id:
            vascular_access.externalid = self.xml.external_id

        if self.xml.Attributes:
            if self.xml.Attributes.acc19:
                vascular_access.acc19 = self.xml.Attributes.acc19

            if self.xml.Attributes.acc20:
                vascular_access.acc20 = self.xml.Attributes.acc20

            if self.xml.Attributes.acc21:
                vascular_access.acc21 = self.xml.Attributes.acc21

            if self.xml.Attributes.acc22:
                vascular_access.acc22 = self.xml.Attributes.acc22

            if self.xml.Attributes.acc30:
                vascular_access.acc30 = self.xml.Attributes.acc30

            if self.xml.Attributes.acc40:
                vascular_access.acc40 = self.xml.Attributes.acc40

        return vascular_access


class Encounter:
    def __init__(self, xml: xsd_encounters.Encounter):
        self.xml = xml

    def to_orm(self):
        encounter = orm.Encounter()
        if self.xml.encounter_number:
            encounter.encounternumber = self.xml.encounter_number
        if self.xml.encounter_type:
            encounter.encountertype = self.xml.encounter_type
        if self.xml.from_time:
            encounter.fromtime = self.xml.from_time
        if self.xml.to_time:
            encounter.totime = self.xml.to_time
        if self.xml.admitting_clinician:
            encounter.admittingcliniciancode = self.xml.admitting_clinician.code
            encounter.admittingcliniciancodestd = self.xml.admitting_clinician.coding_standard
            encounter.admissionsourcedesc = self.xml.admitting_clinician.description
        if self.xml.admit_reason:
            encounter.admitreasoncode = self.xml.admit_reason.code
            encounter.admitreasoncodestd = self.xml.admit_reason.coding_standard
            encounter.admitreasondesc = self.xml.admit_reason.description
        if self.xml.admission_source:
            encounter.admissionsourcecode = self.xml.admission_source.code
            encounter.admissionsourcecodestd = self.xml.admission_source.coding_standard
            encounter.admissionsourcedesc = self.xml.admission_source.description
        if self.xml.discharge_reason:
            encounter.dischargereasoncode = self.xml.discharge_reason.code
            encounter.dischargereasoncodestd = self.xml.discharge_reason.coding_standard
            encounter.dischargereasondesc = self.xml.discharge_reason.description
        if self.xml.discharge_location:
            encounter.dischargelocationcode = self.xml.discharge_location.code
            encounter.dischargereasoncodestd = self.xml.discharge_location.coding_standard
            encounter.dischargelocationdesc = self.xml.discharge_location.description
        if self.xml.health_care_facility:
            encounter.healthcarefacilitycode = self.xml.health_care_facility.code
            encounter.healthcarefacilitycodestd = self.xml.health_care_facility.coding_standard
            encounter.healthcarefacilitydesc = self.xml.health_care_facility.description
        if self.xml.entered_at:
            encounter.enteredatcode = self.xml.entered_at.code
            encounter.enteredatcodestd = self.xml.entered_at.coding_standard
            encounter.enteredatdesc = self.xml.entered_at.description
        if self.xml.visit_description:
            encounter.visitdescription = self.xml.visit_description
        if self.xml.updated_on:
            encounter.updatedon = self.xml.updated_on
        if self.xml.external_id:
            encounter.externalid = self.xml.external_id
        if self.xml.updated_on:
            encounter.update_date = self.xml.updated_on

        return encounter


class Treatment:
    def __init__(self, xml: xsd_encounters.Treatment):
        self.xml = xml

    def to_orm(self):
        treatment = orm.Treatment()
        if self.xml.encounter_number:
            treatment.encounternumber = self.xml.encounter_number
        if self.xml.encounter_type:
            treatment.encountertype = self.xml.encounter_type
        if self.xml.from_time:
            treatment.fromtime = self.xml.from_time
        if self.xml.to_time:
            treatment.totime = self.xml.to_time
        if self.xml.admitting_clinician:
            treatment.admittingcliniciancode = self.xml.admitting_clinician.code
            treatment.admittingcliniciancodestd = self.xml.admitting_clinician.coding_standard
            treatment.admittingcliniciandesc = self.xml.admitting_clinician.description
        if self.xml.admission_source:
            treatment.admissionsourcecode = self.xml.admission_source.code
            treatment.admissionsourcecodestd = self.xml.admission_source.coding_standard
            treatment.admissionsourcedesc = self.xml.admission_source.description
        if self.xml.discharge_reason:
            treatment.dischargereasoncode = self.xml.discharge_reason.code
            treatment.dischargereasoncodestd = self.xml.discharge_reason.coding_standard
            treatment.dischargereasondesc = self.xml.discharge_reason.description
        if self.xml.discharge_location:
            treatment.dischargelocationcode = self.xml.discharge_location.code
            treatment.dischargelocationcodestd = self.xml.discharge_location.coding_standard
            treatment.dischargelocationdesc = self.xml.discharge_location.description
        if self.xml.health_care_facility:
            treatment.healthcarefacilitycode = self.xml.health_care_facility.code
            treatment.healthcarefacilitycodestd = self.xml.health_care_facility.coding_standard
            treatment.healthcarefacilitydesc = self.xml.health_care_facility.description
        if self.xml.entered_at:
            treatment.enteredatcode = self.xml.entered_at.code
            treatment.enteredatcodestd = self.xml.entered_at.coding_standard
            treatment.enteredatdesc = self.xml.entered_at.description
        if self.xml.visit_description:
            treatment.visitdescription = self.xml.visit_description
        if self.xml.updated_on:
            treatment.updatedon = self.xml.updated_on
        if self.xml.external_id:
            treatment.externalid = self.xml.external_id
        if self.xml.Attributes:
            if self.xml.Attributes.hdp01:
                treatment.hdp01 = self.xml.Attributes.hdp01

            if self.xml.Attributes.hdp02:
                treatment.hdp02 = self.xml.Attributes.hdp02

            if self.xml.Attributes.hdp03:
                treatment.hdp03 = self.xml.Attributes.hdp03

            if self.xml.Attributes.hdp04:
                treatment.hdp04 = self.xml.Attributes.hdp04

            if self.xml.Attributes.qbl05:
                treatment.qbl05 = self.xml.Attributes.qbl05
            if self.xml.Attributes.qbl06:
                treatment.qbl06 = self.xml.Attributes.qbl06

            if self.xml.Attributes.qbl07:
                treatment.qbl07 = self.xml.Attributes.qbl07
            if self.xml.Attributes.erf61:
                treatment.erf61 = self.xml.Attributes.erf61
            if self.xml.Attributes.pat35:
                treatment.pat35 = self.xml.Attributes.pat35

        return treatment


class TransplantList:
    def __init__(self, xml: xsd_encounters.TransplantList):
        self.xml = xml

    def to_orm(self):
        transplant_list = orm.TransplantList()
        if self.xml.updated_on:
            transplant_list.updatedon = self.xml.updated_on

        if self.xml.admission_source:
            transplant_list.admissionsourcecode = self.xml.admission_source.code
            transplant_list.admissionsourcecodestd = self.xml.admission_source.coding_standard
            transplant_list.admissionsourcedesc = self.xml.admission_source.description

        if self.xml.admit_reason:
            transplant_list.admitreasoncode = self.xml.admit_reason.code
            transplant_list.admitreasoncodestd = self.xml.admit_reason.coding_standard
            transplant_list.admitreasondesc = self.xml.admit_reason.description

        if self.xml.admitting_clinician:
            transplant_list.admittingcliniciancode = self.xml.admitting_clinician.code
            transplant_list.admittingcliniciancodestd = self.xml.admitting_clinician.coding_standard
            transplant_list.admittingcliniciandesc = self.xml.admitting_clinician.description

        if self.xml.discharge_location:
            transplant_list.dischargelocationcode = self.xml.discharge_location.code
            transplant_list.dischargereasoncodestd = self.xml.discharge_location.coding_standard
            transplant_list.dischargelocationdesc = self.xml.discharge_location.description

        if self.xml.discharge_reason:
            transplant_list.dischargereasoncode = self.xml.discharge_reason.code
            transplant_list.dischargereasoncodestd = self.xml.discharge_reason.coding_standard
            transplant_list.dischargereasondesc = self.xml.discharge_reason.description

        if self.xml.encounter_number:
            transplant_list.encounternumber = self.xml.encounter_number

        if self.xml.encounter_type:
            transplant_list.encountertype = self.xml.encounter_type

        if self.xml.entered_at:
            transplant_list.enteredatcode = self.xml.entered_at.code
            transplant_list.enteredatcodestd = self.xml.entered_at.coding_standard
            transplant_list.enteredatdesc = self.xml.entered_at.description

        if self.xml.from_time:
            transplant_list.fromtime = self.xml.from_time

        if self.xml.health_care_facility:
            transplant_list.healthcarefacilitycode = self.xml.health_care_facility.code
            transplant_list.healthcarefacilitycodestd = self.xml.health_care_facility.coding_standard
            transplant_list.healthcarefacilitydesc = self.xml.health_care_facility.description

        if self.xml.to_time:
            transplant_list.totime = self.xml.to_time

        return transplant_list


class ProgramMembership:
    def __init__(self, xml: xsd_program_memberships.ProgramMembership):
        self.xml = xml

    def to_orm(self):
        program_membership = orm.ProgramMembership()
        if self.xml.entered_at:
            program_membership.enteredatcode = self.xml.entered_at.code
            program_membership.enteredatdesc = self.xml.entered_at.description
            program_membership.enteredatcodestd = self.xml.entered_at.coding_standard
        if self.xml.entered_by:
            program_membership.enteredbycode = self.xml.entered_by.code
            program_membership.enteredbycodestd = self.xml.entered_by.coding_standard
            program_membership.enteredbydesc = self.xml.entered_by.description
        if self.xml.external_id:
            program_membership.externalid = self.xml.external_id
        if self.xml.from_time:
            program_membership.fromtime = self.xml.from_time
        if self.xml.program_description:
            program_membership.programdescription = self.xml.program_description
        if self.xml.program_name:
            program_membership.programname = self.xml.program_name
        if self.xml.to_time:
            program_membership.to_time = self.xml.to_time
        if self.xml.updated_on:
            program_membership.updatedon = self.xml.updated_on

        return program_membership


class OptOut:
    def __init__(self, xml: xsd_opt_outs.OptOut):
        self.xml = xml

    def to_orm(self):
        opt_out = orm.OptOut()
        if self.xml.entered_at:
            opt_out.entered_at_code = self.xml.entered_at.code
            opt_out.entered_at_code_std = self.xml.entered_at.coding_standard
            opt_out.entered_at_desc = self.xml.entered_at.description
        if self.xml.entered_by:
            opt_out.entered_by_code = self.xml.entered_by.code
            opt_out.entered_by_code_std = self.xml.entered_by.coding_standard
            opt_out.entered_by_desc = self.xml.entered_by.description
        if self.xml.external_id:
            opt_out.external_id = self.xml.external_id
        if self.xml.from_time:
            opt_out.fromtime = self.xml.from_time
        if self.xml.program_description:
            opt_out.program_description = self.xml.from_time
        if self.xml.program_name:
            opt_out.programname = self.xml.program_name
        if self.xml.to_time:
            opt_out.totime = self.xml.to_time
        if self.xml.updated_on:
            opt_out.updatedon = self.xml.updated_on

        return opt_out


class ClinicalRelationship:
    def __init__(self, xml: xsd_clinical_relationships.ClinicalRelationship):
        self.xml = xml

    def to_orm(self):
        clinical_relationship = orm.ClinicalRelationship()
        if self.xml.clinician:
            clinical_relationship.cliniciancode = self.xml.clinician.code
            clinical_relationship.cliniciancodestd = self.xml.clinician.coding_standard
            clinical_relationship.cliniciandesc = self.xml.clinician.description
        if self.xml.external_id:
            clinical_relationship.externalid = self.xml.external_id
        if self.xml.facility_code:
            clinical_relationship.facilitycode = self.xml.facility_code
        if self.xml.from_time:
            clinical_relationship.fromtime = self.xml.from_time
        if self.xml.to_time:
            clinical_relationship.totime = self.xml.to_time
        if self.xml.updated_on:
            clinical_relationship.updatedon = self.xml.updated_on

        return clinical_relationship


class Level:
    def __init__(self, xml: xsd_surveys.Level):
        self.xml = xml

    def to_orm(self):
        level = orm.Level()
        if self.xml.value:
            level.value = self.xml.value
        if self.xml.level_type:
            level.leveltypecode = self.xml.level_type.code
            level.leveltypecodestd = self.xml.level_type.coding_standard
            level.leveltypedesc = self.xml.level_type.description

        return level


class Question:
    def __init__(self, xml: xsd_surveys.Question):
        self.xml = xml

    def to_orm(self):
        question = orm.Question()
        if self.xml.question_text:
            question.questiontext = self.xml.question_text
        if self.xml.question_type:
            question.questiontypecode = self.xml.question_type.code
            question.questiontypecodestd = self.xml.question_type.description
            question.questiontypedesc = self.xml.question_type.description
        if self.xml.response:
            question.response = self.xml.response

        return question


class Score:
    def __init__(self, xml: xsd_surveys.Score):
        self.xml = xml

    def to_orm(self):
        score = orm.Score()
        if self.xml.score_type:
            score.scoretypecode = self.xml.score_type.code
            score.scoretypecodestd = self.xml.score_type.coding_standard
            score.scoretypedesc = self.xml.score_type.description
        if self.xml.value:
            score.value = self.xml.value
        return score


class Survey:
    def __init__(self, xml: xsd_surveys.Survey):
        self.xml = xml

    def to_orm(self):
        survey = orm.Survey()
        if self.xml.entered_at:
            survey.enteredatcode = self.xml.entered_at.code
            survey.enteredatcodestd = self.xml.entered_at.coding_standard
            survey.enteredatdesc = self.xml.entered_at.description
        if self.xml.entered_by:
            survey.enteredbycode = self.xml.entered_by.code
            survey.enteredbycodestd = self.xml.entered_by.coding_standard
            survey.enteredbydesc = self.xml.entered_by.description
        if self.xml.external_id:
            survey.externalid = self.xml.external_id
        if self.xml.hdlocation:
            survey.hdlocation = self.xml.hdlocation
        if self.xml.survey_time:
            survey.surveytime = self.xml.survey_time
        if self.xml.levels:
            survey.levels = [Level(level) for level in self.xml.levels.level]
        if self.xml.questions:
            survey.questions = [Question(question) for question in self.xml.questions.question]
        if self.xml.scores:
            survey.scores = [Score(score) for score in self.xml.scores.score]
        return survey


class PVData:
    def __init__(self, xml: xsd_pvdata):
        self.xml = xml

    def to_orm(self):
        pvdata = orm.PVData()
        return pvdata


class Document:
    def __init__(self, xml: xsd_documents.Document):
        self.xml = xml

    def to_orm(self):
        document = orm.Document()
        if self.xml.clinician:
            document.cliniciancode = self.xml.clinician.code
            document.cliniciancodestd = self.xml.clinician.coding_standard
            document.cliniciandesc = self.xml.clinician.description

        if self.xml.document_name:
            document.documentname = self.xml.document_name

        if self.xml.document_time:
            document.documentname = self.xml.document_name

        if self.xml.document_type:
            document.documenttypecode = self.xml.document_type.code
            document.documenttypecodestd = self.xml.document_type.coding_standard
            document.documenttypedesc = self.xml.document_type.description

        if self.xml.document_url:
            document.documenturl = self.xml.document_url

        if self.xml.entered_at:
            document.enteredatcode = self.xml.entered_at.code
            document.enteredatcodestd = self.xml.entered_at.coding_standard
            document.enteredatdesc = self.xml.entered_at.description

        if self.xml.entered_by:
            document.enteredbycode = self.xml.entered_by.code
            document.enteredbycodestd = self.xml.entered_by.coding_standard
            document.enteredbydesc = self.xml.entered_by.description

        if self.xml.external_id:
            document.externalid = self.xml.external_id

        if self.xml.file_name:
            document.filename = self.xml.file_name

        if self.xml.file_type:
            document.filetype = self.xml.file_type

        if self.xml.note_text:
            document.notetext = self.xml.note_text

        if self.xml.status:
            document.statuscode = self.xml.status.code
            document.statuscodestd = self.xml.status.coding_standard
            document.statusdesc = self.xml.status.description

        if self.xml.stream:
            document.stream = self.xml.stream

        if self.xml.updated_on:
            document.updatedon = self.xml.updated_on


class PatientRecord:
    def __init__(self, xml: xsd_ukrdc.PatientRecord):
        self.xml = xml

    def to_orm(self):
        record = orm.PatientRecord()

        # Basic columns

        record.sendingfacility = self.xml.sending_facility.value if self.xml.sending_facility else None

        record.sendingextract = self.xml.sending_extract.value

        # Relationships

        record.patient = Patient(self.xml.patient).to_orm() if self.xml.patient else None

        if self.xml.lab_orders:
            record.lab_orders = [LabOrder(order).to_orm() for order in self.xml.lab_orders.lab_order]

        if self.xml.social_histories:
            record.social_histories = [SocialHistory(history).to_orm() for history in self.xml.social_histories.social_history]

        if self.xml.family_histories:
            record.family_histories = [FamilyHistory(history).to_orm() for history in self.xml.family_histories.family_history]

        if self.xml.allergies:
            record.allergies = [Allergy(allergy).to_orm() for allergy in self.xml.allergies.allergy]

        if self.xml.diagnoses:
            if self.xml.diagnoses.diagnosis:
                record.diagnoses = [Diagnosis(diagnosis).to_orm() for diagnosis in self.xml.diagnoses.diagnosis]
            if self.xml.diagnoses.cause_of_death:
                record.cause_of_death = [CauseOfDeath(self.xml.diagnoses.cause_of_death).to_orm()]
            if self.xml.diagnoses.renal_diagnosis:
                record.renaldiagnoses = [RenalDiagnosis(self.xml.diagnoses.renal_diagnosis).to_orm()]

        if self.xml.medications:
            record.medications = [Medication(medication).to_orm() for medication in self.xml.medications.medication]

        if self.xml.procedures:
            if self.xml.procedures.procedure:
                record.procedures = [Procedure(procedure).to_orm() for procedure in self.xml.procedures.procedure]
            if self.xml.procedures.dialysis_sessions:
                # DialysisSessions list can be split into multiple elements with different start and stop values.
                # In the XML files, this simply corresponds to multiple <DialysisSessions start=... stop=...> elements,
                # each containing a list of DialysisSession elements.
                # In the Python XSData objects though, this corresponds to a two-deep nested list which we need to unpack.
                # Currently, the start and stop values of each outer element are ignored.
                record.dialysis_sessions = [
                    DialysisSession(session).to_orm()
                    for dialysis_sessions in self.xml.procedures.dialysis_sessions
                    for session in dialysis_sessions.dialysis_session
                ]
            if self.xml.procedures.transplant:
                record.transplants = [Transplant(transplant).to_orm() for transplant in self.xml.procedures.transplant]

            if self.xml.procedures.vascular_access:
                record.vascular_accesses = [VascularAccess(access).to_orm() for access in self.xml.procedures.vascular_access]

        if self.xml.documents:
            record.documents = [Document(document).to_orm() for document in self.xml.documents.document]

        if self.xml.encounters:
            if self.xml.encounters.encounter:
                record.encounters = [Encounter(encounter).to_orm() for encounter in self.xml.encounters.encounter]

            if self.xml.encounters.treatment:
                record.treatments = [Treatment(treatment).to_orm() for treatment in self.xml.encounters.treatment]

            if self.xml.encounters.transplant_list:
                record.transplantlists = [TransplantList(tplist).to_orm() for tplist in self.xml.encounters.transplant_list]

        if self.xml.program_memberships:
            record.program_memberships = [ProgramMembership(membership).to_orm() for membership in self.xml.program_memberships]

        if self.xml.opt_outs:
            record.opt_outs = [OptOut(optout).to_orm() for optout in self.xml.opt_outs]

        if self.xml.clinical_relationships:
            record.clinical_relationships = [ClinicalRelationship(relationship).to_orm() for relationship in self.xml.clinical_relationships]

        if self.xml.surveys:
            record.surveys = [Survey(survey).to_orm() for survey in self.xml.surveys]

        if self.xml.pvdata:
            record.pvdata = [PVData(pvdata).to_orm() for pvdata in self.xml.pvdata]

        return record
