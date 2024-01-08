import pandas as pd
import csv
from urllib.parse import urljoin
from companies_house_api import ChAPI
from datetime import datetime

class CompanyInfo():
    """
    GET request based on company number.
    The authentication method uses an api key stored in a text file located in the parent directory.
    Company information is exported to CSV files.
    """
    
    def __init__(self, company_number: str, timestamp: str, authentication_fp: str = None, prefix: str = '') -> None:
        self._company_number = company_number
        self._base_url = r'https://api.company-information.service.gov.uk/'
        self._company_url = urljoin(self.base_url + 'company/', str(self._company_number))
        self._prefix = prefix
        self._timestamp = timestamp
        
        if authentication_fp is None:
            self.__api_key = ChAPI.getApiKey()
        else:
            self.__api_key = ChAPI.getApiKey(authentication_fp)
        
        self._company_data = ChAPI.getChData(self._company_url, self.__api_key)
        # Links
        links = self._company_data.get('links')
        self._officers_url = urljoin(self._base_url, links.get('officers', ''))
        self._filing_history_url = urljoin(self._base_url, links.get('filing_history', '')) 
        self._charges_url = urljoin(self._base_url, links.get('charges', '')) 
        self._persons_significant_control_url = urljoin(self._base_url, links.get('persons_with_significant_control', ''))
        # Company info
        self._company_status = str(self._company_data.get('company_status', ''))
        self._company_name = str(self._company_data.get('company_name', ''))
        self._jurisdiction = str(self._company_data.get('jurisdiction', ''))
        self._date_of_creation = str(self._company_data.get('date_of_creation', ''))
        self._has_insolvency_history = bool(self._company_data.get('date_of_creation', None))
        self._has_charges = bool(self._company_data.get('has_charges', None))
        self._has_been_liquidated = bool(self._company_data.get('has_been_liquidated', None))
        self._undeliverable_registered_office_address = bool(self._company_data.get('undeliverable_registered_office_address', None))
        self._registered_office_is_in_dispute = bool(self._company_data.get('registered_office_is_in_dispute', None))
        self._accounts_overdue = bool(self._company_data.get('accounts', {}).get('overdue', None))
        self._etag = str(self._company_data.get('etag', ''))
        self._external_registration_number = str(self._company_data.get('external_registration_number', ''))
        self._company_type = str(self._company_data.get('type', ''))
        if self._company_data.get('foreign_company_details'):
            self._is_foreign_company = True
        else:
            self._is_foreign_company = False
        
        # Address
        self._address_line_1 = str(self._company_data.get('registered_office_address', {}).get('address_line_1', ''))
        self._postal_code = str(self._company_data.get('registered_office_address', {}).get('postal_code', '')) 
        self._locality = str(self._company_data.get('registered_office_address', {}).get('locality', ''))
        self._country = str(self._company_data.get('registered_office_address', {}).get('country', ''))
        
        # Officers
        self._officers = dict()
        
        
    @property
    def company_status(self) -> str:
        return self._company_status

    @property
    def company_name(self) -> str:
        return self._company_name

    @property
    def jurisdiction(self) -> str:
        return self._jurisdiction

    @property
    def date_of_creation(self) -> str:
        return self._date_of_creation

    @property
    def has_insolvency_history(self) -> bool:
        return self._has_insolvency_history

    @property
    def has_charges(self) -> bool:
        return self._has_charges

    @property
    def has_been_liquidated(self) -> bool:
        return self._has_been_liquidated

    @property
    def undeliverable_registered_office_address(self) -> bool:
        return self._undeliverable_registered_office_address

    @property
    def registered_office_is_in_dispute(self) -> bool:
        return self._registered_office_is_in_dispute

    @property
    def accounts_overdue(self) -> bool:
        return self._accounts_overdue

    @property
    def address_line_1(self) -> str:
        return self._address_line_1

    @property
    def postal_code(self) -> str:
        return self._postal_code

    @property
    def locality(self) -> str:
        return self._locality

    @property
    def country(self) -> str:
        return self._country
    
    @property
    def company_number(self) -> str:
        return self._company_number
    
    @property
    def company_url(self) -> str:
        return self._company_url
    
    @property 
    def officers_url(self) -> str:
        return self._officers_url

    @property
    def filing_history_url(self) -> str:
        return self._filing_history_url

    @property
    def charges_url(self) -> str:
        return self._charges_url
    
    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def persons_significant_control_url(self) -> str:
        return self._persons_significant_control_url
    
    @property
    def api_key(self):
        return "Access denied"
    
    @property
    def officers(self) -> dict:
        return self._officers
    
    @property
    def prefix(self) -> str:
        return self._prefix
    
    @property
    def timestamp(self) -> str:
        return self._timestamp
    
    @property
    def is_foreign_company(self) -> bool:
        return self._is_foreign_company
        
        
    def exportCompanyInfo(self) -> None:
        """
        Get company profile info from Companies House and export it to CSV files:
        
        {prefix}_sic_codes_{timestamp}.csv,
        {prefix}_previous_company_names_{timestamp}.csv,
        {prefix}_companies_{timestamp}.csv,
        {prefix}_company_officers_{timestamp}.csv,
        {prefix}_persons_significant_control_{timestamp}.csv,
        {prefix}_officer_appointments_{timestamp}.csv,
        {prefix}_natures_of_control_{timestamp}.csv
        
        The primary key is the company number.
        """
        # Get company profile information
        self.getCompanyInfo()
        
        # Get sic codes
        sic_codes = self._company_data.get('sic_codes')
        
        if not sic_codes is None:
            self.getSICCodes(sic_codes)
                
        # Get previous company names
        prev_companies = self._company_data.get('previous_company_names')
        
        if not prev_companies is None:
            self.getPreviousCompanyNames(prev_companies)

        # Get company officers and their appointments
        self.getCompanyOfficers()
        
        # Get persons with significant control
        self.getPersonsSignificantControl()
        
        
    def getCompanyInfo(self):
        """
        Get company profile information
        """
        company_fp = ChAPI.getDataFolderLocation(self._prefix + '_companies_' + self._timestamp + '.csv')
        with open(company_fp,"a",newline='') as company_file:
            company_writer = csv.writer(company_file)
            company_writer.writerow([self._company_number, self._company_name, self._company_status, self._company_type,
                                    self._jurisdiction, self._is_foreign_company, self._date_of_creation, self._etag,
                                    self._external_registration_number, self._address_line_1, self._locality, self._postal_code,
                                    self._country, self._accounts_overdue, self._has_been_liquidated, self._has_charges,
                                    self._has_insolvency_history, self._registered_office_is_in_dispute, 
                                    self._undeliverable_registered_office_address])
        
        
    def getSICCodes(self, sic_codes: list) -> None:
        """
        Get SIC codes
        """
        sic_fp = ChAPI.getDataFolderLocation(self._prefix + "_sic_codes_" + self._timestamp + ".csv")
        
        with open(sic_fp,"a",newline='') as sic_file:
            sf_writer = csv.writer(sic_file)
            for sic in sic_codes:
                sf_writer.writerow([self._company_number, sic])


    def getPreviousCompanyNames(self, prev_companies: list) -> None:
        """
        Get previous company names
        """
        prev_fp = ChAPI.getDataFolderLocation(self._prefix + "_previous_company_names_" + self._timestamp + ".csv")
        
        with open(prev_fp,"a",newline='') as prev_file:
            pf_writer = csv.writer(prev_file)
            for prev in prev_companies:
                pf_writer.writerow([self._company_number,prev.get('ceased_on'),prev.get('effective_from'),prev.get('name')])
                
                
    def getCompanyOfficers(self) -> None:
        """
        Get company officers
        """
        # Fetch new officers data
        officers_data = ChAPI.getChData(self._officers_url, self.__api_key)
        officers = officers_data.get('items', [])

        # Update the _officers attribute with the new data
        self._officers = dict()

        with open(ChAPI.getDataFolderLocation(self._prefix + "_company_officers_" + self._timestamp + ".csv"), "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            for officer in officers:
                officer_name = officer.get('name')
                if officer_name is not None:
                    officer_name = str(officer_name)
                    officer_names = officer_name.split(',')
                    if len(officer_names) == 1:
                        officer_surname = ''
                        officer_forenames = ''
                        officer_forename = ''
                    else:
                        officer_surname = officer_names[0].strip()
                        officer_forenames = officer_names[1].strip().split(' ',1)
                        officer_forename = officer_forenames[0]
                    if len(officer_forenames) < 2:
                        officer_other_forenames = None
                    else:
                       officer_other_forenames = officer_forenames[1] 
                    appointments = str(officer.get('links', {}).get('officer', {}).get('appointments', ''))
                    if appointments != '':
                        officer_id = appointments.split('/')[2]
                    else:
                        officer_id = None
                    self._officers[officer_name] = {
                        'officer_role': str(officer.get('officer_role', '')),
                        'nationality': str(officer.get('nationality', '')),
                        'appointed_on': str(officer.get('appointed_on', '')),
                        'date_of_birth_month': int(officer.get('date_of_birth', {}).get('month', 0)),
                        'date_of_birth_year': int(officer.get('date_of_birth', {}).get('year', 0)),
                        'address_premises': str(officer.get('address', {}).get('premises', '')),
                        'address_address_line_1': str(officer.get('address', {}).get('address_line_1', '')),
                        'address_postal_code': str(officer.get('address', {}).get('postal_code', '')),
                        'address_locality': str(officer.get('address', {}).get('locality', '')),
                        'address_country': str(officer.get('address', {}).get('country', '')),
                        'occupation': str(officer.get('occupation', '')),
                        'country_of_residence': str(officer.get('country_of_residence')),
                        'appointments': appointments,
                        'officer_id': officer_id,
                        'officer_surname': officer_surname,
                        'officer_forename': officer_forename,
                        'officer_other_forenames': officer_other_forenames,
                    }
                    # Export appointments data for all company officers to a csv file. Three fields will be saved in the class.
                    appointments_url = urljoin(self._base_url, appointments)
                    appointments_data = ChAPI.getChData(appointments_url, self.__api_key)
                    appointments_fields = self.getOfficerAppointments(appointments_data, officer_id,)
                    self._officers[officer_name]['appointment_kind'] = str(appointments_fields.get('kind', ''))
                    self._officers[officer_name]['is_corporate_officer'] = bool(appointments_fields.get('is_corporate_officer', None))
                    self._officers[officer_name]['total_company_appointments'] = int(appointments_fields.get('total_results', 0))
                    
                    # Write data to CSV
                    csv_writer.writerow([
                        self._company_number,
                        self._officers[officer_name]['officer_surname'],
                        self._officers[officer_name]['officer_forename'],
                        self._officers[officer_name]['officer_other_forenames'],
                        officer_name,
                        self._officers[officer_name]['officer_role'],
                        self._officers[officer_name]['nationality'],
                        self._officers[officer_name]['appointed_on'],
                        self._officers[officer_name]['date_of_birth_month'],
                        self._officers[officer_name]['date_of_birth_year'],
                        self._officers[officer_name]['address_premises'],
                        self._officers[officer_name]['address_address_line_1'],
                        self._officers[officer_name]['address_postal_code'],
                        self._officers[officer_name]['address_locality'],
                        self._officers[officer_name]['address_country'],
                        self._officers[officer_name]['country_of_residence'],
                        self._officers[officer_name]['occupation'],
                        self._officers[officer_name]['appointments'],
                        self._officers[officer_name]['officer_id'],
                        self._officers[officer_name]['appointment_kind'],
                        self._officers[officer_name]['is_corporate_officer'],
                        self._officers[officer_name]['total_company_appointments'],
                    ])
                else:
                    print("Warning: Officer name is None.")
                    
    def getOfficerAppointments(self, appointments_data: dict, officer_id: str) -> dict:
        """
        Get officer appointments and export to a csv file.
        
        Returns:
            dict: total appointments, is corporate officer, and kind of appointment
        """
        with open(
            ChAPI.getDataFolderLocation(self.prefix + "_officer_appointments_" + self._timestamp + ".csv"),
            "a", newline='') as appointments_csv_file:
            appointments_csv_writer = csv.writer(appointments_csv_file)
            items = appointments_data.get('items', [])
            for item in items:
                appointments_csv_writer.writerow([
                    officer_id,
                    item.get('appointed_to', {}).get('company_number', ''),
                    item.get('appointed_to', {}).get('company_name', ''),
                    item.get('appointed_to', {}).get('company_status', ''),
                    item.get('officer_role', ''),
                    item.get('appointed_on', ''),
                ])
            return dict({
                'kind': appointments_data.get('kind', ''), 
                'is_corporate_officer': appointments_data.get('is_corporate_officer', None), 
                'total_results': appointments_data.get('total_results', None)
                })
        
    
    def getPersonsSignificantControl(self):
        """
        Get persons with significant control of the company.
        """
        if self._base_url == self._persons_significant_control_url:
            # There is no persons with significant control url link
            return
        persons = ChAPI.getChData(self._persons_significant_control_url, self.__api_key)
        with open(ChAPI.getDataFolderLocation(self._prefix + "_persons_significant_control_" + self._timestamp + ".csv"),
                  "a", newline='') as significant_persons_csv_file:
            significant_persons_csv_writer = csv.writer(significant_persons_csv_file)
            # A separate file/table is needed to list each person's natures of control
            with open(ChAPI.getDataFolderLocation(self._prefix + "_natures_of_control_" + self._timestamp + ".csv"),
                      "a", newline='') as natures_of_control_csv_file:
                natures_of_control_csv_writer = csv.writer(natures_of_control_csv_file)
                
                items = persons.get('items', [])
                for item in items:
                    etag = item.get('etag', '') 
                    significant_persons_csv_writer.writerow([
                        self._company_number,
                        item.get('name', ''),
                        item.get('name_elements', {}).get('title', ''),
                        item.get('name_elements', {}).get('surname', ''),
                        item.get('name_elements', {}).get('forename', ''),
                        item.get('name_elements', {}).get('other_forenames', ''),
                        item.get('date_of_birth', {}).get('month', ''),
                        item.get('date_of_birth', {}).get('year', ''),
                        item.get('kind', ''),
                        item.get('notified_on', ''),
                        item.get('nationality', ''),
                        item.get('country_of_residence', ''),
                        item.get("address", {}).get('premises', ''),
                        item.get('address', {}).get('address_line_1', ''),
                        item.get('address', {}).get('address_line_2', ''),
                        item.get('address', {}).get('locality', ''),
                        item.get('address', {}).get('postal_code', ''),
                        item.get('address', {}).get('country', ''),
                        etag,
                        item.get('identification', {}).get('registration_number', ''),
                        item.get('identification', {}).get('legal_form', ''),
                        item.get('identification', {}).get('legal_authority', ''),
                        item.get('identification', {}).get('country_registered', ''),
                        item.get('identification', {}).get('place_registered', ''),
                    ])
                    natures_of_control = item.get('natures_of_control', [])
                    if not natures_of_control:
                        # There is no data on this person's natures of control
                        return
                    else:
                        for nature_of_control in natures_of_control:
                            natures_of_control_csv_writer.writerow([
                                etag,
                                nature_of_control,
                            ])

    
    def setAuthenticationFilePath(self, auth_fp: any) -> None:
        """
        Change the api key by entering a new file path for the authentication file.    
        """
        self.__api_key = ChAPI.getApiKey(auth_fp)
    

if __name__ == '__main__':
    """
    'MAN UTD supporters club Scandinavia': 'OE025157', 
    'Dundonald Church': '07496944'
    'MAN UTD football club ltd': '00095489'
    'MAN UTD ltd': '02570509'
    'Swaravow Ltd' = '15192197'
    """
    # current date and time
    now = datetime.now()
    timestamp = str(datetime.timestamp(now))
    company_info = CompanyInfo('OE025157',timestamp)
