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
import ukrdc_xsdata.ukrdc.social_histories as xsd_social_histories


class SocialHistory:
    def __init__(self, social_history: xsd_social_histories.SocialHistory):
        self.social_history = social_history

    def to_orm(self) -> orm.SocialHistory:
        orm_social_history = orm.SocialHistory(
            socialhabitcode=self.social_history.social_habit.code if self.social_history.social_habit else None,
            socialhabitcodestd=self.social_history.social_habit.coding_standard if self.social_history.social_habit else None,
            socialhabitcodedesc=self.social_history.social_habit.description if self.social_history.social_habit else None,
            updatedon=self.social_history.updated_on,
            externalid=self.social_history.external_id,
        )
        return orm_social_history


class ResultItem:
    def __init__(self, result_item: xsd_lab_orders.ResultItem):
        self.result_item = result_item

    def to_orm(self) -> orm.ResultItem:
        return orm.ResultItem(
            resulttype=self.result_item.result_type,
            enteredon=self.result_item.entered_on,
            prepost=self.result_item.pre_post.value if self.result_item.pre_post else None,
            serviceidcode=self.result_item.service_id.code if self.result_item.service_id else None,
            serviceidcodestd=self.result_item.service_id.coding_standard if self.result_item.service_id else None,
            serviceiddesc=self.result_item.service_id.description if self.result_item.service_id else None,
            subid=self.result_item.sub_id,
            resultvalue=self.result_item.result_value,
            resultvalueunits=self.result_item.result_value_units,
            referencerange=self.result_item.reference_range,
            interpretationcodes=self.result_item.interpretation_codes.value if self.result_item.interpretation_codes else None,
            status=self.result_item.status.value if self.result_item.status else None,
            observationtime=self.result_item.observation_time,
            commenttext=self.result_item.comments,
            referencecomment=self.result_item.reference_comment,
        )


class LabOrder:
    def __init__(self, laborder: xsd_lab_orders.LabOrder):
        self.laborder = laborder

    def to_orm(self) -> orm.LabOrder:
        return orm.LabOrder(
            receivinglocationcode=self.laborder.receiving_location.code if self.laborder.receiving_location else None,
            receivinglocationdesc=self.laborder.receiving_location.description if self.laborder.receiving_location else None,
            receivinglocationcodestd=self.laborder.receiving_location.coding_standard if self.laborder.receiving_location else None,
            placerid=self.laborder.placer_id,
            fillerid=self.laborder.filler_id,
            orderedbycode=self.laborder.ordered_by.code if self.laborder.ordered_by else None,
            orderedbydesc=self.laborder.ordered_by.description if self.laborder.ordered_by else None,
            orderedbycodestd=self.laborder.ordered_by.coding_standard if self.laborder.ordered_by else None,
            orderitemcode=self.laborder.order_item.code if self.laborder.order_item else None,
            orderitemdesc=self.laborder.order_item.description if self.laborder.order_item else None,
            orderitemcodestd=self.laborder.order_item.coding_standard if self.laborder.order_item else None,
            ordercategorycode=self.laborder.order_category.code if self.laborder.order_category else None,
            ordercategorydesc=self.laborder.order_category.description if self.laborder.order_category else None,
            ordercategorycodestd=self.laborder.order_category.coding_standard if self.laborder.order_category else None,
            specimencollectedtime=self.laborder.specimen_collected_time,
            specimenreceivedtime=self.laborder.specimen_received_time,
            status=self.laborder.status,
            prioritycode=self.laborder.priority.code if self.laborder.priority else None,
            prioritydesc=self.laborder.priority.description if self.laborder.priority else None,
            prioritycodestd=self.laborder.priority.coding_standard if self.laborder.priority else None,
            specimensource=self.laborder.specimen_source,
            duration=self.laborder.duration,
            patientclasscode=self.laborder.patient_class.code if self.laborder.patient_class else None,
            patientclassdesc=self.laborder.patient_class.description if self.laborder.patient_class else None,
            patientclasscodestd=self.laborder.patient_class.coding_standard if self.laborder.patient_class else None,
            enteredon=self.laborder.entered_on,
            enteredatcode=self.laborder.entered_at.code if self.laborder.entered_at else None,
            enteredatdesc=self.laborder.entered_at.description if self.laborder.entered_at else None,
            enteredatcodestd=self.laborder.entered_at.coding_standard if self.laborder.entered_at else None,
            enteringorganizationcode=self.laborder.entering_organization.code if self.laborder.entering_organization else None,
            enteringorganizationdesc=self.laborder.entering_organization.description if self.laborder.entering_organization else None,
            enteringorganizationcodestd=self.laborder.entering_organization.coding_standard if self.laborder.entering_organization else None,
            updatedon=self.laborder.updated_on,
            externalid=self.laborder.external_id,
            result_items=[ResultItem(item).to_orm() for item in self.laborder.result_items.result_item] if self.laborder.result_items else None,
        )


class FamilyDoctor:
    def __init__(self, family_doctor: xsd_types.FamilyDoctor):
        self.family_doctor = family_doctor

    def to_orm(self) -> orm.FamilyDoctor:
        return orm.FamilyDoctor(
            gpname=self.family_doctor.gpname,
            gpid=self.family_doctor.gpid,
            gppracticeid=self.family_doctor.gppractice_id,
            addressuse=self.family_doctor.address.use if self.family_doctor.address else None,
            fromtime=self.family_doctor.address.from_time if self.family_doctor.address else None,
            totime=self.family_doctor.address.to_time if self.family_doctor.address else None,
            street=self.family_doctor.address.street if self.family_doctor.address else None,
            town=self.family_doctor.address.town if self.family_doctor.address else None,
            county=self.family_doctor.address.county if self.family_doctor.address else None,
            postcode=self.family_doctor.address.postcode if self.family_doctor.address else None,
            countrycode=self.family_doctor.address.country.code if self.family_doctor.address and self.family_doctor.address.country else None,
            countrycodestd=self.family_doctor.address.country.coding_standard if self.family_doctor.address and self.family_doctor.address.country else None,
            countrydesc=self.family_doctor.address.country.description if self.family_doctor.address and self.family_doctor.address.country else None,
            contactuse=self.family_doctor.contact_detail.use if self.family_doctor.contact_detail else None,
            contactvalue=self.family_doctor.contact_detail.value if self.family_doctor.contact_detail else None,
            email=self.family_doctor.email,
            commenttext=self.family_doctor.contact_detail.comments if self.family_doctor.contact_detail else None,
        )


class Address:
    def __init__(self, address: xsd_types.Address):
        self.address = address

    def to_orm(self) -> orm.Address:
        return orm.Address(
            addressuse=self.address.use,
            fromtime=self.address.from_time,
            totime=self.address.to_time,
            street=self.address.street,
            town=self.address.town,
            county=self.address.county,
            postcode=self.address.postcode,
            countrycode=self.address.country.code if self.address.country else None,
            countrycodestd=self.address.country.coding_standard if self.address.country else None,
            countrydesc=self.address.country.description if self.address.country else None,
        )


class ContactDetail:
    def __init__(self, xsd_contact: xsd_types.ContactDetail):
        self.xsd_contact = xsd_contact

    def to_orm(self) -> orm.ContactDetail:
        return orm.ContactDetail(
            contactuse=self.xsd_contact.use,
            contactvalue=self.xsd_contact.value,
            commenttext=self.xsd_contact.comments,
        )


class Name:
    def __init__(self, xml: xsd_types.Name):
        self.xml = xml

    def to_orm(self):
        return orm.Name(
            nameuse=self.xml.use,
            prefix=self.xml.prefix,
            family=self.xml.family,
            given=self.xml.given,
            othergivennames=self.xml.other_given_names,
            suffix=self.xml.suffix,
        )


class PatientNumber:
    def __init__(self, xml: xsd_types.PatientNumber):
        self.xml = xml

    def to_orm(self):
        return orm.PatientNumber(
            patientid=self.xml.number,
            organization=self.xml.organization,
            numbertype=self.xml.number_type,
        )


class Patient:
    def __init__(self, xml: xsd_ukrdc.Patient):
        self.xml = xml

    @property
    def _first_person_to_contact(self) -> Optional[xsd_types.ContactDetail]:
        if self.xml.person_to_contact and self.xml.person_to_contact.contact_details:
            return self.xml.person_to_contact.contact_details[0]
        return None

    def to_orm(self):
        return orm.Patient(
            birthtime=self.xml.birth_time.to_datetime() if self.xml.birth_time else None,
            deathtime=self.xml.death_time.to_datetime() if self.xml.death_time else None,
            gender=self.xml.gender,
            countryofbirth=self.xml.country_of_birth,
            ethnicgroupcode=self.xml.ethnic_group.code if self.xml.ethnic_group else None,
            ethnicgroupcodestd=self.xml.ethnic_group.coding_standard if self.xml.ethnic_group else None,
            ethnicgroupdesc=self.xml.ethnic_group.description if self.xml.ethnic_group else None,
            persontocontactname=self.xml.person_to_contact.name if self.xml.person_to_contact else None,
            persontocontact_contactnumber=self._first_person_to_contact.value if self._first_person_to_contact else None,
            persontocontact_relationship=self.xml.person_to_contact.relationship if self.xml.person_to_contact else None,
            persontocontact_contactnumbercomments=self._first_person_to_contact.comments if self._first_person_to_contact else None,
            persontocontact_contacttype=self._first_person_to_contact.use if self._first_person_to_contact else None,
            occupationcode=self.xml.occupation.code if self.xml.occupation else None,
            occupationcodestd=self.xml.occupation.coding_standard if self.xml.occupation else None,
            occupationdesc=self.xml.occupation.description if self.xml.occupation else None,
            primarylanguagecode=self.xml.primary_language.code if self.xml.primary_language else None,
            primarylanguagecodestd=self.xml.primary_language.coding_standard if self.xml.primary_language else None,
            primarylanguagedesc=self.xml.primary_language.description if self.xml.primary_language else None,
            death=self.xml.death,
            updatedon=self.xml.updated_on.to_datetime() if self.xml.updated_on else None,
            bloodgroup=self.xml.blood_group,
            bloodrhesus=self.xml.blood_rhesus,
            numbers=[PatientNumber(number).to_orm() for number in self.xml.patient_numbers.patient_number] if self.xml.patient_numbers else [],
            names=[Name(name).to_orm() for name in self.xml.names.name] if self.xml.names else [],
            contact_details=[ContactDetail(contact).to_orm() for contact in self.xml.contact_details.contact_detail] if self.xml.contact_details else [],
            addresses=[Address(address).to_orm() for address in self.xml.addresses.address] if self.xml.addresses else [],
            familydoctor=FamilyDoctor(self.xml.family_doctor).to_orm() if self.xml.family_doctor else None,
        )


class PatientRecord:
    def __init__(self, xml: xsd_ukrdc.PatientRecord):
        self.xml = xml

    def to_orm(self):
        return orm.PatientRecord(
            # pid=self.pid,
            # ukrdcid=self.ukrdcid,
            # localpatientid=self.localpatientid,
            # extracttime=self.extract_time,
            # creationdate=self.creation_date,
            # updatedate=self.update_date,
            # repositorycreationdate=self.repository_creation_date,
            # repositoryupdatedate=self.repository_update_date,
            sendingfacility=self.xml.sending_facility.value if self.xml.sending_facility else None,
            sendingextract=self.xml.sending_extract,
            patient=Patient(self.xml.patient).to_orm() if self.xml.patient else None,
            lab_orders=[LabOrder(order).to_orm() for order in self.xml.lab_orders.lab_order] if self.xml.lab_orders else [],
            social_histories=[SocialHistory(history).to_orm() for history in self.xml.social_histories.social_history] if self.xml.social_histories else [],
        )
