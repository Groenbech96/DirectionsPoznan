# E-Document Integration Workshop Guide

Welcome to the E-Document Integration Workshop! In this hands-on workshop, you'll learn how to build a complete E-Document integration for Business Central, including exporting, sending, receiving, and importing documents.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Exercise 1: Export Documents (15 minutes)](#exercise-1-export-documents-15-minutes)
4. [Exercise 2: Send Documents (10 minutes)](#exercise-2-send-documents-10-minutes)
5. [Testing: Send a Document from Business Central](#testing-send-a-document-from-business-central)
6. [Exercise 3: Receive Documents (15 minutes)](#exercise-3-receive-documents-15-minutes)
7. [Exercise 4: Import Documents (10 minutes)](#exercise-4-import-documents-10-minutes)
8. [Testing: Complete Flow](#testing-complete-flow)

---

## Prerequisites

- Business Central environment with development access
- AL Language extension installed in VS Code
- Access to the workshop repository
- Basic understanding of AL programming

---

## Setup Instructions

Before starting the exercises, you need to configure the E-Document service and connect to the Connector service.

### Step 1: Configure E-Document Service

1. Open Business Central and search for **E-Document Services**
2. Click **New** to create a new service
3. Fill in the following fields:
   - **Code**: Enter a unique code (e.g., `CONNECTOR`)
   - **Description**: Enter a description (e.g., `Directions Connector Service`)
   - **Document Format**: Select **SimpleJson Format**
   - **Service Integration V2**: Select **Connector**
4. Set the documents to export by clicking the action "Configure Documents to Export" and add Sales Invoice.
5. Click **OK** to save

### Step 2: Configure Connector Connection

1. While still on the E-Document Service page, click **Service Integration Setup**
2. The **Connector Connection Setup** page will open
3. Fill in the following fields:
   - **API Base URL**: `https://directionsemea2025-b6aeebakc8fvf0bq.swedencentral-01.azurewebsites.net/`
   - **Service Key**: Click **Register** to get a new service key, or enter your existing key
   - **User Name**: Your name or identifier. Make it unique
4. Click **Test Connection** to verify the setup works
5. Close the setup page

### Step 3: Set Up E-Document Workflow

Follow these steps to configure the workflow that handles E-Document processing:

1. Search for **Workflow Templates**
2. If you don't see **E-Document Workflow Templates**, click **Reset Microsoft Templates**
3. Close the Workflow Templates page
4. Search for **Workflows**
5. Click **New Workflow from Template**
6. Select **Send to one service** template
7. Click **OK**
8. In the workflow, find the **Then Response** field
9. Select **Send E-Document using setup**
10. Select the E-Document Service you created (e.g., `CONNECTOR`)
11. Click **OK**
12. **Enable** the workflow by toggling the **Enabled** switch

**Reference**: [Set up the workflow - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/finance-how-setup-edocuments#set-up-the-workflow)

### Step 4: Configure Document Sending Profile

1. Search for **Document Sending Profiles**
2. Click **New** to create a new profile
3. On the **General** FastTab:
   - **Code**: Enter a code (e.g., `EDOC`)
   - **Description**: Enter description (e.g., `E-Document Sending`)
4. On the **Sending Options** FastTab:
   - Set **Printer**: `No`
   - Set **Email**: `No`
   - Set **Disk**: `No`
   - Set **Electronic Document**: `Extended E-Document Service Flow`
   - Set **E-Document Workflow**: Select the workflow you created
5. Click **OK** to save

**Reference**: [Set up a document sending profile - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/finance-how-setup-edocuments#set-up-a-document-sending-profile)

### Step 5: Assign Document Sending Profile to Customer

1. Search for **Customers**
2. Open a customer card (e.g., customer `10000`)
3. On the **Invoicing** FastTab:
   - Set **Document Sending Profile**: Select the profile you created (e.g., `EDOC`)
4. Close the customer card

**Reference**: [Set Up Document Sending Profiles - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/sales-how-setup-document-send-profiles)

---

## Exercise 1: Export Documents (15 minutes)

**Objective**: Implement the ability to export a Sales Invoice to SimpleJson format.

### Files to Edit
- `SimpleJsonFormat.Codeunit.al`

### Tasks

#### Task 1.A: Validate Posting Date

In the `Check` procedure, add validation for the Posting Date field.

**Location**: Around line 33

**Instructions**:
1. Find the comment `// TODO: Exercise 1.A: Validate Posting Date like Sell-to Customer No.`
2. Add validation for the Posting Date field

**Hint**: Use `.TestField()` like the example above for "Sell-to Customer No."

<details>
<summary>Solution</summary>

```al
SourceDocumentHeader.Field(SalesInvoiceHeader.FieldNo("Posting Date")).TestField();
```
</details>

#### Task 1.B: Add Customer Information to JSON

In the `CreateSalesInvoiceJson` procedure, add customer number and name to the root JSON object.

**Location**: Around line 77

**Instructions**:
1. Find the comment `// TODO: Exercise 1.B - Fill in "customerNo" and "customerName" into root object`
2. Add two JSON properties:
   - `customerNo` - from `SalesInvoiceHeader."Sell-to Customer No."`
   - `customerName` - from `SalesInvoiceHeader."Sell-to Customer Name"`

**Hint**: Use `RootObject.Add()` like the examples above

<details>
<summary>Solution</summary>

```al
RootObject.Add('customerNo', SalesInvoiceHeader."Sell-to Customer No.");
RootObject.Add('customerName', SalesInvoiceHeader."Sell-to Customer Name");
```
</details>

#### Task 1.C: Add Line Details to JSON

In the same procedure, add description and quantity to each line in the JSON array.

**Location**: Around line 99

**Instructions**:
1. Find the comment `// TODO: Exercise 1.B - Fill in "description" and "quantity" for line into LineObject`
2. Add two JSON properties to the line:
   - `description` - from `SalesInvoiceLine.Description`
   - `quantity` - from `SalesInvoiceLine.Quantity`

<details>
<summary>Solution</summary>

```al
LineObject.Add('description', SalesInvoiceLine.Description);
LineObject.Add('quantity', SalesInvoiceLine.Quantity);
```
</details>

### Testing Exercise 1

1. Build your AL project
2. Publish the extension to Business Central
3. In Business Central, create and post a Sales Invoice for the customer you configured
4. Go to **Posted Sales Invoices** and open the posted invoice
5. Click **E-Document** → **Open E-Document**
6. You should see the E-Document with status **Exported**
7. Check the exported JSON to verify all fields are present

---

## Exercise 2: Send Documents (10 minutes)

**Objective**: Implement the ability to send the exported document to the Connector API.

### Files to Edit
- `ConnectorIntegration.Codeunit.al`

### Tasks

#### Task 2.A: Get the Document Content

In the `Send` procedure, retrieve the document content from SendContext.

**Location**: Around line 44

**Instructions**:
1. Find the comment `// TODO: Get temp blob with json from SendContext`
2. Get the TempBlob from SendContext
3. Read the JSON text from the TempBlob

**Hints**:
- Use `SendContext.GetTempBlob()` to get the TempBlob
- Use `ConnectorRequests.ReadJsonFromBlob(TempBlob)` to read JSON as text

<details>
<summary>Solution</summary>

```al
TempBlob := SendContext.GetTempBlob();
JsonContent := ConnectorRequests.ReadJsonFromBlob(TempBlob);
```
</details>

#### Task 2.B: Set the API Endpoint

Set the API endpoint to call the `enqueue` endpoint.

**Location**: Around line 49

**Instructions**:
1. Find the comment `// TODO: Set APIEndpoint text variable for request to 'enqueue' endpoint`
2. Combine the base URL from `ConnectorSetup."API Base URL"` with `enqueue`

**Hint**: Use string concatenation

<details>
<summary>Solution</summary>

```al
APIEndpoint := ConnectorSetup."API Base URL" + 'enqueue';
```
</details>

#### Task 2.C: Send the HTTP Request

Send the HTTP request and handle the response.

**Location**: Around line 57

**Instructions**:
1. Find the comment `// TODO: Send the HTTP request and handle the response using HttpClient`
2. Use `HttpClient.Send()` to send the request

**Hint**: The method takes HttpRequest and returns HttpResponse

<details>
<summary>Solution</summary>

```al
HttpClient.Send(HttpRequest, HttpResponse);
```
</details>

### Testing Exercise 2

Build and publish your extension, then continue to the next section for testing.

---

## Testing: Send a Document from Business Central

Now that you've implemented export and send functionality, let's test the complete outbound flow:

1. Open Business Central
2. Search for **Customers** and open the customer you configured
3. Verify the **Document Sending Profile** is set correctly
4. Create a new **Sales Invoice** for this customer
5. Add at least one line item
6. Click **Post and Send**
7. Confirm the posting
8. The E-Document should be automatically created and sent
9. Go to **Posted Sales Invoices** and find your invoice
10. Click **E-Document** → **Open E-Document**
11. Verify the status is **Sent** (or similar)
12. Check the **E-Document Log** for details

**Troubleshooting**:
- If the document doesn't send automatically, check the workflow is enabled
- Verify the customer has the correct Document Sending Profile
- Check the E-Document Service is properly configured
- Review the E-Document Log for error messages

---

## Exercise 3: Receive Documents (15 minutes)

**Objective**: Implement the ability to receive documents from the Connector API.

### Files to Edit
- `ConnectorIntegration.Codeunit.al`

### Tasks

#### Task 3.A1: Set the Peek Endpoint

In the `ReceiveDocuments` procedure, set the API endpoint to call the `peek` endpoint.

**Location**: Around line 95

**Instructions**:
1. Find the comment `// TODO: Set APIEndpoint text variable to 'peek' endpoint`
2. Combine the base URL with `peek`

<details>
<summary>Solution</summary>

```al
APIEndpoint := ConnectorSetup."API Base URL" + 'peek';
```
</details>

#### Task 3.A2: Send the Peek Request

Send the HTTP request to peek at available documents.

**Location**: Around line 105

**Instructions**:
1. Find the comment `// TODO: Send the HTTP request and handle the response using HttpClient`
2. Use `HttpClient.Send()` to send the request

<details>
<summary>Solution</summary>

```al
HttpClient.Send(HttpRequest, HttpResponse);
```
</details>

#### Task 3.A3: Add Documents to Metadata List

Add each document to the DocumentsMetadata list for later processing.

**Location**: Around line 121

**Instructions**:
1. Find the comment `// TODO: Add TempBlob to DocumentsMetadata so we can process it later in DownloadDocument`
2. Use `DocumentsMetadata.Add()` to add the TempBlob

<details>
<summary>Solution</summary>

```al
DocumentsMetadata.Add(TempBlob);
```
</details>

#### Task 3.B1: Set the Dequeue Endpoint

In the `DownloadDocument` procedure, set the API endpoint to call the `dequeue` endpoint.

**Location**: Around line 153

**Instructions**:
1. Find the comment `// TODO: Set APIEndpoint text variable to 'dequeue' endpoint`
2. Combine the base URL with `dequeue`

<details>
<summary>Solution</summary>

```al
APIEndpoint := ConnectorSetup."API Base URL" + 'dequeue';
```
</details>

#### Task 3.B2: Send the Dequeue Request

Send the HTTP request to download a document.

**Location**: Around line 160

**Instructions**:
1. Find the comment `// TODO: Send the HTTP request and handle the response using HttpClient`
2. Use `HttpClient.Send()` to send the request

<details>
<summary>Solution</summary>

```al
HttpClient.Send(HttpRequest, HttpResponse);
```
</details>

#### Task 3.B3: Write Document to Blob

Write the received document JSON to the TempBlob.

**Location**: Around line 172

**Instructions**:
1. Find the comment `// TODO: Write DocumentJson to TempBlob`
2. Use `ConnectorRequests.WriteTextToBlob()` to write the JSON text to the blob

<details>
<summary>Solution</summary>

```al
ConnectorRequests.WriteTextToBlob(DocumentJson, TempBlob);
```
</details>

### Testing Exercise 3

Build and publish your extension. Then test receiving documents:

1. In Business Central, search for **E-Document Services**
2. Open your Connector service
3. Click **Receive Documents**
4. The system will fetch available documents from the queue
5. Search for **E-Documents**
6. You should see new incoming E-Documents with status **In Progress** or **Imported**

---

## Exercise 4: Import Documents (10 minutes)

**Objective**: Parse incoming JSON documents and extract field values for Purchase Invoices.

### Files to Edit
- `SimpleJsonFormat.Codeunit.al`

### Tasks

#### Task 4.A: Extract Basic Document Information

In the `GetBasicInfoFromReceivedDocument` procedure, extract vendor information and total amount from the JSON.

**Location**: Around lines 147-156

**Instructions**:
1. Find the TODO comments for extracting vendor number, vendor name, and total amount
2. Replace the empty strings `''` in `SelectJsonToken` with the correct JSON field names:
   - For vendor number: `'vendorNo'`
   - For vendor name: `'vendorName'`
   - For total amount: `'totalAmount'`

**Hint**: Look at the examples above to see the pattern

<details>
<summary>Solution</summary>

```al
// Extract vendor number
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'vendorNo', JsonToken) then
    EDocument."Bill-to/Pay-to No." := SimpleJsonHelper.GetJsonTokenValue(JsonToken);

// Extract vendor name
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'vendorName', JsonToken) then
    EDocument."Bill-to/Pay-to Name" := SimpleJsonHelper.GetJsonTokenValue(JsonToken);

// Extract total amount
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'totalAmount', JsonToken) then
    EDocument."Amount Incl. VAT" := SimpleJsonHelper.GetJsonTokenDecimal(JsonToken);
```
</details>

#### Task 4.B: Extract Line Information

In the `GetCompleteInfoFromReceivedDocument` procedure, extract line details from the JSON.

**Location**: Around lines 218-227

**Instructions**:
1. Find the TODO comments for extracting description, quantity, and lineAmount
2. Replace the empty strings `''` with the correct JSON field names:
   - For description: `'description'`
   - For quantity: `'quantity'`
   - For line amount: `'lineAmount'`

<details>
<summary>Solution</summary>

```al
// Set description
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'description', JsonToken) then
    PurchaseLine.Description := SimpleJsonHelper.GetJsonTokenValue(JsonToken);

// Set quantity
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'quantity', JsonToken) then
    PurchaseLine.Quantity := SimpleJsonHelper.GetJsonTokenDecimal(JsonToken);

// Set line amount
if SimpleJsonHelper.SelectJsonToken(JsonObject, 'lineAmount', JsonToken) then
    PurchaseLine.Amount := SimpleJsonHelper.GetJsonTokenDecimal(JsonToken);
```
</details>

### Testing Exercise 4

Build and publish your extension. Then test importing:

1. Search for **E-Documents** in Business Central
2. Open an incoming E-Document that was received
3. If the status is not yet **Imported**, click **Create Document**
4. The system will parse the JSON and create a Purchase Invoice
5. Verify the Purchase Invoice was created correctly
6. Check that vendor, dates, amounts, and lines are populated

---

## Testing: Complete Flow

### End-to-End Test

1. **Send a document**:
   - Post a Sales Invoice for a configured customer

2. **Receive the document**:
   - Run **Receive Documents** from E-Document Services
   - Verify the document appears in E-Documents list

3. **Import the document**:
   - Open the received E-Document
   - Click **Create Document**
   - Verify a Purchase Invoice is created with correct data

4. **Review logs**:
   - Check the E-Document Log for each step
   - Review any errors or warnings

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Documents not sending | Check workflow is enabled and customer has correct sending profile |
| Connection errors | Verify API Base URL and Service Key in Connector setup |
| Documents not received | Ensure documents are in the queue (check API with `/peek`) |
| Import fails | Check JSON format matches expected structure |
| Vendor not found | Ensure vendor number exists in Business Central |

---

## Congratulations!

You've successfully completed the E-Document Integration Workshop! You now know how to:

✅ Export documents to JSON format  
✅ Send documents via REST API  
✅ Receive documents from external services  
✅ Import and create purchase documents from JSON  

### Next Steps

- Explore additional document types (Orders, Credit Memos)
- Add error handling and validation
- Implement batch processing
- Add custom fields to your JSON format
- Integrate with other external services

### Resources

- [E-Documents Overview - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/finance-edocuments-overview)
- [Set up E-Documents - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/finance-how-setup-edocuments)
- [API Reference](./API_REFERENCE.md) - Connector API documentation
- [Business Central AL Developer Guide](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-dev-overview)

---

**Workshop Version**: 1.0  
**Last Updated**: November 2025
