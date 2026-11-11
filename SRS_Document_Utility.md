# Software Requirements Specification (SRS)
## Project: Utility Management System
### Prepared by: Jasika Noor (Student ID: 22CSE002)

---

### 1. Introduction

#### 1.1 Purpose
The purpose of this document is to define the Software Requirements Specification (SRS) for the **Utility Management System**. This document outlines both functional and non-functional requirements, system architecture, database schema, user roles, external interface specifications, and data flow models. This specification serves as the official reference for software developers, database administrators, system architects, utility company operators, and project stakeholders.

#### 1.2 Scope
**Utility Management System** is an enterprise-grade, web-based utility administration and customer service portal designed to digitize and automate multi-utility management (Electricity, Water, and Gas). The application covers:
- **Multi-Role Authentication & Access Control** for Administrators, Utility Staff/Employees, and Consumers/Customers.
- **Customer Directory & Profile Management** linked to meter accounts and addresses.
- **Smart Meter Registration & Consumption Tracking** (Electricity, Water, Gas meter inventory and monthly reading logs).
- **Automated Billing Engine & Tariff Rate Processing** calculating bill amounts based on consumption delta (`currReading - prevReading`).
- **Automated Email Notification System** providing instant invoice notifications, due-date reminders, and payment receipts.
- **Digital Payment Processing** supporting multi-channel payment records (bKash, Nagad, Rocket, Bank Transfer, Credit Card).
- **Customer Support Ticketing & Complaint Management** with live comment threads and status pipelines.
- **Field Maintenance Service Request System** for technical repairs, meter installation, and field technician assignment.
- **Geographic Information System (GIS) Mapping** for spatial customer/meter distribution, substation tracking, and outage zone visualization.
- **Analytics & Revenue Reporting** generating monthly utility consumption charts, financial collection trends, and PDF export capabilities.

#### 1.3 Definitions, Acronyms, and Abbreviations

| Term / Acronym | Meaning & Context |
| :--- | :--- |
| **SRS** | Software Requirements Specification |
| **UMS / utilis-app** | Utility Management System Platform |
| **FR / NFR** | Functional Requirement / Non-Functional Requirement |
| **GIS** | Geographic Information System (Spatial Map Visualization) |
| **SPA** | Single Page Application (Client-side dynamic UI) |
| **REST** | Representational State Transfer (HTTP API Architecture) |
| **CRUD** | Create, Read, Update, Delete database operations |
| **DFD** | Data Flow Diagram (Level 1 Process Architecture) |
| **ERD** | Entity Relationship Diagram (Database Schema Model) |
| **PK / FK** | Primary Key / Foreign Key in relational database design |

#### 1.4 References
1. IEEE Std 830-1998: *IEEE Recommended Practice for Software Requirements Specifications*.
2. IEEE Std 29148-2018: *Systems and software engineering — Life cycle processes — Requirements engineering*.
3. Sommerville, Ian. *Software Engineering* (10th Edition), Addison-Wesley.
4. Express.js Documentation: [https://expressjs.com/](https://expressjs.com/)
5. MySQL 8.0 Reference Manual: [https://dev.mysql.com/doc/refman/8.0/en/](https://dev.mysql.com/doc/refman/8.0/en/)
6. Leaflet.js Interactive Maps: [https://leafletjs.com/](https://leafletjs.com/)

#### 1.5 Overview
This document is organized into seven core sections:
- **Section 2**: Overall Description (Product Perspective, User Classes, Operating Environment, Constraints).
- **Section 3**: System Features & Functional Requirements (FR-01 to FR-42 across 10 core modules).
- **Section 4**: External Interface Requirements (UI, Hardware, Software, Communication).
- **Section 5**: Non-Functional Requirements (Performance, Security, Reliability, Usability, Portability).
- **Section 6**: Other Requirements (Regulatory Compliance, Tariff Policies & Data Privacy).
- **Section 7**: Appendices (Data Flow Diagram Level 1 & Complete ERD Database Schema).

---

### 2. Overall Description

#### 2.1 Product Perspective
`utilis-app` is a self-contained full-stack web application designed with a decoupled architecture. The backend service layer operates using Node.js and Express.js interacting with a MySQL relational database (`utilis_db`). The frontend is a modern, responsive Single Page Application (SPA) communicating asynchronously via REST API endpoints.

#### 2.2 Product Functions
- **User Authentication & Session Handling**: Secure login, self-registration for customers, role-based session storage, and logout.
- **Customer Master Directory**: Centralized management of consumer personal details, contact info, utility service locations, and linked meters.
- **Smart Meter Management**: Meter inventory tracking, meter serial numbers, utility type classification (Electricity/Water/Gas), status flags, and customer assignments.
- **Meter Reading & Consumption Calculation**: Monthly meter reading logging, automatic delta consumption computation (`currReading - prevReading`).
- **Tariff Rate & Automated Billing Engine**: Tiered tariff calculations, invoice generation, due date enforcement, and billing status tracking (Paid/Unpaid/Overdue).
- **Email & Notification Engine**: Automated Nodemailer integration sending bill generation notices, urgent unpaid bill reminders, and resolution alerts.
- **Online Payment Settlement**: Recording customer payments with payment method tracking (bKash, Nagad, Bank), transaction IDs, and receipt downloads.
- **Complaint & Support Ticket System**: Customer submission of service issues (faulty meter, wrong billing, power outage) with admin assignment and status updates.
- **Field Maintenance Dispatch**: Scheduling emergency repair and maintenance jobs, assigning field technicians, and updating job status.
- **GIS Spatial Outage & Meter Map**: Interactive geographical map placing customer meters, transformer nodes, and color-coded fault markers.
- **Reports & Financial Dashboard**: Revenue graphs, utility breakdown analytics, billing summary cards, and PDF invoice printing.

#### 2.3 User Classes and Characteristics

| User Role | Target Audience | Key Responsibilities & Permissions |
| :--- | :--- | :--- |
| **System Administrator (`admin`)** | Utility Executive & System Manager | Full access to customer records, meter management, billing generation, financial reports, GIS map overview, technician assignment, and system settings. |
| **Utility Field Staff (`employee`)** | Field Engineers & Meter Readers | Logs monthly meter readings, updates maintenance ticket statuses, resolves technical complaints, and inspects GIS meter locations. |
| **Utility Customer (`customer`)** | Residential & Commercial Consumers | Views current & historical utility bills, submits meter readings, pays bills online, tracks payment history, files complaints/maintenance requests, and updates profile. |

#### 2.4 Operating Environment
- **Server Environment**: Node.js runtime (v18.0+), Express.js framework (port 5000), Nodemailer service.
- **Database Environment**: MySQL Server (v8.0+), relational schema `utilis_db`.
- **Client Environment**: Web browser execution (Chrome v100+, Firefox v100+, Edge, Safari), HTTP static server (port 8080).
- **Libraries & Extensions**: FontAwesome icons, Chart.js analytics engine, Leaflet.js GIS spatial engine.

#### 2.5 Design and Implementation Constraints
- **Dual-Port Architecture**: Backend API executes on `http://localhost:5000` while static SPA assets serve on `http://localhost:8080`.
- **Relational Integrity**: Foreign key constraints strictly enforced across 9 SQL tables (`users`, `customers`, `meters`, `meter_readings`, `bills`, `payments`, `complaints`, `notifications`, `maintenance`).
- **Calculated Metric Boundaries**: Consumption cannot be negative (`currReading >= prevReading`). Tariff rates must reflect positive double-precision numbers.

#### 2.6 User Documentation
Complete installation and operational guides are documented in `README.md` within the root project directory.

#### 2.7 Assumptions and Dependencies
- Users access the system via standard web browsers over HTTP/HTTPS connections.
- MySQL database server is running locally or remotely with appropriate database user permissions.
- SMTP email server credentials are provided in `.env` for email reminder dispatch.

---

### 3. System Features (Functional Requirements)

#### 3.1 Module 1: User Authentication & Profile Management
| ID | Requirement Statement |
| :--- | :--- |
| **FR-01** | The system shall allow users to log in using a valid username/email and password. |
| **FR-02** | The system shall maintain session state (`sessionStorage`) with role-based permissions (`admin`, `employee`, `customer`). |
| **FR-03** | The system shall allow new customers to self-register with full name, username, email, password, phone, address, and optional meter serial number. |
| **FR-04** | The system shall allow logged-in customers to view and update their personal profile information. |
| **FR-05** | The system shall provide a secure log-out capability that clears session state and redirects to the public landing portal. |

#### 3.2 Module 2: Customer Account Management
| ID | Requirement Statement |
| :--- | :--- |
| **FR-06** | The system shall maintain a customer registry linking customer profile details to user authentication accounts. |
| **FR-07** | The system shall allow administrators to view, add, update, and search customer records by name, email, or phone. |
| **FR-08** | The system shall allow administrators to activate or deactivate customer accounts. |
| **FR-09** | The system shall allow administrators to link or re-assign utility meter units to specific customer accounts. |

#### 3.3 Module 3: Smart Meter & Reading Tracking
| ID | Requirement Statement |
| :--- | :--- |
| **FR-10** | The system shall maintain a master meter inventory recording meter ID, meter serial number, utility type (Electricity, Water, Gas), status, and installation date. |
| **FR-11** | The system shall allow administrators and field staff to register new utility meters into the system. |
| **FR-12** | The system shall record monthly meter readings containing meter ID, billing month, and units consumed. |
| **FR-13** | The system shall display meter status indicators (`active`, `faulty`, `inactive`). |
| **FR-14** | The system shall allow filtering meter records by utility category (Electricity, Water, Gas) and assignment status. |

#### 3.4 Module 4: Consumption Billing & Tariff Calculation
| ID | Requirement Statement |
| :--- | :--- |
| **FR-15** | The system shall generate monthly utility bills for customers based on meter consumption data. |
| **FR-16** | The system shall automatically compute utility consumption delta: `consumption = currReading - prevReading`. |
| **FR-17** | The system shall calculate billing amounts by multiplying unit consumption by applicable utility tariff rates (`amount = consumption * tariffRate`). |
| **FR-18** | The system shall enforce due dates, billing months, and billing years for every generated invoice record. |
| **FR-19** | The system shall allow administrators to manually trigger single or batch bill generation. |
| **FR-20** | The system shall mark bill statuses dynamically as `unpaid`, `paid`, or `overdue`. |

#### 3.5 Module 5: Automated Email Notification & Reminder System
| ID | Requirement Statement |
| :--- | :--- |
| **FR-21** | The system shall automatically dispatch an email notification to the customer upon bill generation. |
| **FR-22** | The system shall provide an administrative feature to trigger urgent email reminders (`/api/send-bill-reminder`) for unpaid utility bills. |
| **FR-23** | The system shall render HTML-formatted email reminder templates containing invoice ID, utility type, due date, and amount due. |
| **FR-24** | The system shall store in-app user notifications in the database with unread/read state tracking. |

#### 3.6 Module 6: Payment Processing & Financial Accounting
| ID | Requirement Statement |
| :--- | :--- |
| **FR-25** | The system shall allow customers to submit bill payments choosing digital channels (bKash, Nagad, Rocket, Bank Transfer, Credit Card). |
| **FR-26** | The system shall validate payment inputs and record unique transaction reference IDs (`transactionId`). |
| **FR-27** | The system shall automatically update bill status from `unpaid` to `paid` upon successful payment verification. |
| **FR-28** | The system shall generate printable digital payment receipts for completed utility transactions. |

#### 3.7 Module 7: Complaint Management & Support Ticketing
| ID | Requirement Statement |
| :--- | :--- |
| **FR-29** | The system shall allow customers to submit support complaints selecting subject, description, and utility category. |
| **FR-30** | The system shall track complaint status through a defined workflow pipeline (`Pending`, `In Progress`, `Resolved`). |
| **FR-31** | The system shall allow administrators and employees to assign complaints to technical staff members. |
| **FR-32** | The system shall support interactive JSON comment threads attached to each complaint ticket for communication between customers and staff. |

#### 3.8 Module 8: Field Maintenance & Technical Operations
| ID | Requirement Statement |
| :--- | :--- |
| **FR-33** | The system shall allow customers and staff to lodge maintenance requests (e.g., Meter Inspection, Leak Repair, Line Maintenance). |
| **FR-34** | The system shall record maintenance request type, description, customer link, assigned technician, and creation timestamp. |
| **FR-35** | The system shall allow field staff to update maintenance task progress and log resolution notes. |
| **FR-36** | The system shall display active maintenance request metrics on administrative dashboards. |

#### 3.9 Module 9: Geographic Information System (GIS) & Spatial Mapping
| ID | Requirement Statement |
| :--- | :--- |
| **FR-37** | The system shall integrate Leaflet GIS interactive map visualization displaying spatial distribution of customer meters. |
| **FR-38** | The system shall plot custom map markers indicating customer locations, meter health status, and utility types. |
| **FR-39** | The system shall highlight active utility fault areas and substation coverage zones on the GIS map canvas. |

#### 3.10 Module 10: Reports & Executive Analytics Engine
| ID | Requirement Statement |
| :--- | :--- |
| **FR-40** | The system shall render analytical summary charts (Chart.js) illustrating monthly consumption trends and revenue collection figures. |
| **FR-41** | The system shall generate summary statistics for total registered customers, active meters, total billed revenue, and unpaid balances. |
| **FR-42** | The system shall allow exporting billing summaries and customer ledgers to printable format / PDF. |

---

### 4. External Interface Requirements

#### 4.1 User Interfaces
The user interface is constructed as a modern, dark-mode/light-mode responsive Single Page Application (SPA) utilizing HTML5, CSS3, and JavaScript ES6 modules. Key UI design highlights:
- **Navigation Sidebar**: Role-specific dynamic navigation rendering appropriate workspace menus.
- **KPI Summary Cards**: Overview counters displaying total customers, active meters, revenue, and open tickets.
- **Data Tables**: Interactive grids featuring real-time filtering, search inputs, pagination, and action buttons.
- **Modal Dialogs**: Styled overlays for customer registration, meter addition, bill generation, payment processing, and complaint creation.
- **GIS Canvas**: Embedded interactive map container supporting zoom, tile layering, and popup tooltips.

#### 4.2 Hardware Interfaces
- **Server Hardware**: x86-64 server or virtual machine (Minimum: 2 Core CPU, 4 GB RAM, 20 GB Storage).
- **Client Hardware**: Desktop computers, laptops, tablets, or mobile smartphones with standard screen resolution (1024x768 and above recommended).

#### 4.3 Software Interfaces
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS.
- **Node.js Environment**: Version 18.0.0 or higher.
- **Database Engine**: MySQL Server 8.0+ running engine `InnoDB` with UTF-8 character encoding.
- **Web Server**: Express.js HTTP framework and static web server.

#### 4.4 Communication Interfaces
- **Protocol**: HTTP/1.1 or HTTPS for API and static resource delivery.
- **API Architecture**: RESTful API endpoints exchanging JSON data payloads (`Content-Type: application/json`).
- **CORS Configuration**: Cross-Origin Resource Sharing enabled on backend port 5000 to accept requests from frontend origin port 8080.
- **Email Protocol**: SMTP (Simple Mail Transfer Protocol) for outbound email reminder dispatch via Nodemailer.

---

### 5. Non-Functional Requirements

| ID | Category | Specification |
| :--- | :--- | :--- |
| **NFR-01** | Performance | API response time shall remain under 1.5 seconds for database queries and under 3.0 seconds for email dispatches. |
| **NFR-02** | Security | User passwords shall be stored securely. Session state must be bounded by browser session boundaries with role validation on API routes. |
| **NFR-03** | Reliability | The database layer shall use InnoDB foreign keys with cascading delete/update constraints to maintain data integrity with 99.9% consistency. |
| **NFR-04** | Usability | The UI shall provide clear visual status badges, actionable confirmation prompts, and immediate toast feedback for user actions. |
| **NFR-05** | Portability | The web interface shall execute across modern standard web browsers (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari) without plugin requirements. |

---

### 6. Other Requirements

#### 6.1 Regulatory Compliance & Tariff Policies
The system enforces standard utility tariff structures approved by national utility regulatory commissions. Tariff rates are applied uniformly per unit based on utility type (Electricity per kWh, Water per Litre/Unit, Gas per Unit/Cubic Meter).

#### 6.2 Data Privacy & Billing Audit Trail
All financial transactions, payments, and bill updates are timestamped and linked to specific customer and invoice IDs, establishing an immutable audit trail for accounting and auditing purposes.

---

### 7. Appendices

#### 7.1 Appendix A: Data Flow Diagram (DFD Level 1)

1. **Customer** → `[Login / Registration]` → User Authentication Process → `[Store Session]` → `users` & `customers` DB
2. **Field Staff / Employee** → `[Meter Reading Data]` → Reading Log Process → `[Store Consumption Delta]` → `meter_readings` DB
3. **Billing Engine** → `[Fetch Readings & Tariff]` → Billing Generation Process → `[Compute Amount]` → `bills` DB → `[Send Email]` → **Customer**
4. **Customer** → `[Payment Details & Transaction ID]` → Payment Gateway Process → `[Verify & Update Status]` → `payments` & `bills` DB
5. **Customer** → `[Complaint / Maintenance Request]` → Support Ticket Process → `[Assign Staff & Log Status]` → `complaints` & `maintenance` DB
6. **Administrator** → `[Request GIS & Analytics]` → Reporting Engine → `[Aggregate Metrics & Map Data]` → `gis` & `reports` Dashboard

#### 7.2 Appendix B: Entity Relationship Diagram (ERD) & Database Schema

| Database Table | Attributes & Keys | Description |
| :--- | :--- | :--- |
| **`users`** | `id` (PK), `name`, `username` (UQ), `email`, `password`, `role`, `status` | Stores authentication credentials and user role (`admin`, `employee`, `customer`). |
| **`customers`** | `customer_id` (PK), `user_id` (FK -> users.id), `phone`, `address` | Stores customer profile details linked to a user login account. |
| **`meters`** | `meter_id` (PK), `customer_id` (FK -> customers.customer_id), `meter_number` (UQ), `utilityType`, `status`, `installDate` | Stores utility meter records (Electricity, Water, Gas) and customer ownership. |
| **`meter_readings`** | `reading_id` (PK), `meter_id` (FK -> meters.meter_id), `month`, `unit_consumed` | Tracks monthly consumption units logged per meter. |
| **`bills`** | `bill_id` (PK), `customer_id` (FK -> customers.customer_id), `amount`, `due_date`, `status`, `billingMonth`, `billingYear`, `meterId` (FK -> meters.meter_id), `prevReading`, `currReading`, `consumption`, `tariffRate`, `createdAt`, `paymentDate` | Stores calculated utility bills, reading deltas, tariff rates, due dates, and statuses. |
| **`payments`** | `payment_id` (PK), `bill_id` (FK -> bills.bill_id), `amount`, `payment_date`, `method`, `transactionId`, `status` | Records payment transactions, methods (bKash, Nagad, Bank), and transaction IDs. |
| **`complaints`** | `complaint_id` (PK), `customer_id` (FK -> customers.customer_id), `subject`, `description`, `status`, `assignedTo`, `createdAt`, `comments` (JSON) | Manages customer support tickets, status pipeline, assigned staff, and comment logs. |
| **`notifications`** | `id` (PK), `userId` (FK -> users.id), `message`, `type`, `date`, `isRead` | Stores system notifications and unread/read indicators for users. |
| **`maintenance`** | `maintenance_id` (PK), `customer_id` (FK -> customers.customer_id), `request_type`, `description`, `status`, `assigned_to`, `createdAt`, `comments` (JSON) | Manages technical field maintenance requests, assigned technicians, and status tracking. |
