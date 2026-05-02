# CRM API Detailed Report

## 1. How API Calls Will Work
The CRM API is a RESTful API. To make a request, you will use standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`). Most endpoints require an `Authorization` header with a Bearer token (`Bearer <your_token_here>`). Data is sent and received in JSON format (`application/json`).

## 2. Accessing the API
- **Base URL**: `https://api-crm.rustx.net`
- **Authentication Endpoint**: `/api/Authentication/dologin` or `/api/Authentication/userlogin` (POST to get token)
- **Documentation UI**: `https://api-crm.rustx.net/swagger/index.html`

## 3. API Summary Statistics
- **Total Endpoints**: 258
- **GET Requests**: 98
- **POST Requests**: 159
- **PUT Requests**: 0
- **DELETE Requests**: 1

## 4. Detailed API Endpoints

### `POST` /api/AttributeMst/GetAttributeMst
- **Tags**: AttributeMst
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeMst/AddEditAttributeMst
- **Tags**: AttributeMst
- **Request Body (JSON)**: Schema `AttributeMstModel`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeMst/GetAttributeType
- **Tags**: AttributeMst
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeMst/AddEditAttributeType
- **Tags**: AttributeMst
- **Request Body (JSON)**: Schema `AttributeTypeModel`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeMst/getAttributeListById/{id}
- **Tags**: AttributeMst
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/AttributeType/updateTallyData
- **Tags**: AttributeType
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeType/getSaleTargets
- **Tags**: AttributeType
- **Request Body (JSON)**: Schema `SaleTargetRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeType/SaveSaleTarget
- **Tags**: AttributeType
- **Request Body (JSON)**: Schema `SaleTargetModel`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeType/GetCalendarEvents
- **Tags**: AttributeType
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeType/BulkAssignPipeline
- **Tags**: AttributeType
- **Request Body (JSON)**: Schema `BulkAssignPipelineModal`
- **Responses**:
  - `200`: Success

### `POST` /api/AttributeType/SaveMenuOptions
- **Tags**: AttributeType
- **Request Body (JSON)**: Schema `AddMenuOptions`
- **Responses**:
  - `200`: Success

### `GET` /api/AttributeType/GetMenuList
- **Tags**: AttributeType
- **Responses**:
  - `200`: Success

### `GET` /api/AttributeType/GetMenus
- **Tags**: AttributeType
- **Responses**:
  - `200`: Success

### `GET` /api/AttributeType/GetSideMenuList
- **Tags**: AttributeType
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/dologin
- **Tags**: Authentication
- **Request Body (JSON)**: Schema `LoginModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/sendOtp/{type}/{MobileNo}
- **Tags**: Authentication
- **Parameters**:
  - `type` (path): Required
  - `MobileNo` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/verifyMobileOTP/{MobileNo}&{OTP}
- **Tags**: Authentication
- **Parameters**:
  - `MobileNo` (path): Required
  - `OTP` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/userlogin
- **Tags**: Authentication
- **Request Body (JSON)**: Schema `UserLoginMst`
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/requestResetPassword
- **Tags**: Authentication
- **Parameters**:
  - `email` (query): Optional
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/updateUserPassword
- **Tags**: Authentication
- **Request Body (JSON)**: Schema `UpdateUserPasswordModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Authentication/forgotPassword
- **Tags**: Authentication
- **Request Body (JSON)**: Schema `ForgotPasswordModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Authentication/userMenuOptions/{userId}
- **Tags**: Authentication
- **Parameters**:
  - `userId` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Bank/GetBankDetails
- **Tags**: Bank
- **Responses**:
  - `200`: Success

### `POST` /api/Bank/AddEditBankDetails
- **Tags**: Bank
- **Request Body (JSON)**: Schema `BankMstModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Brand/getBrands
- **Tags**: Brand
- **Responses**:
  - `200`: Success

### `POST` /api/Brand/SaveBrand
- **Tags**: Brand
- **Request Body (JSON)**: Schema `BrandModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Brand/GetBrandById/{id}
- **Tags**: Brand
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Brand/GenerateBrandExcel
- **Tags**: Brand
- **Responses**:
  - `200`: Success

### `POST` /api/Comment/AddEditComment
- **Tags**: Comment
- **Request Body (JSON)**: Schema `Comments`
- **Responses**:
  - `200`: Success

### `GET` /api/Comment/GetCommentByCustomerId/{Id}
- **Tags**: Comment
- **Parameters**:
  - `Id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Comment/GetComments/{Id}/{type}
- **Tags**: Comment
- **Parameters**:
  - `Id` (path): Required
  - `type` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Comment/GetPipelineComment/{fromDate}/{toDate}/{empCode}
- **Tags**: Comment
- **Parameters**:
  - `fromDate` (path): Required
  - `toDate` (path): Required
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Comment/SaveComment
- **Tags**: Comment
- **Request Body (JSON)**: Schema `CommentsRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Comment/EditComment
- **Tags**: Comment
- **Request Body (JSON)**: Schema `EditCommentModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Comment/CommentsCountForChart
- **Tags**: Comment
- **Parameters**:
  - `isShowAll` (query): Optional
- **Responses**:
  - `200`: Success

### `GET` /api/Comment/GetCompRecentComments/{Id}
- **Tags**: Comment
- **Parameters**:
  - `Id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Country/GetCountry
- **Tags**: Country
- **Responses**:
  - `200`: Success

### `GET` /api/Country/GetCityList
- **Tags**: Country
- **Responses**:
  - `200`: Success

### `POST` /api/Country/GetStateByCountryId
- **Tags**: Country
- **Request Body (JSON)**: Schema `RequestCountryModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Country/GetCityByStateId
- **Tags**: Country
- **Request Body (JSON)**: Schema `RequestStateModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Country/SaveCountry
- **Tags**: Country
- **Request Body (JSON)**: Schema `CountryModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Country/SaveState
- **Tags**: Country
- **Request Body (JSON)**: Schema `CountryModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Country/SaveCity
- **Tags**: Country
- **Request Body (JSON)**: Schema `CountryModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Country/SearchCity/{searchText}
- **Tags**: Country
- **Parameters**:
  - `searchText` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Country/SearchState/{searchText}
- **Tags**: Country
- **Parameters**:
  - `searchText` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/GetCustomerList
- **Tags**: Customer
- **Request Body (JSON)**: Schema `EmployeeCustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/GenerateCustomersExcel
- **Tags**: Customer
- **Request Body (JSON)**: Schema `EmployeeCustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/getCustomerByStage
- **Tags**: Customer
- **Parameters**:
  - `empCode` (query): Optional
  - `stage` (query): Optional
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/getEmpAllClientList
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/searchedEmpClients
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/saveCustomerForm
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CompanyModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/getStages
- **Tags**: Customer
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/getCompanyById/{id}
- **Tags**: Customer
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/getCompanyContact/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/addEditCompanyContact
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CustomerContactModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/customerCheckInDetail/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/customerPipeLine/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/addToPipeLine/{CompCode}/{EmpCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
  - `EmpCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/RemoveCustomerPipeline/{compCode}/{empCode}
- **Tags**: Customer
- **Parameters**:
  - `empCode` (path): Required
  - `compCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/SearchERPCLients
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/SearchCRMCLientList
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CustomerRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/saveMapCRMTallyCustomer
- **Tags**: Customer
- **Request Body (JSON)**: Schema `TallyCrmMappedModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/getTallyCrmMappedList/{EmpCode}
- **Tags**: Customer
- **Parameters**:
  - `EmpCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/GenerateTallyCrmMappedExcel
- **Tags**: Customer
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/updateCustomerStages/{CompCode}/{Stage}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
  - `Stage` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/updateCustomerBusinessValue/{CompCode}/{businessValue}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
  - `businessValue` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/postForCMC/{empCode}/{compCode}
- **Tags**: Customer
- **Parameters**:
  - `empCode` (path): Required
  - `compCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/getCmcCustomerList
- **Tags**: Customer
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/GenerateCmcCustomersToExcel
- **Tags**: Customer
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/updateCMCStatus
- **Tags**: Customer
- **Request Body (JSON)**: Schema `UpdateCMCStatusModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/CmcCustomerPDF/{id}
- **Tags**: Customer
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/updateCustomerTerms
- **Tags**: Customer
- **Request Body (JSON)**: Schema `CompanyModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/CustomerERPInvoices/{erpCompCode}
- **Tags**: Customer
- **Parameters**:
  - `erpCompCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/GetCustomerData/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Customer/DeleteCompanyMapRecord
- **Tags**: Customer
- **Request Body (JSON)**: Schema `RemoveTallyCrmMapModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/GetCustomerSpecifications/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/GetCustomerPOSpecs/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Customer/GetCustomerRateChangeSpecs/{CompCode}
- **Tags**: Customer
- **Parameters**:
  - `CompCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/DashboardHeader/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/MvcStagewise/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/MvcCountryWise/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/YearlySaleData/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/ErpMappedCustomerCount/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Dashboard/ReminderCount/{empCode}
- **Tags**: Dashboard
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Document/GetDocumentById/{docAid}
- **Tags**: Document
- **Parameters**:
  - `docAid` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Document/AddEditDocuments
- **Tags**: Document
- **Request Body (JSON)**: Schema `DocumentAttachment`
- **Responses**:
  - `200`: Success

### `POST` /api/Document/uploadSchedularFiles
- **Tags**: Document
- **Responses**:
  - `200`: Success

### `GET` /api/Document/GetDocumentsByRefType/{id}/{type}
- **Tags**: Document
- **Parameters**:
  - `id` (path): Required
  - `type` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Document/GetDocCategoryTypes
- **Tags**: Document
- **Responses**:
  - `200`: Success

### `GET` /api/DutiesTaxes/GetTerm
- **Tags**: DutiesTaxes
- **Parameters**:
  - `type` (query): Optional
- **Responses**:
  - `200`: Success

### `GET` /api/DutiesTaxes/GetDutyTax
- **Tags**: DutiesTaxes
- **Responses**:
  - `200`: Success

### `POST` /api/DutiesTaxes/AddEditDutyTax
- **Tags**: DutiesTaxes
- **Request Body (JSON)**: Schema `DutiesTaxesModel`
- **Responses**:
  - `200`: Success

### `GET` /api/DutiesTaxes/GenerateDutyTaxExcel
- **Tags**: DutiesTaxes
- **Responses**:
  - `200`: Success

### `GET` /api/DynamicItemSpecForm/GetFormByCategory/{category}
- **Tags**: DynamicItemSpecForm
- **Parameters**:
  - `category` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/DynamicItemSpecForm/SaveDynamicItemSpecFormData
- **Tags**: DynamicItemSpecForm
- **Request Body (JSON)**: Schema `SaveDynamicItemSpecDateModel`
- **Responses**:
  - `200`: Success

### `POST` /api/DynamicItemSpecForm/GetList
- **Tags**: DynamicItemSpecForm
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/DynamicItemSpecForm/SaveSpecsApproval
- **Tags**: DynamicItemSpecForm
- **Request Body (JSON)**: Schema `SpecsApproval`
- **Responses**:
  - `200`: Success

### `GET` /api/DynamicItemSpecForm/GetDynamicSpecData
- **Tags**: DynamicItemSpecForm
- **Responses**:
  - `200`: Success

### `POST` /api/DynamicItemSpecForm/SaveDynamicSpecData
- **Tags**: DynamicItemSpecForm
- **Request Body (JSON)**: Schema `DynamicItemSpecFormModel`
- **Responses**:
  - `200`: Success

### `POST` /api/EmailSender/send
- **Tags**: EmailSender
- **Request Body (JSON)**: Schema `EmailModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Employee/SaveEmployee
- **Tags**: Employee
- **Request Body (JSON)**: Schema `EmployeeModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetEmployeeList
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetEmployeeById/{id}
- **Tags**: Employee
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/getDesignation
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/getUserType
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetEmployeesByType/{userType}
- **Tags**: Employee
- **Parameters**:
  - `userType` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetEmployeesBySearch/{searchText}
- **Tags**: Employee
- **Parameters**:
  - `searchText` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GenerateEmployeeExcel
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `POST` /api/Employee/updateProfileData
- **Tags**: Employee
- **Request Body (JSON)**: Schema `UserProfileModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetTallyCRMSalesPersonMapped
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetTallySalesName
- **Tags**: Employee
- **Responses**:
  - `200`: Success

### `POST` /api/Employee/AddTallyCRMSalesPersonMap
- **Tags**: Employee
- **Request Body (JSON)**: Schema `GetTallyCRMSalesPersonMappedModelcs`
- **Responses**:
  - `200`: Success

### `DELETE` /api/Employee/DeleteTallyCRMSalesPersonMap/{srNo}
- **Tags**: Employee
- **Parameters**:
  - `srNo` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Employee/GetMgmtHierarchy/{empCode}
- **Tags**: Employee
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Employee/SaveMgmtHierarchy
- **Tags**: Employee
- **Request Body (JSON)**: Schema `AddHierarchyRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Error/Error
- **Tags**: Error
- **Responses**:
  - `200`: Success

### `GET` /api/Error/GetErrorLogsById/{id}
- **Tags**: Error
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Franchise/FranchiseRequest
- **Tags**: Franchise
- **Request Body (JSON)**: Schema `FranchiseRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Franchise/GetFranchiseList
- **Tags**: Franchise
- **Responses**:
  - `200`: Success

### `POST` /api/Invoice/GetProformaInvoices
- **Tags**: Invoice
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Invoice/GenerateProformaInvoice
- **Tags**: Invoice
- **Request Body (JSON)**: Schema `QuotationModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Invoice/SaveProformaInvoice
- **Tags**: Invoice
- **Request Body (JSON)**: Schema `GenerateInvoiceModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Invoice/proformaPDF/{id}
- **Tags**: Invoice
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Invoice/getProformaInvoiceByCustId/{id}
- **Tags**: Invoice
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Invoice/GenerateProformaInvoiceExcel
- **Tags**: Invoice
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/JobProfile/Add
- **Tags**: JobProfile
- **Request Body (JSON)**: Schema `JobModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/getLeads
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GenerateLeadsToExcel
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Lead/AssignToMe/{EmpCode}/{LeadAid}
- **Tags**: Lead
- **Parameters**:
  - `EmpCode` (path): Required
  - `LeadAid` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Lead/getEmpLeads/{EmpCode}
- **Tags**: Lead
- **Parameters**:
  - `EmpCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/SaveLead
- **Tags**: Lead
- **Request Body (JSON)**: Schema `LeadMaster`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/SaveLeadStage
- **Tags**: Lead
- **Request Body (JSON)**: Schema `LeadStage`
- **Responses**:
  - `200`: Success

### `GET` /api/Lead/getAllAssignedLeads
- **Tags**: Lead
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GenerateAllAssignedLeadsToExcel
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GenerateEmployeeLeadsToExcel
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/upload
- **Tags**: Lead
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/StageWiseLeadReport
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GenerateLeadsStageReportToExcel
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GetLeadStageLogReport
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/GenerateLeadStageLogReportToExcel
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ExportLeadStageLogReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Lead/AddLeadToCustomerList
- **Tags**: Lead
- **Request Body (JSON)**: Schema `ExportLeadToCustomerList`
- **Responses**:
  - `200`: Success

### `GET` /api/Lead/id/{LeadAid}
- **Tags**: Lead
- **Parameters**:
  - `LeadAid` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Lead/GetLeadDroppedReasons
- **Tags**: Lead
- **Responses**:
  - `200`: Success

### `GET` /api/Menu/userMenuAccess/{empCode}
- **Tags**: Menu
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Menu/getSideMenu
- **Tags**: Menu
- **Responses**:
  - `200`: Success

### `POST` /api/Menu/AddEditSideMenu
- **Tags**: Menu
- **Request Body (JSON)**: Schema `AddEditSideMenuModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Menu/getParentMenuIds
- **Tags**: Menu
- **Responses**:
  - `200`: Success

### `POST` /api/Menu/AddEditAccessToAll
- **Tags**: Menu
- **Request Body (JSON)**: Schema `AddEditMenuModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Notification/get/{id}/{type}
- **Tags**: Notification
- **Parameters**:
  - `id` (path): Required
  - `type` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Notification/Add
- **Tags**: Notification
- **Request Body (JSON)**: Schema `NotificationModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Notification/MarkAsRead
- **Tags**: Notification
- **Request Body (JSON)**: Schema `MarkAsRead`
- **Responses**:
  - `200`: Success

### `GET` /api/Notification/NotificationCount/{EmpCode}
- **Tags**: Notification
- **Parameters**:
  - `EmpCode` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/OtpMst/GetOtpMaster
- **Tags**: OtpMst
- **Responses**:
  - `200`: Success

### `GET` /api/Plant/getPlantName
- **Tags**: Plant
- **Responses**:
  - `200`: Success

### `POST` /api/Plant/AddEditPlant
- **Tags**: Plant
- **Request Body (JSON)**: Schema `PlantModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Plant/GeneratePlantExcel
- **Tags**: Plant
- **Responses**:
  - `200`: Success

### `GET` /api/Product/getProductCategory
- **Tags**: Product
- **Responses**:
  - `200`: Success

### `GET` /api/Product/getUnitType
- **Tags**: Product
- **Responses**:
  - `200`: Success

### `GET` /api/Product/ProductWithPriceList
- **Tags**: Product
- **Responses**:
  - `200`: Success

### `POST` /api/Product/searchedProducts
- **Tags**: Product
- **Request Body (JSON)**: Schema `ProductRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Product/searchERPInvoiceItem
- **Tags**: Product
- **Request Body (JSON)**: Schema `ProductRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Product/SaveProduct
- **Tags**: Product
- **Request Body (JSON)**: Schema `ProductModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Product/GetProductById/{id}
- **Tags**: Product
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Product/GenerateProductExcel
- **Tags**: Product
- **Responses**:
  - `200`: Success

### `POST` /api/Product/SaveProductCategory
- **Tags**: Product
- **Request Body (JSON)**: Schema `ProductCategoryModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Product/GenerateProductCategoryExcel
- **Tags**: Product
- **Responses**:
  - `200`: Success

### `POST` /api/Product/AddEditUnit
- **Tags**: Product
- **Request Body (JSON)**: Schema `UnitModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/getQuoteType
- **Tags**: Quote
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/getCurrencyName
- **Tags**: Quote
- **Responses**:
  - `200`: Success

### `POST` /api/Quote/SaveQuotationForm
- **Tags**: Quote
- **Request Body (JSON)**: Schema `QuotationModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Quote/getQuotation
- **Tags**: Quote
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/getQuotationById/{id}
- **Tags**: Quote
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/quotationPDF/{id}
- **Tags**: Quote
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/getQuotationByCustId/{id}
- **Tags**: Quote
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/getStatusdata
- **Tags**: Quote
- **Responses**:
  - `200`: Success

### `POST` /api/Quote/GenerateQuotationExcel
- **Tags**: Quote
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Quote/updateStatus
- **Tags**: Quote
- **Request Body (JSON)**: Schema `UpdateStatusModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Quote/statusCount/{empCode}
- **Tags**: Quote
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Reports/GetActivityStatus
- **Tags**: Reports
- **Parameters**:
  - `isShowAll` (query): Optional
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetActivityStatusCustomer
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCustomerERPSaleReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Reports/GetCustomersLastComment/{empCode}
- **Tags**: Reports
- **Parameters**:
  - `empCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Reports/GetEmployeeCustomerSummary
- **Tags**: Reports
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCustomerStageChangeLog
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCustomerStageChangeLogReportToExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `CustomerStageChangeLogExportModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetQuotationReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetSampleReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetPendingSaleOrder
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCustomerBillingFrequencyRpt
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCustomerBillingFreqReportToExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportCustomerBillingFreqReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCheckinData
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetOutstandingBalanceData
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCommentsReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCommentsReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportCommentReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GeneratePendingSaleOrderExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportPendingReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateActivityStatusExcel
- **Tags**: Reports
- **Parameters**:
  - `isShowAll` (query): Optional
- **Request Body (JSON)**: Schema `ExportCommentCount`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCustomerERPSaleReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportErpSaleReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateSampleReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportSampleReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateQuotationReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportQuotationReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateActivityStatusCustomerExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportCustomerVisitReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetNifReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateGetNifReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportNifReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCheckinDataExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportCheckInExcel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateOutstandingBalanceExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportOutstandingBalanceReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetEmpTallySaleRpt
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateProductWiseTallySaleReportExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateEmployeeStageExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportEmpCustomerStageWiseReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetFeedbackList
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateFeedbackReportToExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Reports/GetFeedbackAnswerById/{FbId}
- **Tags**: Reports
- **Parameters**:
  - `FbId` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetCustomerComments
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateCustomerCommentsExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ExportCommentReport`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetERPCustomerDespatches
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GenerateERPCustomerDespatchesToExcel
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetERPSaleAndPendingOrderRpt
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/getERPSaleVsPendingOrderWithVisiton
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Reports/GetERPProductRateChangeReport
- **Tags**: Reports
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Sample/SaveSample
- **Tags**: Sample
- **Request Body (JSON)**: Schema `SampleModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Sample/getSamples
- **Tags**: Sample
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Sample/getSamplesById/{id}
- **Tags**: Sample
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Sample/samplePDF/{id}
- **Tags**: Sample
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Sample/saveSampleDispatch
- **Tags**: Sample
- **Request Body (JSON)**: Schema `SampleDispatchModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Sample/getSampleByCustId/{id}
- **Tags**: Sample
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Sample/GenerateSampleExcel
- **Tags**: Sample
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Sample/sendSampleMail/{id}/{sendDespatchDetail}
- **Tags**: Sample
- **Parameters**:
  - `id` (path): Required
  - `sendDespatchDetail` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/SmsTemplate/GetSmsTemplate
- **Tags**: SmsTemplate
- **Responses**:
  - `200`: Success

### `POST` /api/SmsTemplate/GetSmsTemplateById/{id}
- **Tags**: SmsTemplate
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/SmsTemplate/AddEditSmsTemplateMst
- **Tags**: SmsTemplate
- **Request Body (JSON)**: Schema `SmsTemplateMasterModel`
- **Responses**:
  - `200`: Success

### `POST` /api/SmsTemplate/GetSMSTextList
- **Tags**: SmsTemplate
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/SaveRateChangeSpecs
- **Tags**: Specification
- **Request Body (JSON)**: Schema `RateChangeRequest`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/SaveSpecsApproval
- **Tags**: Specification
- **Request Body (JSON)**: Schema `SpecsApproval`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/SaveCustomerTermsSpecs
- **Tags**: Specification
- **Request Body (JSON)**: Schema `CompanyTermsSpecs`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/getCustomerTermsSpecs
- **Tags**: Specification
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/RateChangeSpecs
- **Tags**: Specification
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/getCustomerRateChangeSpecs
- **Tags**: Specification
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Specification/RateChangeSpecsPDF/{id}
- **Tags**: Specification
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Specification/ItemSpecChangePDF/{id}
- **Tags**: Specification
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/SaveSpecsApprovalInfo
- **Tags**: Specification
- **Request Body (JSON)**: Schema `SpecsApproval`
- **Responses**:
  - `200`: Success

### `POST` /api/Specification/GetOrderStatusSpecList
- **Tags**: Specification
- **Request Body (JSON)**: Schema `ListRequestModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Task/SaveTask
- **Tags**: Task
- **Request Body (JSON)**: Schema `TaskModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Task/getTask/{EmpCode}
- **Tags**: Task
- **Parameters**:
  - `EmpCode` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Task/getPriority
- **Tags**: Task
- **Responses**:
  - `200`: Success

### `GET` /api/Task/getTaskStatus
- **Tags**: Task
- **Responses**:
  - `200`: Success

### `POST` /api/Task/SaveTaskProcessTemplate
- **Tags**: Task
- **Request Body (JSON)**: Schema `TaskProcessTemplateRequestModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Task/getTaskProcessTemplates
- **Tags**: Task
- **Responses**:
  - `200`: Success

### `POST` /api/Task/autoGenerateTask
- **Tags**: Task
- **Request Body (JSON)**: Schema `AutoGenerateTaskModel`
- **Responses**:
  - `200`: Success

### `GET` /api/Task/taskProcessTemplate/{id}
- **Tags**: Task
- **Parameters**:
  - `id` (path): Required
- **Responses**:
  - `200`: Success

### `GET` /api/Task/taskTemplateMaps/{taskName}
- **Tags**: Task
- **Parameters**:
  - `taskName` (path): Required
- **Responses**:
  - `200`: Success

### `POST` /api/Task/SaveTaskTemplateMap
- **Tags**: Task
- **Request Body (JSON)**: Schema `TaskTemplateMap`
- **Responses**:
  - `200`: Success

### `POST` /api/TimeZone/GetTimeZone
- **Tags**: TimeZone
- **Responses**:
  - `200`: Success

### `POST` /api/TimeZone/AddEditTimeZone
- **Tags**: TimeZone
- **Request Body (JSON)**: Schema `TimeZoneModel`
- **Responses**:
  - `200`: Success

### `POST` /api/User/getuserlist
- **Tags**: User
- **Request Body (JSON)**: Schema `UserModel`
- **Responses**:
  - `200`: Success

### `POST` /api/User/register
- **Tags**: User
- **Request Body (JSON)**: Schema `SignUpModel`
- **Responses**:
  - `200`: Success

### `POST` /api/User/Webregister
- **Tags**: User
- **Request Body (JSON)**: Schema `WebUserRegModel`
- **Responses**:
  - `200`: Success

### `POST` /api/User/getusertypelist
- **Tags**: User
- **Responses**:
  - `200`: Success

### `POST` /api/User/AddEditUserType
- **Tags**: User
- **Request Body (JSON)**: Schema `UserTypeModel`
- **Responses**:
  - `200`: Success

### `POST` /api/Whatsapp/SendWhatsApp
- **Tags**: Whatsapp
- **Request Body (JSON)**: Schema `MessageData`
- **Responses**:
  - `200`: Success

### `POST` /api/Whatsapp/GetWhatsAppList
- **Tags**: Whatsapp
- **Responses**:
  - `200`: Success

